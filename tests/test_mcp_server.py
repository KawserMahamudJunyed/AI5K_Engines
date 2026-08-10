import pytest
import inspect
from app.mcp_server import mcp

def test_server_initialization():
    """Verify that the MCP server initializes correctly."""
    assert mcp.name == "ai5k-local-engine"

def test_tool_registration():
    """Verify that all four required tools are registered and have the correct signatures."""
    # Depending on mcp version, tools are typically stored in server._tools or similar.
    # In official Python MCP SDK, the tools are often registered as instances or async functions.
    # Let's verify by inspecting the python globals in mcp_server module or server object.
    
    import app.mcp_server as mcp_mod
    
    # Check that the tool functions exist and have correct schemas
    analyze = getattr(mcp_mod, "analyze_local_profile", None)
    assert analyze is not None
    sig_analyze = inspect.signature(analyze)
    assert "cv_path" in sig_analyze.parameters
    assert "github_username" in sig_analyze.parameters
    assert "upwork_text" in sig_analyze.parameters

    get_gaps = getattr(mcp_mod, "get_profile_gaps", None)
    assert get_gaps is not None
    sig_gaps = inspect.signature(get_gaps)
    assert "run_id" in sig_gaps.parameters

    match_job = getattr(mcp_mod, "match_local_job", None)
    assert match_job is not None
    sig_match = inspect.signature(match_job)
    assert "job_description_path" in sig_match.parameters
    assert "user_id" in sig_match.parameters

    draft = getattr(mcp_mod, "draft_proposal", None)
    assert draft is not None
    sig_draft = inspect.signature(draft)
    assert "opportunity_id" in sig_draft.parameters
    assert "user_id" in sig_draft.parameters

def test_stdio_mocking():
    """Verify that main is a standard function for FastMCP."""
    from app.mcp_server import main
    assert callable(main)
