"""3-pass LLM claim extractor with quote-based span grounding.

Design principle: 'Quote, Don't Compute' — the LLM outputs exact substrings
from the source document, and our code verifies character-level boundaries.
"""
from __future__ import annotations

import asyncio
import difflib
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Protocol

from app.core.config import settings
from app.core.errors import AppError, ErrorCode
from app.schemas.claim import Claim, SourceSpan

__all__ = ["ClaimExtractor", "LLMClient"]

# ── Normalization ────────────────────────────────────────────────
_CURLY_QUOTES = str.maketrans("\u2018\u2019\u201c\u201d", "''\"\"")
_EM_DASH = re.compile(r"[\u2013\u2014]")

_BOILERPLATE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"npx\s+create-\w[\w-]*", re.IGNORECASE),
    re.compile(r"npm\s+(install|run|start|build|test)", re.IGNORECASE),
    re.compile(r"yarn\s+(add|install|start|build)", re.IGNORECASE),
    re.compile(r"pip\s+install", re.IGNORECASE),
    re.compile(r"docker\s+(run|build|compose)", re.IGNORECASE),
    re.compile(r"git\s+(clone|init|checkout|pull)", re.IGNORECASE),
]

_TIER_RANK = {f"T{i}": i for i in range(1, 9)}


def normalize_text(text: str) -> str:
    text = text.translate(_CURLY_QUOTES)
    text = _EM_DASH.sub("-", text)
    return text


def is_boilerplate(text: str) -> bool:
    return any(p.search(text) for p in _BOILERPLATE_PATTERNS)


def vocab_overlap(claim_text: str, quote_text: str) -> float:
    """Return fraction of significant words in claim that appear in quote."""
    stop = {"the", "a", "an", "is", "are", "was", "were", "in", "on", "at",
            "to", "for", "of", "and", "or", "with", "by", "as", "it", "that",
            "this", "from", "be", "has", "had", "have", "i", "my", "we", "our"}

    def significant(t: str) -> set[str]:
        return {w.lower() for w in re.findall(r"\w{3,}", t)} - stop

    claim_words = significant(claim_text)
    quote_words = significant(quote_text)
    if not claim_words:
        return 1.0
    return len(claim_words & quote_words) / len(claim_words)


class LLMClient(Protocol):
    """Protocol for LLM providers."""
    async def extract_claims(
        self, source_text: str, source_type: str, pass_number: int
    ) -> list[dict[str, Any]]:
        """Return list of raw claim dicts with 'claim_text', 'skill_ids', 'evidence_quote', 'observed_date'."""
        ...


class ClaimExtractor:
    def __init__(self, llm: LLMClient, *, max_workers: int | None = None) -> None:
        self._llm = llm
        self._max_workers = max_workers or settings.max_extraction_workers
        self._passes = settings.extraction_passes
        self._similarity_threshold = settings.similarity_threshold
        self._vocab_threshold = settings.vocab_overlap_threshold

    async def extract(
        self,
        source_text: str,
        source_type: str,
        document_id: uuid.UUID,
    ) -> list[Claim]:
        normalized = normalize_text(source_text)
        raw_claims = await self._multi_pass_extract(normalized, source_type)
        grounded = self._ground_claims(raw_claims, normalized, document_id, source_type)
        filtered = [c for c in grounded if not is_boilerplate(c.claim_text)]
        deduped = self._deduplicate(filtered)
        return deduped

    async def _multi_pass_extract(
        self, source_text: str, source_type: str
    ) -> list[dict[str, Any]]:
        tasks = [
            self._llm.extract_claims(source_text, source_type, i + 1)
            for i in range(self._passes)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        merged = []
        for res in results:
            if isinstance(res, Exception):
                continue
            merged.extend(res)
        return merged

    def _ground_claims(
        self,
        raw_claims: list[dict[str, Any]],
        normalized_source: str,
        document_id: uuid.UUID,
        source_type: str,
    ) -> list[Claim]:
        grounded = []
        for raw in raw_claims:
            claim_text = raw.get("claim_text", "")
            evidence_quote = raw.get("evidence_quote", "")
            skill_ids = raw.get("skill_ids", [])
            observed_date = raw.get("observed_date")
            evidence_tier = raw.get("evidence_tier", "T8")

            norm_quote = normalize_text(evidence_quote)

            span = None
            if norm_quote:
                start_idx = normalized_source.find(norm_quote)
                if start_idx != -1:
                    overlap = vocab_overlap(claim_text, norm_quote)
                    if overlap >= self._vocab_threshold:
                        end_idx = start_idx + len(norm_quote)
                        span = SourceSpan(
                            document_id=document_id,
                            start_index=start_idx,
                            end_index=end_idx,
                            source_type=source_type,
                        )

            claim = Claim(
                id=uuid.uuid4(),
                claim_text=claim_text,
                skill_ids=skill_ids,
                source_span=span,
                observed_date=observed_date,
                evidence_tier=evidence_tier,
                created_at=datetime.now(timezone.utc),
            )
            grounded.append(claim)

        return grounded

    def _deduplicate(self, claims: list[Claim]) -> list[Claim]:
        if not claims:
            return []

        unique_claims: list[Claim] = []

        for claim in claims:
            matched = False
            for i, existing in enumerate(unique_claims):
                ratio = difflib.SequenceMatcher(
                    None, claim.claim_text.lower(), existing.claim_text.lower()
                ).ratio()

                if ratio >= self._similarity_threshold:
                    matched = True
                    # Keep the one with highest tier (lowest rank number)
                    t_claim = _TIER_RANK.get(claim.evidence_tier, 8)
                    t_exist = _TIER_RANK.get(existing.evidence_tier, 8)

                    if t_claim < t_exist:
                        unique_claims[i] = claim
                    break

            if not matched:
                unique_claims.append(claim)

        return unique_claims