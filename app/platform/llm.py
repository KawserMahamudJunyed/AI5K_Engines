"""Groq LLM implementations for extraction and generation."""
from __future__ import annotations

import json
from typing import Any

from groq import AsyncGroq

from app.schemas.claim import Claim
from app.schemas.benchmark import Benchmark
from app.core.config import settings
from app.ingestion.extractor import LLMClient
from app.generation.generator import GeneratorLLM

__all__ = ["GroqClient", "GroqGenerator"]


class GroqClient(LLMClient):
    """Groq implementation for extracting claims."""
    
    def __init__(self, api_key: str, model: str = settings.groq_model) -> None:
        self.client = AsyncGroq(api_key=api_key)
        self.model = model

    async def extract_claims(
        self, source_text: str, source_type: str, pass_number: int
    ) -> list[dict[str, Any]]:
        """Extract claims from the source text using JSON mode."""
        prompt = (
            f"You are an expert technical recruiter analyzing a {source_type}. "
            f"Pass {pass_number}: Read the document and extract specific, granular skill claims. "
            "For each claim, you MUST provide the exact substring from the document in 'evidence_quote'. "
            "Output strictly a JSON object with a 'claims' array. Each object in the array MUST have: "
            "'claim_text' (str), 'evidence_quote' (str), 'skill_ids' (list of str), 'evidence_tier' (str like 'T1'-'T8'), "
            "and 'observed_date' (str ISO date).\n\n"
            f"Document:\n{source_text}"
        )

        response = await self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a precise JSON-only extraction engine."},
                {"role": "user", "content": prompt}
            ],
            model=self.model,
            response_format={"type": "json_object"},
            temperature=settings.llm_temperature,
        )

        try:
            content = response.choices[0].message.content or "{}"
            data = json.loads(content)
            return data.get("claims", [])
        except Exception:
            return []


class GroqGenerator(GeneratorLLM):
    """Groq implementation for generating output assets."""

    def __init__(self, api_key: str, model: str = settings.groq_model) -> None:
        self.client = AsyncGroq(api_key=api_key)
        self.model = model

    async def generate_title(
        self, claims: list[Claim], benchmark: Benchmark
    ) -> str:
        prompt = "Based on these verified claims, write a highly professional, 3-7 word job title."
        response = await self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert profile title generator. Output ONLY the title, no quotes or prefix."},
                {"role": "user", "content": prompt + "\n\nClaims: " + str([c.claim_text for c in claims])}
            ],
            model=self.model,
            temperature=settings.llm_temperature,
        )
        return (response.choices[0].message.content or "Professional").strip('\"')

    async def generate_overview(
        self, claims: list[Claim], benchmark: Benchmark
    ) -> str:
        prompt = "Write a compelling, professional 2-3 paragraph overview based ONLY on these verified claims."
        response = await self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a top-tier resume writer. Write the overview."},
                {"role": "user", "content": prompt + "\n\nClaims: " + str([c.claim_text for c in claims])}
            ],
            model=self.model,
            temperature=0.3,
        )
        return response.choices[0].message.content or ""

    async def generate_case_studies(
        self, claims: list[Claim], benchmark: Benchmark
    ) -> list[dict[str, str]]:
        # For MVP, we return an empty list or we can generate them.
        return []

    async def generate_gap_actions(
        self, claims: list[Claim], benchmark: Benchmark
    ) -> list[dict[str, Any]]:
        prompt = (
            "Analyze these claims against standard senior engineering benchmarks. "
            "Identify 3-5 specific actionable gaps (things they are missing or unverified). "
            "Output strictly a JSON object with a 'gap_actions' array. Each object MUST have: "
            "'action_title' (str), 'effort_hours_est' (int, 0-40), 'score_gain_est' (int, 0-30), and 'remediation_link' (str or null)."
        )
        response = await self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert technical assessor. Output ONLY valid JSON."},
                {"role": "user", "content": prompt + "\n\nClaims: " + str([c.claim_text for c in claims])}
            ],
            model=self.model,
            response_format={"type": "json_object"},
            temperature=settings.llm_temperature,
        )
        try:
            content = response.choices[0].message.content or "{}"
            data = json.loads(content)
            return data.get("gap_actions", [])
        except Exception:
            return []