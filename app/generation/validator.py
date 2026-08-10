from __future__ import annotations
import re
import uuid
from dataclasses import dataclass
from app.schemas.claim import Claim, SourceSpan
from app.generation.generator import DraftAsset

__all__ = ["ValidationResult", "validate_asset", "reverify_span"]

_PUBLISHABLE_TIERS = frozenset({"T1", "T2", "T3", "T4"})

# Proof language that MUST be backed by T1-T4 claims
_UNBACKED_PROOF_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"proven\s+(expert|leader|track record|specialist)", re.I),
    re.compile(r"verified\s+(leader|expert|professional|specialist)", re.I),
    re.compile(r"demonstrated\s+(expertise|mastery|excellence)", re.I),
    re.compile(r"award[- ]winning", re.I),
    re.compile(r"industry[- ]leading", re.I),
    re.compile(r"world[- ]class", re.I),
    re.compile(r"best[- ]in[- ]class", re.I),
    re.compile(r"top[- ]rated", re.I),
    re.compile(r"guaranteed\s+(results|quality|delivery)", re.I),
    re.compile(r"unmatched\s+(expertise|skill|quality)", re.I),
]

@dataclass
class ValidationResult:
    validated: bool
    overview_blocked_by_evidence_tier: bool
    issues: list[str]
    reverified_spans: int
    failed_spans: int

def reverify_span(span: SourceSpan, source_text: str) -> bool:
    """Re-check that the span text matches source_text[start_index:end_index]."""
    if span.start_index < 0 or span.end_index > len(source_text) or span.start_index > span.end_index:
        return False
    return source_text[span.start_index:span.end_index] == span.text

def validate_asset(asset: DraftAsset, claims: list[Claim], source_texts: dict[uuid.UUID, str]) -> ValidationResult:
    """Validate DraftAsset for unbacked proof language and reverify source spans."""
    issues = []
    blocked_by_tier = False
    validated = True
    
    # 1. Check if overview contains unbacked proof language
    has_proof_language = any(pattern.search(asset.overview) for pattern in _UNBACKED_PROOF_PATTERNS)
    
    # 2. If proof language found, verify if there are T1-T4 claims backing it
    if has_proof_language:
        has_backing = any(c.evidence_tier in _PUBLISHABLE_TIERS for c in asset.claims_used)
        # 3. If no T1-T4 backing, set overview_blocked_by_evidence_tier=True, validated=False
        if not has_backing:
            blocked_by_tier = True
            validated = False
            issues.append("Overview contains proof language without T1-T4 evidence backing.")
            
    # 4. Re-verify all source_spans in claims_used against source_texts
    reverified = 0
    failed = 0
    
    for claim in asset.claims_used:
        for span in claim.source_spans:
            source_text = source_texts.get(span.source_id, "")
            if reverify_span(span, source_text):
                reverified += 1
            else:
                failed += 1
                validated = False
                issues.append(f"Span verification failed for claim {claim.claim_id}, span source {span.source_id}")
                
    return ValidationResult(
        validated=validated,
        overview_blocked_by_evidence_tier=blocked_by_tier,
        issues=issues,
        reverified_spans=reverified,
        failed_spans=failed,
    )