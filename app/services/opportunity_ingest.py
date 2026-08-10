"""Service for ingesting and normalizing opportunities."""
from __future__ import annotations

import json
from groq import AsyncGroq
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.schemas.opportunity import OpportunityInput, ParsedOpportunity
from app.models.opportunity import Opportunity
from datetime import datetime, timedelta, timezone

__all__ = ["ingest_and_normalize", "check_deduplication"]

async def ingest_and_normalize(raw_post: OpportunityInput) -> ParsedOpportunity:
    """Extract structured skills, vertical, and bounds from raw job text using Groq."""
    
    if not settings.groq_api_key or not settings.groq_api_key.get_secret_value():
        # Fallback dummy parser if API key is not set
        return ParsedOpportunity(
            **raw_post.model_dump(),
            required_skills=["python", "fastapi"],
            industry_vertical="Software",
            budget_tier="Medium",
            estimated_effort_hours=40.0
        )
        
    client = AsyncGroq(api_key=settings.groq_api_key.get_secret_value())
    
    prompt = (
        f"You are a technical recruiter. Parse this job description:\n\n{raw_post.description}\n\n"
        "Output strictly a JSON object with:\n"
        "- 'required_skills' (list of strings, normalized)\n"
        "- 'industry_vertical' (string, e.g., 'SMB Automation', 'Mortgage Ops', 'Legal')\n"
        "- 'budget_tier' (string: 'High', 'Medium', or 'Low')\n"
        "- 'estimated_effort_hours' (float, estimate based on duration/description)\n"
    )
    
    response = await client.chat.completions.create(
        messages=[
            {"role": "system", "content": "You are a precise JSON-only extraction engine."},
            {"role": "user", "content": prompt}
        ],
        model=settings.groq_model,
        response_format={"type": "json_object"},
        temperature=0.1,
    )
    
    try:
        content = response.choices[0].message.content or "{}"
        data = json.loads(content)
        
        return ParsedOpportunity(
            **raw_post.model_dump(),
            required_skills=data.get("required_skills", []),
            industry_vertical=data.get("industry_vertical", "Unknown"),
            budget_tier=data.get("budget_tier", "Medium"),
            estimated_effort_hours=float(data.get("estimated_effort_hours", 40.0))
        )
    except Exception:
        # Fallback on failure
        return ParsedOpportunity(
            **raw_post.model_dump(),
            required_skills=[],
            industry_vertical="Unknown",
            budget_tier="Medium",
            estimated_effort_hours=40.0
        )

async def check_deduplication(title: str, description: str, db_session: AsyncSession) -> Opportunity | None:
    """Check if an exact title/description exists within the last 24 hours."""
    yesterday = datetime.now(timezone.utc) - timedelta(days=1)
    
    stmt = select(Opportunity).where(
        Opportunity.title == title,
        Opportunity.description == description,
        Opportunity.created_at >= yesterday
    ).limit(1)
    
    result = await db_session.execute(stmt)
    return result.scalar_one_or_none()