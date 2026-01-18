# Technology Stack & Patterns

**Last Updated:** 2026-01-18
**Status:** Living Document

## Frontend (Dashboard)
- **Framework:** React 19
- **Build Tool:** Vite 7
- **Styling:** Tailwind CSS 4.0
    - *Note:* Uses `@tailwindcss/vite` plugin.
- **Icons:** Lucide React
- **Linting:** ESLint 9 + React Hooks + Refresh

## Backend (Agent Platform)
- **Runtime:** Python 3.10+
- **Framework:** FastAPI + Uvicorn
- **AI/Agent SDKs:** 
    - `google-adk` (Agent Development Kit)
    - `google-genai` (Gemini API)
    - `a2a-sdk` (Agent-to-Agent Communication)
- **Observability:** 
    - Arize Phoenix (Tracing, OTLP)
    - OpenTelemetry

## Infrastructure
- **Containerization:** Docker + Docker Compose
- **Orchestration:** Docker Compose (Service Mesh style)
- **Services:**
    - `orchestrator` (Entry point)
    - `researcher`, `judge`, `content_builder`, `image_generator`, `customer_service` (Worker Agents)
    - `phoenix` (Observability)

## Internal Standards
- **Imports:** `from agent_platform.config import ...`
- **Agent Definition:** `agent.yaml` in `domains/<domain>/<agent>/`
- **Schema-First:** Pydantic models for A2A communication.
