# Product Design Document: Super Powered IDE

## 1. Executive Summary
The primary goal is to significantly increase the capabilities of the **Antigravity IDE**, evolving it from a standard consumer-grade AI editor into an **Enterprise-Grade Agentic Personal Assistant**.

Unlike typical IDE assistants that just offer chat, this system acts as a "Super Powered" control plane. It orchestrates a fleet of **Specialist Agents** (running as Docker services) and utilizes deep **Context Engineering** to complete complex work automatically. It manages a high-performance **Hybrid Intelligence Layer** (Online + Local) to deliver capabilities far beyond standard tools.

## 2. Hardware Strategy
*   **Primary Compute**: NVIDIA RTX 4090 (24GB VRAM).
*   **Orchestration Goal**: Maximize VRAM usage by dynamically loading/unloading models or running optimized concurrent workloads.
*   **Performance Baseline**:
    *   Target Speed: >100 tokens/sec for chat (verified 126 t/s).
    *   Engine: Flexible backend selection (ExLlamaV2, llama.cpp) based on live benchmarks.

## 3. System Architecture

### 3.1 The "Local Cloud" Ecosystem (Docker Compose)
We will treat your machine as a private cloud region. All services, including **Specialist Agents**, are defined in a single `docker-compose.yml`. These agents behave like persistent services, performing background workflow automation.

| Service | Image | Port | Purpose |
| :--- | :--- | :--- | :--- |
| **Orchestrator** | `app-orchestrator:latest` | 3000 | The Custom UI/API that manages everything. |
| **Brain Router** | `ollama/ollama:latest` | 11434 | Primary Inference Engine (auto-loads models). |
| **Graph Store** | `neo4j:community` | 7474 | Storing code relationships and concepts. |
| **Vector Store** | `qdrant/qdrant:latest` | 6333 | Fast embedding search. |
| **Browser** | `browserless/chrome` | 3000 | Headless browser for Agents to control. |

### 3.2 The Development Workflow
**"Dev in Antigravity -> Deploy to Container"**

1.  **Development**: You write agent code (e.g., a "Documentation Researcher" graph) inside your current IDE (Antigravity).
2.  **Testing**: Run the agent locally against the `localhost` Docker stack (Ollama, Neo4j, etc.).
3.  **Deployment**:
    *   The agent code is wrapped in a standard `Dockerfile`.
    *   We build the image: `docker build -t local-agent-researcher .`
    *   The Orchestrator spins up this container on-demand.
    *   *Result*: Your Orchestrator works like a "App Store" for your own local agents.

## 4. Hybrid Intelligence Strategy
We will leverage a **Hybrid Approach**, combining the reasoning power of massive online models with the speed, privacy, and cost-efficiency of local models.

### 4.1 Online Large Models (Cloud)
*   **Role**: Complex reasoning, high-level planning, creative generation, and "General Intelligence".
*   **Examples**: Google Gemini Ultra, GPT-4o.
*   **Use Cases**: Architectural review, complex refactoring, image generation (**Imagen 4.0 Ultra**), undefined workflows.

### 4.2 Local Models (Edge - RTX 4090)
*   **Role**: High-speed inference (>100 t/s), privacy-sensitive tasks, retrieval, and "Muscle Memory" tasks.
*   **Examples**: DeepSeek-Coder-V2, Llama-3, Mistral, Qwen.
*   **Use Cases**: Code completion, syntax fixing, fast chat, local RAG, function calling.

## 5. Development Roadmap
1.  **Infrastructure Setup**: Define the `docker-compose` stack for the core services (Vector DB, Graph DB).
2.  **Orchestrator MVP**: Simple UI to view status of containers and send a prompt to the "Brain".
3.  **Agent Integration**: Connect the "Brain" to the Docker tools (giving it tool use capabilities).

## 6. Context Engineering
A dedicated system to manage the "Mental State" of the AI, ensuring it has the right information at the right time without context window overflow.

*   **Memory Management**: Utilizing `GEMINI.md` and `MEMORY.md` for persistent instructions and user preferences.
*   **Knowledge Retrieval**: A "Seek-and-Read" pattern using **Knowledge Items** (curated documentation) and a **Knowledge Graph** (Neo4j) to understand project structure.
*   **Context Injection**: Dynamic injection of relevant artifacts, summaries, and active file content into the Agent's prompt based on the current mode (Planning, Execution, Verification).
