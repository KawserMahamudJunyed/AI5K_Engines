from __future__ import annotations
from dataclasses import dataclass
from app.schemas.claim import Claim
from app.schemas.benchmark import Benchmark

__all__ = ["score_profile", "DimensionWeights", "WEIGHTS", "SYNONYM_MAP"]


@dataclass(frozen=True)
class DimensionWeights:
    """Weights for various scoring dimensions."""
    positioning: float = 0.22
    evidence_quality: float = 0.22
    keyword_coverage: float = 0.15
    portfolio_quality: float = 0.15
    completeness: float = 0.10
    conversion: float = 0.08
    pricing_strategy: float = 0.08


WEIGHTS = DimensionWeights()

_TIER_WEIGHTS: dict[str, float] = {
    "T1": 1.0, "T2": 0.9, "T3": 0.8, "T4": 0.75,
    "T5": 0.5, "T7": 0.3, "T8": 0.1,
}

SYNONYM_MAP: dict[str, list[str]] = {
    "ml": ["machine learning", "deep learning"],
    "js": ["javascript"],
    "react": ["reactjs", "react.js"],
    "aws": ["amazon web services"],
    "nlp": ["natural language processing"],
    "ai": ["artificial intelligence"],
    "cv": ["computer vision"],
    "gcp": ["google cloud platform"],
    "k8s": ["kubernetes"],
    "ts": ["typescript"],
    "node": ["node.js", "nodejs"],
    "vue": ["vuejs", "vue.js"],
    "postgres": ["postgresql"],
}


def _score_positioning(claims: list[Claim], benchmark: Benchmark) -> float:
    """Score 0-100 based on niche keyword density in high-tier claims."""
    if not claims:
        return 0.0

    total_score = 0.0
    required_terms = getattr(benchmark, "required_terms", []) or []
    if not required_terms:
        return 100.0

    for claim in claims:
        text = (getattr(claim, "claim_text", "") or "").lower()
        tier = getattr(claim, "evidence_tier", "T8") or "T8"
        weight = 2.0 if tier in {"T1", "T2", "T3", "T4"} else 1.0
        
        matches = sum(1 for term in required_terms if term.lower() in text)
        total_score += matches * weight
    
    score = (total_score / (len(claims) * max(1, len(required_terms)))) * 100.0
    return min(score, 100.0)


def _score_evidence_quality(claims: list[Claim]) -> float:
    """Average of tier weights for the highest-tiered proof per unique skill_id."""
    if not claims:
        return 0.0
        
    best_tier_per_skill: dict[str, float] = {}
    
    for claim in claims:
        tier = getattr(claim, "evidence_tier", "T8") or "T8"
        tier_weight = _TIER_WEIGHTS.get(tier, 0.1)
        skill_ids = getattr(claim, "skill_ids", []) or []
        
        for skill_id in skill_ids:
            if skill_id not in best_tier_per_skill or tier_weight > best_tier_per_skill[skill_id]:
                best_tier_per_skill[skill_id] = tier_weight
                
    if not best_tier_per_skill:
        return 0.0
    
    avg_weight = sum(best_tier_per_skill.values()) / len(best_tier_per_skill)
    return min(avg_weight * 100.0, 100.0)


def _score_keyword_coverage(claims: list[Claim], benchmark: Benchmark) -> float:
    """70% weight for exact matching + 30% for semantic synonym map coverage."""
    required_terms = getattr(benchmark, "required_terms", []) or []
    if not required_terms:
        return 100.0
    
    all_text = " ".join(getattr(c, "claim_text", "") or "" for c in claims).lower()
    
    exact_matches = 0
    semantic_matches = 0
    total_terms = len(required_terms)
    
    for term in required_terms:
        term_lower = term.lower()
        if term_lower in all_text:
            exact_matches += 1
            semantic_matches += 1
        else:
            synonyms = SYNONYM_MAP.get(term_lower, [])
            if any(syn in all_text for syn in synonyms):
                semantic_matches += 1
                
    exact_score = (exact_matches / total_terms) * 70.0
    semantic_score = (semantic_matches / total_terms) * 30.0
    
    return min(exact_score + semantic_score, 100.0)


