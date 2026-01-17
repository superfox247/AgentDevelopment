# Implementation Plan: Super Powered IDE

**Goal**: Build a Local AI Orchestrator that manages a fleet of Dockerized AI services (Ollama, Neo4j, Qdrant) and provides a "Super Powered" interface for development.

## Phase 1: Infrastructure (The "Local Cloud" Foundation)
**Objective**: Establish a stable, GPU-accelerated Docker environment that hosts all AI services.

### 1.1 Detailed Task Decomposition
- [ ] **Pre-requisite Checks**
    - [ ] Run `wsl --status` to verify WSL2 version.
    - [ ] Run `nvidia-smi` in PowerShell to confirm Host GPU availability.
    - [ ] Check ports `11434` (Ollama), `7474` (Neo4j), `6333` (Qdrant), `3000` (Browserless) for conflicts using `netstat -ano`.
- [ ] **Docker Compose Definition** (`/infra/docker-compose.yml`)
    - [ ] **Network**: Define `local-ai-net` bridge network for internal DNS resolution.
    - [ ] **Service: Ollama**:
        - [ ] Image: `ollama/ollama:latest`
        - [ ] Deploy Config: `resources: reservations: devices: - driver: nvidia`
        - [ ] Volumes: `./ollama/models:/root/.ollama` (Persist models)
    - [ ] **Service: Neo4j**:
        - [ ] Image: `neo4j:community`
        - [ ] Env Vars: `NEO4J_AUTH=none` (Dev mode) or configured password.
        - [ ] Ports: `7474` (HTTP), `7687` (Bolt)
        - [ ] Volumes: `./neo4j/data:/data`
    - [ ] **Service: Qdrant**:
        - [ ] Image: `qdrant/qdrant:latest`
        - [ ] Volumes: `./qdrant/storage:/qdrant/storage`
    - [ ] **Service: Browserless**:
        - [ ] Image: `browserless/chrome:latest`
        - [ ] Env Vars: `MAX_CONCURRENT_SESSIONS=5`
- [ ] **Verification & Scripts**
    - [ ] Create `infra/start.sh` (or `.ps1`) wrapper for `docker-compose up -d`.
    - [ ] Create `infra/test_health.py`:
        - [ ] Python script using `requests` to hit `http://localhost:11434/api/tags`.
        - [ ] Python script using `neo4j` driver to test connection.
        - [ ] Report "Pass/Fail" for the entire stack.

### 1.2 Discovery & Unknowns (Missing Areas)
*   **Networking**: Docker on Windows (WSL2) sometimes has localhost forwarding issues.
    *   *Plan*: We will explicitly map ports to `127.0.0.1` in compose and test `curl localhost` from PowerShell.
*   **Data Persistence**: Storing DB data on the Windows filesystem mounted into WSL2 is SLOW.
    *   *Plan*: We MUST store the Docker Volumes inside the WSL2 filesystem (e.g., `~/local-ai-data`) or a named Docker Volume, NOT a Windows mount (`/mnt/c/...`).
*   **Resource Contention**: running Neo4j (Java) + Ollama (VRAM) + Chrome (RAM) at once.
    *   *Plan*: Set `mem_limit` in docker-compose to prevent system freeze?

### 1.3 User Review Point (Review 1)
> [!IMPORTANT]
> **STOP**: We must verify the `docker-compose.yml` works and the GPU is correctly detected by Ollama before writing any App code.

---

## Phase 2: The Orchestrator (Application Layer)
**Objective**: Build the Python/Web application that acts as the user interface and controller.

### 2.1 Detailed Task Decomposition
- [ ] **Project Setup**
    - [ ] Create `orchestrator/` directory.
    - [ ] Initialize `poetry` or `uv` project.
    - [ ] Dependencies: `fastapi`, `uvicorn`, `docker`, `httpx`, `neo4j`, `qdrant-client`, `langgraph`.
- [ ] **Container Manager Service** (`services/docker_service.py`)
    - [ ] `get_container_status(name: str)`: Returns CPU/Memory/State.
    - [ ] `ensure_service_running(name: str)`: Idempotent start command.
    - [ ] `list_active_models()`: Proxies to Ollama API.
- [ ] **UI Implementation** (Streamlit Prototype)
    - [ ] **Sidebar**: Connection status indicators (Green/Red dots) for all 4 services.
    - [ ] **Page: "Brain"**: Dropdown to `ollama pull` and `ollama run` models.
    - [ ] **Page: "Knowledge"**: Simple statistics (Node count in Graph, Vector count in Qdrant).
- [ ] **Observability** (New Requirement)
    - [ ] Implement `structlog` for structured JSON logging.
    - [ ] Create a `/health` endpoint that aggregates underlying service health.

### 2.2 Discovery & Unknowns (Missing Areas)
*   **Orchestrator Hosting**: Should the Orchestrator itself run in Docker?
    *   *Pros*: Easy networking (can use `http://neo4j:7474`).
    *   *Cons*: harder to access local files (the code you are editing) without mounting.
    *   *Decision*:Run Orchestrator on HOST (Windows/WSL) for development speed, talk to containers via `localhost` ports.
*   **Security**: Authentication?
    *   *Plan*: No Auth for MVP (Localhost only).

### 2.3 User Review Point (Review 2)
> [!IMPORTANT]
> **STOP**: Review the basic UI and Container Management logic. Can we successfully spin up the Stack from the App?

---

## Phase 3: The "Brain" (Agent Framework)
**Objective**: Implement the actual logic: RAG, Graph Exploration, and Browser Control.

### 3.1 Detailed Task Decomposition
- [ ] **Graph Schema Definition**
    - [ ] Define `CodeNode` (File, Function, Class).
    - [ ] Define `ConceptNode` (Abstract topics).
    - [ ] Define Edges: `CALLS`, `DEFINES`, `RELATES_TO`.
- [ ] **RAG Pipeline (LlamaIndex)**
    - [ ] Configure `Neo4jGraphStore`.
    - [ ] Configure `QdrantVectorStore`.
    - [ ] Create `IngestionPipeline` for users' local code files.
- [ ] **Agent Logic (LangGraph)**
    - [ ] **State**: `AgentState` { input, memory, active_tools }.
    - [ ] **Tool: `search_docs`**: Wraps Browserless to search documentation.
    - [ ] **Tool: `query_codebase`**: Wraps LlamaIndex RAG pipeline.
    - [ ] **Node: `reasoning`**: The LLM call to decide next step.
- [ ] **Testing**
    - [ ] Create `benchmark_agent.py`: Run a standard set of questions ("Find the auth logic", "Summarize this file") and grade not just accuracy but *speed*.

### 3.2 Discovery & Unknowns (Missing Areas)
*   **Context Management**: `gpt-oss-20b` context window limit?
    *   *Plan*: Implement aggressive summarization steps in LangGraph before passing data to the final context.
*   **Model "Stupidity"**: Small local models often fail at JSON tool use.
    *   *Plan*: Prepare to use `grammar` sampling (available in llama.cpp/Ollama) to FORCE valid JSON output.

### 3.3 User Review Point (Review 3)
> [!IMPORTANT]
> **STOP**: Review the "Graph Schema" and Agent Logic. Test a simple "Describe this codebase" agent loop.
