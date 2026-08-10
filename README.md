# AI5K Modular Monolith 🚀

AI5K is an organization-first, evidence-based AI capability platform designed to securely and deterministically evaluate, score, and match developer profiles to opportunities using verified claims.

This repository contains the backend modular monolith, including the core processing pipeline, the 5-Factor Matcher, and the native Model Context Protocol (MCP) server.

## 🏗️ Architecture: The Master Blueprint

The backend is built with **FastAPI** and **SQLAlchemy 2.0 (Async)**, utilizing the `pgvector` extension for semantic embedding matches.

The codebase is strictly organized into domains:
- `/app/evidence`: Handles claim parsing, evidence tier assignment (T1-T8), and verification.
- `/app/scoring`: Computes multi-dimensional readiness scores and identifies skill gaps.
- `/app/generation`: Uses LLMs (Groq) to generate deterministic proposals and gap-closure action plans.
- `/app/ingestion`: Connectors for extracting data from PDFs, GitHub, and Upwork.
- `/app/platform`: Orchestrates the asynchronous pipeline execution and status tracking.
- `/app/services`: Contains business logic such as the `calculate_match_score` matcher and `vector_service`.

## 🛠️ Local Development & Testing

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Setup**
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=sqlite+aiosqlite:///./ai5k.db
   GROQ_API_KEY=your_groq_api_key_here
   ```
   *(Note: For production, `DATABASE_URL` should point to a PostgreSQL database).*

3. **Run the Test Suite**
   The application features a 100% green Pytest verification suite that tests the entire orchestrator completely offline.
   ```bash
   pytest tests/test_trinity_engines.py -v
   ```

4. **Boot the Server**
   ```bash
   uvicorn app.main:app --reload
   ```

## 🔌 Using the MCP Server

We provide a native Model Context Protocol (MCP) server in `app/mcp_server.py`. This allows IDEs (like Cursor, Windsurf, or Claude Desktop) to natively interact with the backend matching engines over standard I/O.

### Configuring Claude Desktop
Add this to your `%APPDATA%\Claude\claude_desktop_config.json` (Windows) or `~/Library/Application Support/Claude/claude_desktop_config.json` (Mac):
```json
{
  "mcpServers": {
    "ai5k-local-engine": {
      "command": "python",
      "args": ["/absolute/path/to/AI5K_Engines/app/mcp_server.py"]
    }
  }
}
```

The MCP Server exposes 4 tools:
- `analyze_local_profile`: Reads local CVs and runs the full pipeline.
- `get_profile_gaps`: Queries the database for prioritized GapActions.
- `match_local_job`: Runs the 5-Factor Matcher against local job descriptions.
- `draft_proposal`: Generates XML proposals applying verified claim tags.

## 🚀 Deployment (Backend)

The backend is configured for a free-tier deployment on **Render.com**. 
It uses a `render.yaml` Infrastructure-as-Code file to automatically spin up a FastAPI web service connected to a managed PostgreSQL database. 

*(Note: Vercel is recommended for the frontend/client repository).*