def _score_portfolio_quality(claims: list[Claim], benchmark: Benchmark) -> float:
    """Count unique document_ids from publishable claims vs portfolio_targets."""
    if not claims:
        return 0.0
        
    unique_docs = set()
    for claim in claims:
        doc_id = getattr(claim, "document_id", None)
        if doc_id:
            unique_docs.add(doc_id)
        else:
            unique_docs.add(id(claim))
            
    count = len(unique_docs)
    targets = getattr(benchmark, "portfolio_targets", 3) or 3
    
    return min(count / max(targets, 1), 1.0) * 100.0


def _score_completeness(claims: list[Claim]) -> float:
    """Heuristic on profile depth: multiple source types, spans, diverse skill_ids."""
    if not claims:
        return 0.0

    sources = {getattr(c, "source_type", "") for c in claims if getattr(c, "source_type", "")}
    has_spans = any(getattr(c, "source_span", None) is not None for c in claims)
    skills = {s for c in claims for s in (getattr(c, "skill_ids", []) or [])}
    
    score = 0.0
    score += min(len(sources) * 10, 30.0)
    
    if has_spans:
        score += 30.0
        
    score += min(len(skills) * 5, 40.0)
    
    return min(score, 100.0)


def _score_conversion(claims: list[Claim]) -> float:
    """Density of persuasive proof words across publishable claims."""
    if not claims:
        return 0.0
        
    proof_words = {
        "increased", "reduced", "achieved", "delivered", 
        "optimized", "scaled", "automated", "improved", 
        "grew", "boosted"
    }
    
    total_matches = 0
    for claim in claims:
        text = (getattr(claim, "claim_text", "") or "").lower()
        words = text.split()
        for w in words:
            clean_w = "".join(c for c in w if c.isalpha())
            if clean_w in proof_words:
                total_matches += 1
                
    return min((total_matches / 10.0) * 100.0, 100.0)


def _score_pricing_strategy(rate_desired: float | None, benchmark: Benchmark) -> float:
    """How close the desired rate is to the benchmark rate_band midpoint."""
    band_min = getattr(benchmark, "rate_band_min", None)
    band_max = getattr(benchmark, "rate_band_max", None)

    if rate_desired is None or band_min is None or band_max is None:
        return 50.0 
    
    midpoint = (band_min + band_max) / 2.0
    
    if band_min <= rate_desired <= band_max:
        return 100.0
    
    diff = abs(rate_desired - midpoint)
    spread = (band_max - band_min) or 10.0
    
    decay = (diff / spread) * 20.0
    return max(100.0 - decay, 0.0)


def score_profile(
    claims: list[Claim],
    benchmark: Benchmark,
    rate_desired: float | None = None,
) -> tuple[float, dict[str, float]]:
    """
    Score profile across multiple dimensions.
    
    Args:
        claims: Evaluated claims for the profile.
        benchmark: Benchmark context for scaling.
        rate_desired: Target hourly/project rate.
        
    Returns:
        A tuple of (readiness_score, dimension_scores_dict).
    """
    dimensions = {
        "positioning": _score_positioning(claims, benchmark),
        "evidence_quality": _score_evidence_quality(claims),
        "keyword_coverage": _score_keyword_coverage(claims, benchmark),
        "portfolio_quality": _score_portfolio_quality(claims, benchmark),
        "completeness": _score_completeness(claims),
        "conversion": _score_conversion(claims),
        "pricing_strategy": _score_pricing_strategy(rate_desired, benchmark),
    }
    
    readiness = sum(
        dimensions[k] * getattr(WEIGHTS, k)
        for k in dimensions
    )
    
    return round(readiness, 2), {k: round(v, 2) for k, v in dimensions.items()}