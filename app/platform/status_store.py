from __future__ import annotations
import asyncio
import uuid
from datetime import datetime, timezone
from app.schemas.result import PipelineStatus, Result

__all__ = ["StatusStore"]

_STAGE_NAMES = [
    "extract_claims",
    "load_benchmark",
    "assign_tiers",
    "score_profile",
    "rank_gaps",
    "generate",
]

class StatusStore:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._statuses: dict[uuid.UUID, PipelineStatus] = {}
        self._results: dict[uuid.UUID, Result] = {}

    async def create_run(self, run_id: uuid.UUID) -> PipelineStatus:
        async with self._lock:
            status = PipelineStatus(
                run_id=run_id,
                status="running",
                progress_pct=0.0,
                current_stage="extract_claims",
                started_at=datetime.now(timezone.utc),
                completed_at=None,
                error=None
            )
            self._statuses[run_id] = status
            return status

    async def update_stage(self, run_id: uuid.UUID, stage_index: int) -> None:
        async with self._lock:
            if run_id in self._statuses:
                status = self._statuses[run_id]
                status.current_stage = _STAGE_NAMES[stage_index]
                status.progress_pct = (stage_index / len(_STAGE_NAMES)) * 100.0

    async def complete(self, run_id: uuid.UUID, result: Result) -> None:
        async with self._lock:
            if run_id in self._statuses:
                status = self._statuses[run_id]
                status.status = "completed"
                status.progress_pct = 100.0
                status.completed_at = datetime.now(timezone.utc)
            self._results[run_id] = result

    async def fail(self, run_id: uuid.UUID, error: str) -> None:
        async with self._lock:
            if run_id in self._statuses:
                status = self._statuses[run_id]
                status.status = "failed"
                status.error = error
                status.completed_at = datetime.now(timezone.utc)

    async def get_status(self, run_id: uuid.UUID) -> PipelineStatus | None:
        async with self._lock:
            return self._statuses.get(run_id)

    async def get_result(self, run_id: uuid.UUID) -> Result | None:
        async with self._lock:
            return self._results.get(run_id)