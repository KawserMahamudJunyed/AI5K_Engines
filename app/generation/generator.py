from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Protocol
from app.schemas.claim import Claim
from app.schemas.benchmark import Benchmark

__all__ = ["DraftAsset", "AssetGenerator", "GeneratorLLM"]

_PUBLISHABLE_TIERS = frozenset({"T1", "T2", "T3", "T4"})

@dataclass
class DraftAsset:
    title: str
    overview: str
    case_studies: list[dict[str, str]]
    skill_highlights: list[str]
    gap_actions: list[dict[str, Any]] = field(default_factory=list)
    claims_used: list[Claim] = field(default_factory=list)
    source_tiers_used: set[str] = field(default_factory=set)

class GeneratorLLM(Protocol):
    async def generate_title(self, claims: list[Claim], benchmark: Benchmark) -> str: ...
    async def generate_overview(self, claims: list[Claim], benchmark: Benchmark) -> str: ...
    async def generate_case_studies(self, claims: list[Claim], benchmark: Benchmark) -> list[dict[str, str]]: ...
    async def generate_gap_actions(self, claims: list[Claim], benchmark: Benchmark) -> list[dict[str, Any]]: ...

class AssetGenerator:
    def __init__(self, llm: GeneratorLLM) -> None:
        self._llm = llm

    async def generate(self, claims: list[Claim], benchmark: Benchmark) -> DraftAsset:
        # Filter claims: overview STRICTLY restricted to T1-T4 claims
        publishable = [c for c in claims if c.evidence_tier in _PUBLISHABLE_TIERS and c.publishable]
        all_publishable = [c for c in claims if c.publishable]

        if publishable:
            overview = await self._llm.generate_overview(publishable, benchmark)
        else:
            overview = ""  # Cannot generate overview without T1-T4 evidence

        title = await self._llm.generate_title(publishable or all_publishable, benchmark)
        case_studies = await self._llm.generate_case_studies(publishable, benchmark) if publishable else []
        gap_actions = await self._llm.generate_gap_actions(claims, benchmark)

        skill_highlights = list({sid for c in all_publishable for sid in c.skill_ids})
        tiers_used = {c.evidence_tier for c in publishable}

        return DraftAsset(
            title=title,
            overview=overview,
            case_studies=case_studies,
            skill_highlights=sorted(skill_highlights),
            gap_actions=gap_actions,
            claims_used=publishable,
            source_tiers_used=tiers_used,
        )