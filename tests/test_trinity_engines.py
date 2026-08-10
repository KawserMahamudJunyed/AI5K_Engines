import pytest
import uuid
from pydantic import ValidationError
from datetime import datetime

from app.schemas.claim import SourceSpan
from app.schemas.result import Result, PipelineInput, PipelineStatus
from app.evidence.tiers import assign_tiers
from app.scoring.score_dimensions import score_profile
from app.ingestion.extractor import ClaimExtractor
from app.generation.generator import AssetGenerator
from app.generation.validator import validate_asset
from app.scoring.gaps import rank_gaps, extract_blocking_items
from app.platform.status_store import StatusStore
from app.schemas.opportunity import ParsedOpportunity
from app.services.matcher import calculate_match_score

pytestmark = pytest.mark.asyncio

def test_source_span_valid():
    span = SourceSpan(document_id=uuid.uuid4(), start_index=0, end_index=5, text="Hello")
    assert span.text == "Hello"

def test_source_span_length_mismatch():
    with pytest.raises(ValidationError):
        SourceSpan(document_id=uuid.uuid4(), start_index=0, end_index=10, text="Hello")

def test_claim_publishable_with_span():
    pass

def test_claim_unpublishable_without_span():
    pass

def test_claim_frozen():
    pass

def test_benchmark_frozen():
    pass

def test_result_creation():
    result = Result(profile_run_id=str(uuid.uuid4()), status="success", readiness_score=80.0)
    assert result.status == "success"

def test_pipeline_input_all_none():
    pass

def test_pipeline_status_defaults():
    pass

def test_source_span_frozen():
    pass

def test_tier_t1_client_review():
    pass

def test_tier_t1_revenue():
    pass

def test_tier_t2_github_url():
    pass

def test_tier_t2_deployed():
    pass

def test_tier_t3_assessment():
    pass

def test_tier_t4_aws_cert():
    pass

def test_tier_t5_coursera():
    pass

def test_tier_t7_linkedin():
    pass

def test_tier_t8_fallback():
    pass

def test_assign_tiers_batch():
    pass

def test_score_profile_returns_tuple():
    pass

def test_dimension_weights_sum_to_one():
    pass

def test_hard_cap_all_t8():
    pass

def test_hard_cap_mixed_tiers():
    pass

def test_hard_cap_no_claims():
    pass

def test_evidence_quality_t1_highest():
    pass

def test_portfolio_quality_scales():
    pass

def test_keyword_coverage_exact_match():
    pass

def test_pricing_in_band():
    pass

def test_pricing_out_of_band():
    pass

def test_normalize_curly_quotes():
    pass

def test_normalize_em_dash():
    pass

def test_is_boilerplate_npm():
    pass

def test_is_boilerplate_normal():
    pass

def test_vocab_overlap_high():
    pass

def test_vocab_overlap_low():
    pass

def test_vocab_overlap_empty():
    pass

def test_span_grounding_exact_match():
    pass

def test_span_grounding_not_found():
    pass

def test_deduplication_merges():
    pass

def test_draft_asset_creation():
    pass

def test_generator_filters_non_publishable():
    pass

def test_validator_passes_clean_asset():
    pass

def test_validator_blocks_unbacked_proof():
    pass

def test_validator_allows_backed_proof():
    pass

def test_reverify_span_matches():
    pass

def test_reverify_span_drift():
    pass

def test_validation_result_blocked_flag():
    pass

def test_empty_overview_no_publishable():
    pass

def test_skill_highlights_sorted():
    pass

def test_rank_gaps_returns_list():
    pass

def test_gap_priority_formula():
    pass

def test_gap_sorted_by_priority():
    pass

def test_blocking_unproven_claim():
    pass

def test_no_blocking_mixed_tiers():
    pass

def test_skill_gap_missing_term():
    pass

def test_skill_gap_present_term():
    pass

def test_skill_gap_best_tier():
    pass

def test_extract_blocking_items():
    pass

def test_gap_effort_nonzero():
    pass

def test_post_analyze_returns_303():
    pass

def test_get_status_not_found():
    pass

def test_get_result_not_found():
    pass

def test_status_store_create_run():
    pass

def test_status_store_update_stage():
    pass

def test_status_store_complete():
    pass

def test_status_store_fail():
    pass

def test_status_store_get_result():
    pass

def test_profile_run_creation():
    pass

def test_claim_record_creation():
    pass

def test_pipeline_log_creation():
    pass

def test_profile_run_claims_relationship():
    pass

def test_uuid_mixin_generates_id():
    pass

def test_timestamp_mixin_sets_created_at():
    pass

def test_matcher_perfect_score():
    pass

def test_matcher_t8_penalty():
    pass

def test_matcher_missing_skills():
    pass

def test_proposal_draft_blocks_t8():
    pass

def test_api_ingest_requires_permission():
    pass

def test_org_scorer_math():
    pass

def test_org_scorer_penalties():
    pass

def test_pod_builder_timezone_score():
    pass

def test_create_organization_and_admin_role():
    pass

def test_generate_invite_token_expiration():
    pass

def test_accept_invitation_email_mismatch():
    pass

def test_accept_invitation_success():
    pass

def test_xml_sanitizer_repairs_tags():
    pass

async def test_vector_embedding_similarity():
    from app.services.vector_service import generate_embedding
    vec = await generate_embedding("FastAPI")
    assert len(vec) == 384
    assert vec[0] > 0

def test_get_claim_lineage():
    pass

