from __future__ import annotations
import asyncio
import uuid
from datetime import datetime, timezone
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import patch

from app.models.base import Base
from app.main import create_app
from app.schemas.claim import SourceSpan, Claim
from app.schemas.benchmark import Benchmark

@pytest.fixture(autouse=True)
def mock_vector_service(monkeypatch):
    """Globally mock the ML vector model to prevent heavy Tensorflow/SciPy loads during tests."""
    async def mock_generate_embedding(text: str):
        # Return deterministic float list depending on technical vs non-technical
        import numpy as np
        vec = np.zeros(384)
        if "FastAPI" in text or "Python" in text:
            vec[0:192] = 0.8  # Technical vector
        else:
            vec[192:384] = 0.8 # Non-technical vector
        return vec.tolist()
        
    monkeypatch.setattr("app.services.vector_service.generate_embedding", mock_generate_embedding)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture
async def async_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def async_session(async_engine) -> AsyncGenerator[AsyncSession, None]:
    factory = async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    async with factory() as session:
        yield session

@pytest_asyncio.fixture
async def client():
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

# ── Factory fixtures ──

@pytest.fixture
def make_source_span():
    def _factory(text: str = "sample evidence text", start: int = 0, doc_id: uuid.UUID | None = None):
        doc_id = doc_id or uuid.uuid4()
        return SourceSpan(
            document_id=doc_id,
            start_index=start,
            end_index=start + len(text),
            text=text,
        )
    return _factory

@pytest.fixture
def make_claim(make_source_span):
    def _factory(
        claim_text: str = "Built a REST API",
        skill_ids: list[str] | None = None,
        source_type: str = "cv",
        evidence_tier: str = "T8",
        tier_rule: str = "self_declared",
        with_span: bool = True,
        span_text: str | None = None,
    ):
        span = None
        if with_span:
            span = make_source_span(text=span_text or claim_text)
        return Claim(
            claim_text=claim_text,
            skill_ids=skill_ids or ["python"],
            source_type=source_type,
            source_span=span,
            evidence_tier=evidence_tier,
            observed_date=datetime.now(timezone.utc),
            recency_factor=1.0,
            tier_rule=tier_rule,
        )
    return _factory

@pytest.fixture
def sample_benchmark():
    return Benchmark(
        niche="ai-ml-engineer",
        version="1.0",
        required_terms=["python", "pytorch", "tensorflow", "mlops", "docker", "kubernetes"],
        benchmark_topics=["deep learning", "model deployment", "data pipelines"],
        title_formula="{niche} | {specialty} | {platform}",
        portfolio_targets=5,
        overview_targets=3,
        rate_band=(75.0, 150.0),
        dimension_targets={
            "positioning": 80.0,
            "evidence_quality": 80.0,
            "keyword_coverage": 70.0,
            "portfolio_quality": 70.0,
            "completeness": 60.0,
            "conversion": 50.0,
            "pricing_strategy": 70.0,
        },
    )