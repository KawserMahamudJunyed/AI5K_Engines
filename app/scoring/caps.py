from app.schemas.claim import Claim

__all__ = ["apply_hard_caps"]


def apply_hard_caps(
    readiness_score: float,
    dimension_scores: dict[str, float],
    claims: list[Claim],
) -> tuple[float, dict[str, float]]:
    """
    If ALL claims are T8, cap readiness and evidence_quality at 30.
    
    Args:
        readiness_score: The un-capped readiness score.
        dimension_scores: The un-capped dimension scores dictionary.
        claims: A list of claims to evaluate.
        
    Returns:
        A tuple of (capped_readiness_score, capped_dimension_scores).
    """
    if not claims:
        return readiness_score, dimension_scores

    all_t8 = all(getattr(c, "evidence_tier", "T8") == "T8" for c in claims)
    
    if all_t8:
        capped_dims = dict(dimension_scores)
        capped_dims["evidence_quality"] = min(capped_dims.get("evidence_quality", 0.0), 30.0)
        capped_readiness = min(readiness_score, 30.0)
        return capped_readiness, capped_dims
        
    return readiness_score, dimension_scores