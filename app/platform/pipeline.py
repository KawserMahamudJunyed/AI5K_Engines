from __future__ import annotations
import uuid
import json
from pathlib import Path
from datetime import datetime, timezone

from app.core.config import settings
from app.core.errors import AppError, ErrorCode
from app.schemas.claim import Claim
from app.schemas.benchmark import Benchmark, load_benchmark
from app.schemas.result import Result, PipelineInput
from app.ingestion.cv_parser import parse_cv_pdf, parse_cv_text
from app.ingestion.github_parser import parse_github_data
from app.ingestion.upwork_parser import parse_upwork_text
from app.ingestion.extractor import ClaimExtractor, LLMClient
from app.evidence.tiers import assign_tiers
from app.scoring.score_dimensions import score_profile
from app.scoring.caps import apply_hard_caps
from app.scoring.gaps import rank_gaps, extract_blocking_items
from app.scoring.skill_gaps import find_skill_gaps
from app.generation.generator import AssetGenerator, GeneratorLLM, DraftAsset
from app.generation.validator import validate_asset, ValidationResult
from app.platform.status_store import StatusStore

__all__ = ["run_pipeline"]

async def run_pipeline(
    input_data: PipelineInput,
    niche: str,
    version: str,
    run_id: uuid.UUID,
    status_store: StatusStore,
    llm_client: LLMClient,
    generator_llm: GeneratorLLM,
) -> Result:
    try:
        # Stage 1: extract_claims
        await status_store.update_stage(run_id, 0)
        extractor = ClaimExtractor(llm_client)
        all_claims = []
        source_texts = {}
        
        if input_data.cv_pdf_path:
            cv_text = parse_cv_pdf(Path(input_data.cv_pdf_path))
            cv_id = uuid.uuid4()
            source_texts[cv_id] = cv_text
            cv_claims = await extractor.extract(cv_text, cv_id)
            all_claims.extend(cv_claims)
        elif input_data.cv_text:
            cv_text = parse_cv_text(input_data.cv_text)
            cv_id = uuid.uuid4()
            source_texts[cv_id] = cv_text
            cv_claims = await extractor.extract(cv_text, cv_id)
            all_claims.extend(cv_claims)
            
        if input_data.github_url:
            gh_data = parse_github_data(input_data.github_url)
            gh_id = uuid.uuid4()
            source_texts[gh_id] = str(gh_data)
            gh_claims = await extractor.extract(str(gh_data), gh_id)
            all_claims.extend(gh_claims)
            
        if input_data.upwork_url:
            uw_text = parse_upwork_text(input_data.upwork_url)
            uw_id = uuid.uuid4()
            source_texts[uw_id] = uw_text
            uw_claims = await extractor.extract(uw_text, uw_id)
            all_claims.extend(uw_claims)

        # Stage 2: load_benchmark
        await status_store.update_stage(run_id, 1)
        benchmark_path = Path(f"app/data/benchmarks/{niche}_{version}.json")
        if not benchmark_path.exists():
            raise AppError(ErrorCode.BENCHMARK_NOT_FOUND, f"Benchmark {niche}_{version} not found")
        benchmark = load_benchmark(benchmark_path)

        # Stage 3: assign_tiers
        await status_store.update_stage(run_id, 2)
        tiered_claims = assign_tiers(all_claims, benchmark)

        # Stage 4: score_profile
        await status_store.update_stage(run_id, 3)
        scores = score_profile(tiered_claims, benchmark)
        capped_scores = apply_hard_caps(scores, tiered_claims, benchmark)

        # Stage 5: rank_gaps
        await status_store.update_stage(run_id, 4)
        gaps = rank_gaps(capped_scores, benchmark)
        blocking_items = extract_blocking_items(gaps)
        skill_gaps = find_skill_gaps(tiered_claims, benchmark)

        # Stage 6: generate
        await status_store.update_stage(run_id, 5)
        generator = AssetGenerator(generator_llm)
        draft = await generator.generate(tiered_claims, benchmark)
        
        validation = validate_asset(draft, tiered_claims, source_texts)
        if not validation.validated:
            raise AppError(ErrorCode.VALIDATION_FAILED, f"Validation issues: {validation.issues}")
            
        result = Result(
            run_id=run_id,
            claims=tiered_claims,
            scores=capped_scores,
            gaps=gaps,
            blocking_items=blocking_items,
            skill_gaps=skill_gaps,
            draft_asset=draft,
            created_at=datetime.now(timezone.utc)
        )
        
        await status_store.complete(run_id, result)
        return result

    except AppError:
        raise
    except Exception as exc:
        await status_store.fail(run_id, str(exc))
        raise AppError(ErrorCode.PIPELINE_FAILED, str(exc)) from exc