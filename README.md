# AI5K Platform 🚀

AI5K is an organization-first, evidence-based AI capability platform designed to securely and deterministically evaluate, score, and match developer profiles to opportunities using verified claims.

This repository is a **Full-Stack Monorepo**, containing both the Python FastAPI Backend (Modular Monolith) and the Next.js Multi-Engine Portal Frontend.

## 🌐 Live Deployments

- **Frontend (Vercel):** [https://ai5k-engines.vercel.app](https://ai5k-engines.vercel.app)
- **Backend API (Render):** `https://ai5k-engines.onrender.com`

---

## 🎨 Frontend: Multi-Engine Portal (`/frontend`)

The frontend is a gorgeous, flat-architecture multi-page portal built with **Next.js (React)** and **TailwindCSS v4**.

It consists of four distinct "Engines", each accessible from the Master Landing Page:
1. **Profile Intelligence (`/profile`):** Upload CVs (with drag-and-drop) to generate Readiness Gauges and 7-Dimension Cyber Radars.
2. **Opportunity Intelligence (`/opportunity`):** Matches capabilities against target job descriptions.
3. **Organization Teaming (`/teaming`):** Constructs optimized delivery pods based on capacity and budget.
4. **Proposal Workbench (`/proposal`):** Generates high-converting, XML-tagged proposals injecting real verified claims.

### Running the Frontend Locally
```bash
cd frontend
npm install
npm run dev
```
*(The frontend will start on `http://localhost:3000` and communicate with the live Render backend by default).*

---

## 🏗️ Backend: Modular Monolith (`/app`)

The backend is built with **FastAPI** and **SQLAlchemy 2.0 (Async)**, utilizing the `pgvector` extension for semantic embedding matches.

The codebase is strictly organized into domains:
- `/app/evidence`: Handles claim parsing, evidence tier assignment (T1-T8), and verification.
- `/app/scoring`: Computes multi-dimensional readiness scores and identifies skill gaps.
- `/app/generation`: Uses LLMs (Groq) to generate deterministic proposals and gap-closure action plans.
- `/app/platform`: Orchestrates the asynchronous pipeline execution and status tracking.
- `/app/services`: Contains business logic such as the `calculate_match_score` matcher.

### Running the Backend Locally
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```
*(You will need to set a `.env` file with `DATABASE_URL` and `GROQ_API_KEY`).*

---

## 🔌 Native MCP Server

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
