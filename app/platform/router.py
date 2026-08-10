from __future__ import annotations
import uuid
from typing import Any
from fastapi import APIRouter, BackgroundTasks, Query, status, HTTPException, Form, File, UploadFile
from fastapi.responses import JSONResponse, RedirectResponse

from app.schemas.result import PipelineInput, PipelineStatus
from app.platform.status_store import StatusStore
from app.platform.pipeline import run_pipeline
from app.core.errors import AppError, ErrorCode, ErrorResponse, to_response
from app.core.config import settings
from app.ingestion.extractor import LLMClient
from app.generation.generator import GeneratorLLM
from app.schemas.claim import Claim
from app.schemas.benchmark import Benchmark
from app.ingestion.github_parser import fetch_and_normalize_github

__all__ = ["router", "get_status_store"]

router = APIRouter(prefix="/analyze", tags=["analysis"])
_store = StatusStore()


def get_status_store() -> StatusStore:
    """Return the module-level status store singleton."""
    return _store


# ── Default stubs for dependency injection ──

class _DefaultLLMClient:
    """No-op LLM client for local testing."""

    async def extract_claims(
        self, source_text: str, source_type: str, pass_number: int
    ) -> list[dict[str, Any]]:
        return []


class _DefaultGeneratorLLM:
    """No-op generator LLM for local testing."""

    async def generate_title(
        self, claims: list[Claim], benchmark: Benchmark
    ) -> str:
        return "Generated Title"

    async def generate_overview(
        self, claims: list[Claim], benchmark: Benchmark
    ) -> str:
        return "Generated Overview"

    async def generate_case_studies(
        self, claims: list[Claim], benchmark: Benchmark
    ) -> list[dict[str, str]]:
        return []

    async def generate_gap_actions(
        self, claims: list[Claim], benchmark: Benchmark
    ) -> list[dict[str, Any]]:
        return [
            {
                "action_title": "Upload a verified project repository",
                "effort_hours_est": 5,
                "score_gain_est": 15,
                "remediation_link": "/assessments/github"
            },
            {
                "action_title": "Pass Python System Design Test",
                "effort_hours_est": 2,
                "score_gain_est": 20,
                "remediation_link": "/assessments/tests"
            }
        ]

from app.platform.llm import GroqClient, GroqGenerator

@router.post("")
async def start_analysis(
    background_tasks: BackgroundTasks,
    niche: str = Query("ai-ml-engineer", description="Target niche identifier"),
    version: str = Query("1.0", description="Benchmark version"),
    cv_file: UploadFile | None = File(None),
    cv_text: str | None = Form(None),
    github_url: str | None = Form(None),
    upwork_url: str | None = Form(None),
    rate_desired: float | None = Form(None),
) -> RedirectResponse:
    """Launch a pipeline run and redirect to the status endpoint."""
    run_id = uuid.uuid4()
    await _store.create_run(run_id)

    # 1. Parse GitHub URL if provided
    github_data = None
    if github_url:
        github_data = await fetch_and_normalize_github(github_url)

    # 2. Extract PDF bytes if provided
    cv_pdf_bytes = None
    if cv_file and cv_file.filename:
        cv_pdf_bytes = await cv_file.read()

    # 3. Construct the strict Pydantic payload
    input_data = PipelineInput(
        cv_text=cv_text,
        cv_pdf_bytes=cv_pdf_bytes,
        github_data=github_data,
        upwork_text=upwork_url, # The system treats this as raw text for MVP
        rate_desired=rate_desired,
    )

    if settings.groq_api_key and settings.groq_api_key.get_secret_value():
        llm_client = GroqClient(api_key=settings.groq_api_key.get_secret_value())
        generator_llm = GroqGenerator(api_key=settings.groq_api_key.get_secret_value())
    else:
        llm_client = _DefaultLLMClient()
        generator_llm = _DefaultGeneratorLLM()

    background_tasks.add_task(
        run_pipeline,
        input_data,
        niche,
        version,
        run_id,
        _store,
        llm_client,
        generator_llm,
    )

    return JSONResponse(
        content={"run_id": str(run_id), "status_url": f"/analyze/{run_id}/status"},
        status_code=status.HTTP_202_ACCEPTED,
    )


@router.get("/{run_id}/status")
async def get_analysis_status(run_id: uuid.UUID) -> JSONResponse:
    """Check the status of a pipeline run."""
    run_status = await _store.get_status(run_id)
    if run_status is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return JSONResponse(content=run_status.model_dump(mode="json"))


@router.get("/{run_id}/result")
async def get_analysis_result(run_id: uuid.UUID) -> JSONResponse:
    """Get the result of a completed pipeline run."""
    run_status = await _store.get_status(run_id)
    if run_status is None:
        raise HTTPException(status_code=404, detail="Run not found")
    if run_status.error:
        return JSONResponse(
            content={"error": run_status.error or "Unknown pipeline error"},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
    result = await _store.get_result(run_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Result not found")
    return JSONResponse(content=result.model_dump(mode="json"))