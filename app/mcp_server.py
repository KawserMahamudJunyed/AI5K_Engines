import asyncio
import json
import uuid
import os

from mcp.server.fastmcp import FastMCP

from app.core.db import get_db
from app.models.profile import ProfileRun, ClaimRecord
from app.models.opportunity import Opportunity
from app.schemas.result import PipelineInput
from app.platform.pipeline import run_pipeline
from app.platform.status_store import StatusStore
from app.platform.router import _DefaultLLMClient, _DefaultGeneratorLLM
from app.services.matcher import calculate_match_score
from app.schemas.opportunity import ParsedOpportunity
from app.schemas.claim import Claim
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

mcp = FastMCP("ai5k-local-engine")

@mcp.tool()
async def analyze_local_profile(cv_path: str, github_username: str | None = None, upwork_text: str | None = None) -> str:
    """Reads a local PDF CV path, gathers GitHub/Upwork data, invokes the pipeline orchestrator, and returns readiness metrics."""
    try:
        if not os.path.exists(cv_path):
            return f"Error: File not found at {cv_path}"
            
        with open(cv_path, "rb") as f:
            cv_pdf_bytes = f.read()

        github_data = {"username": github_username} if github_username else None
        input_data = PipelineInput(
            cv_pdf_bytes=cv_pdf_bytes,
            github_data=github_data,
            upwork_text=upwork_text
        )

        run_id = uuid.uuid4()
        store = StatusStore()
        await store.create_run(run_id)

        llm_client = _DefaultLLMClient()
        generator_llm = _DefaultGeneratorLLM()

        result = await run_pipeline(
            input_data=input_data,
            niche="ai-ml-engineer",
            version="1.0",
            run_id=run_id,
            status_store=store,
            llm_client=llm_client,
            generator_llm=generator_llm
        )

        # Ensure it wraps db sessions
        async for db in get_db():
            db_run = ProfileRun(
                id=str(run_id),
                readiness_score=result.readiness_score,
                dimension_scores=result.dimension_scores,
                blocking_items=result.blocking_items,
                generated_assets=result.generated_assets,
                niche="ai-ml-engineer",
                version="1.0",
                status="success"
            )
            db.add(db_run)
            await db.commit()
            break  # Only need one session

        response = {
            "run_id": str(run_id),
            "readiness_score": result.readiness_score,
            "dimension_scores": result.dimension_scores,
            "claims_extracted": len(result.claims) if result.claims else 0
        }
        return json.dumps(response, indent=2)

    except Exception as e:
        return f"Error during analysis: {str(e)}"

@mcp.tool()
async def get_profile_gaps(run_id: str) -> str:
    """Queries the database for a prior Result run and returns the prioritized list of GapActions."""
    try:
        async for db in get_db():
            result = await db.get(ProfileRun, run_id)
            if not result:
                return f"Error: No profile run found for ID {run_id}"
            
            # Since gap_actions aren't natively stored on ProfileRun in the provided DB schema,
            # we'll extract them from generated_assets or blocking_items for this demonstration,
            # or return the blocking_items as gaps.
            gaps = []
            if result.generated_assets and "skill_gaps" in result.generated_assets:
                gaps = result.generated_assets["skill_gaps"]
            elif result.blocking_items:
                gaps = [{"action_title": item, "effort_hours_est": 2, "score_gain_est": 5} for item in result.blocking_items]
            
            return json.dumps({"run_id": run_id, "gaps": gaps}, indent=2)

    except Exception as e:
        return f"Error fetching profile gaps: {str(e)}"

