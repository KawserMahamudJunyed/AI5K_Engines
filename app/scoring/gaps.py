from dataclasses import dataclass
from app.schemas.claim import Claim
from app.schemas.benchmark import Benchmark
from app.scoring.score_dimensions import WEIGHTS

__all__ = ["GapItem", "rank_gaps", "extract_blocking_items"]


@dataclass
class GapItem:
    """Represents a score dimension gap to be addressed."""
    dimension: str
    current_score: float
    target_score: float
    weight: float
    gain: float
    effort_hours: float
    efficacy: float
    priority: float
    blocking: bool
    blocking_reason: str | None


def rank_gaps(
    dimension_scores: dict[str, float],
    benchmark: Benchmark,
    claims: list[Claim],
) -> list[GapItem]:
    """
    Rank gaps across dimensions based on potential gain and required effort.
    
    Args:
        dimension_scores: Current scores for each dimension.
        benchmark: Contextual benchmark targets.
        claims: Processed claims for checking blockages.
        
    Returns:
        A prioritized list of GapItem objects.
    """
    gaps: list[GapItem] = []
    
    # Sensible defaults for effort and efficacy
    effort_map = {
        "positioning": 2.0,
        "evidence_quality": 5.0,
        "keyword_coverage": 1.5,
        "portfolio_quality": 8.0,
        "completeness": 3.0,
        "conversion": 2.5,
        "pricing_strategy": 0.5,
    }
    
    efficacy_map = {
        "positioning": 0.8,
        "evidence_quality": 0.9,
        "keyword_coverage": 0.95,
        "portfolio_quality": 0.85,
        "completeness": 0.7,
        "conversion": 0.8,
        "pricing_strategy": 1.0,
    }
    
    all_t8 = bool(claims) and all(getattr(c, "evidence_tier", "T8") == "T8" for c in claims)
    
    for dim, score in dimension_scores.items():
        weight = getattr(WEIGHTS, dim, 0.1)
        target = 100.0
        
        # Calculate gain
        efficacy = efficacy_map.get(dim, 0.8)
        effort = max(effort_map.get(dim, 2.0), 1.0)
        gain = weight * (target - score) * efficacy
        
        priority = gain / effort
        
        blocking = False
        blocking_reason = None
        
        if dim == "evidence_quality" and all_t8:
            blocking = True
            blocking_reason = "UNPROVEN_CLAIM: Missing verifiable high-tier evidence."
            
        if dim == "portfolio_quality" and score < 20.0:
            blocking = True
            blocking_reason = "LACKING_PORTFOLIO: Extremely low portfolio volume."
            
        item = GapItem(
            dimension=dim,
            current_score=score,
            target_score=target,
            weight=weight,
            gain=gain,
            effort_hours=effort,
            efficacy=efficacy,
            priority=priority,
            blocking=blocking,
            blocking_reason=blocking_reason,
        )
        gaps.append(item)
        
    # Sort by priority descending
    gaps.sort(key=lambda g: g.priority, reverse=True)
    return gaps


def extract_blocking_items(gaps: list[GapItem]) -> list[str]:
    """
    Extract blocking reason strings from a list of gaps.
    
    Args:
        gaps: List of prioritized GapItems.
        
    Returns:
        List of active blocking reasons.
    """
    return [g.blocking_reason for g in gaps if g.blocking and g.blocking_reason is not None]