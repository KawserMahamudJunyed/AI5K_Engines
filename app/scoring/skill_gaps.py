from dataclasses import dataclass
from app.schemas.claim import Claim
from app.schemas.benchmark import Benchmark

__all__ = ["SkillGap", "find_skill_gaps"]

# Import weights without cyclic dependency if possible, or define standard.
_TIER_WEIGHTS: dict[str, float] = {
    "T1": 1.0, "T2": 0.9, "T3": 0.8, "T4": 0.75,
    "T5": 0.5, "T7": 0.3, "T8": 0.1,
}

@dataclass
class SkillGap:
    """Identifies a missing required term and possible source tier if found."""
    term: str
    found: bool
    source_tier: str | None  # best tier if found
    suggestion: str


def find_skill_gaps(claims: list[Claim], benchmark: Benchmark) -> list[SkillGap]:
    """
    Report which benchmark required_terms are missing from claims.
    
    Args:
        claims: Processed evidence claims.
        benchmark: Baseline defining required_terms.
        
    Returns:
        List of missing or found SkillGaps.
    """
    required_terms = getattr(benchmark, "required_terms", []) or []
    if not required_terms:
        return []
        
    gaps: list[SkillGap] = []
    
    for term in required_terms:
        found = False
        best_tier: str | None = None
        best_tier_weight = -1.0
        
        term_lower = term.lower()
        
        for claim in claims:
            claim_text = (getattr(claim, "claim_text", "") or "").lower()
            skill_ids = [s.lower() for s in getattr(claim, "skill_ids", []) or []]
            
            if term_lower in claim_text or term_lower in skill_ids:
                found = True
                tier = getattr(claim, "evidence_tier", "T8") or "T8"
                weight = _TIER_WEIGHTS.get(tier, 0.0)
                
                if weight > best_tier_weight:
                    best_tier_weight = weight
                    best_tier = tier
                    
        if found:
            gaps.append(SkillGap(
                term=term,
                found=True,
                source_tier=best_tier,
                suggestion=""
            ))
        else:
            gaps.append(SkillGap(
                term=term,
                found=False,
                source_tier=None,
                suggestion=f"Add evidence for '{term}'"
            ))
            
    return gaps