@mcp.tool()
async def match_local_job(job_description_path: str, user_id: str) -> str:
    """Reads a local job description, runs our 5-Factor Matcher against user verified claims, and returns match breakdown."""
    try:
        if not os.path.exists(job_description_path):
            return f"Error: Job description file not found at {job_description_path}"
            
        with open(job_description_path, "r", encoding="utf-8") as f:
            job_text = f.read()

        async for db in get_db():
            # Get user's latest profile run and claims
            stmt = select(ProfileRun).where(ProfileRun.user_id == user_id).order_by(ProfileRun.created_at.desc())
            db_run = await db.execute(stmt)
            latest_run = db_run.scalar_first()
            
            if not latest_run:
                return f"Error: No profile found for user {user_id}"
            
            # Fetch claims
            claims_stmt = select(ClaimRecord).where(ClaimRecord.profile_run_id == latest_run.id)
            claims_res = await db.execute(claims_stmt)
            claim_records = claims_res.scalars().all()
            
            user_claims = []
            for cr in claim_records:
                user_claims.append(Claim(
                    claim_text=cr.claim_text,
                    skill_ids=cr.skill_ids,
                    evidence_tier=cr.evidence_tier,
                    tier_rule=cr.tier_rule or "Rule",
                    publishable=True
                ))
            
            # Dummy ParsedOpportunity
            opp = ParsedOpportunity(
                id=uuid.uuid4(),
                title="Local Job",
                raw_text=job_text,
                budget_usd=5000,
                required_skills=["Python", "FastAPI"],
                timezone_constraints=[],
                vertical_domain="tech"
            )
            
            # Mock benchmark
            from app.schemas.benchmark import Benchmark
            benchmark = Benchmark(niche="ai-ml-engineer", version="1.0", core_skills=["Python", "FastAPI"])
            
            # calculate_match_score takes opp (ParsedOpportunity or model?), claims, benchmark
            match = await calculate_match_score(opp, user_claims, benchmark, db)
            
            return json.dumps({
                "overall_score": match.overall_score,
                "skill_match": match.skill_match_score,
                "evidence_quality": match.evidence_quality_score,
                "vertical_alignment": match.vertical_alignment_score,
                "timezone_compatibility": match.timezone_compatibility_score,
                "budget_alignment": match.budget_alignment_score
            }, indent=2)

    except Exception as e:
        return f"Error matching local job: {str(e)}"

@mcp.tool()
async def draft_proposal(opportunity_id: str, user_id: str) -> str:
    """Generates an XML-style proposal applying verified claim tags and auto-injecting warnings for missing requirements."""
    try:
        from app.services.proposal_draft import draft_verifiable_proposal
        
        async for db in get_db():
            opp = await db.get(Opportunity, opportunity_id)
            if not opp:
                # Use a dummy opportunity for local offline generation if not in DB
                opp_text = "Software Engineer needed for backend API."
            else:
                opp_text = opp.raw_description

            stmt = select(ProfileRun).where(ProfileRun.user_id == user_id).order_by(ProfileRun.created_at.desc())
            db_run = await db.execute(stmt)
            latest_run = db_run.scalar_first()
            
            if not latest_run:
                return f"Error: No profile found for user {user_id}"

            # Mock claims
            claims_stmt = select(ClaimRecord).where(ClaimRecord.profile_run_id == latest_run.id)
            claims_res = await db.execute(claims_stmt)
            claim_records = claims_res.scalars().all()
            
            user_claims = []
            for cr in claim_records:
                user_claims.append(Claim(
                    claim_text=cr.claim_text,
                    skill_ids=cr.skill_ids,
                    evidence_tier=cr.evidence_tier,
                    tier_rule=cr.tier_rule or "Rule",
                    publishable=True
                ))
            
            from app.schemas.opportunity import ParsedOpportunity
            parsed_opp = ParsedOpportunity(
                id=uuid.UUID(opportunity_id) if len(opportunity_id) == 36 else uuid.uuid4(),
                title="Job",
                raw_text=opp_text,
                budget_usd=5000,
                required_skills=["Python"],
                timezone_constraints=[],
                vertical_domain="tech"
            )

            proposal = await draft_verifiable_proposal(parsed_opp, user_claims)
            return proposal.raw_xml

    except Exception as e:
        return f"Error drafting proposal: {str(e)}"


def main():
    """Run the FastMCP server over stdio."""
    mcp.run()

if __name__ == "__main__":
    main()
