# Product Design Document: Super Powered IDE

## 1. Executive Summary
A standalone **Local AI Orchestrator** designed to run alongside your existing workflows. Instead of reinventing the IDE, this system acts as a "Super Powered" control plane. It orchestrates a fleet of specialized local Docker containers (RAG, Knowledge Graphs, Vector DBs) and manages a high-performance **Local Intelligence Layer** on consumer hardware (RTX 4090).

## 2. Hardware Strategy
*   **Primary Compute**: NVIDIA RTX 4090 (24GB VRAM).
*   **Orchestration Goal**: Maximize VRAM usage by dynamically loading/unloading models or running optimized concurrent workloads.
*   **Performance Baseline**:
    *   Target Speed: >100 tokens/sec for chat (verified 126 t/s).
    *   Engine: Flexible backend selection (ExLlamaV2, llama.cpp) based on live benchmarks.

## 3. System Architecture

### 3.1 The "Local Cloud" Ecosystem (Docker Compose)
We will treat your machine as a private cloud region. All services are defined in a single `docker-compose.yml`.

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

## 4. Local Brain & Model Strategy
We will maintain an up-to-date registry of best-in-class models for specific tasks, swapping them as new SOTA models release.

| Capability | Potential Model Architectures | Backend |
| :--- | :--- | :--- |
| **Coding/Logic** | DeepSeek-Coder, CodeLlama, Phind (Quantized) | ExLlamaV2 (Speed focus) |
| **General Chat** | Llama-3, Mistral, Yi | ExLlamaV2 |
| **Embedding** | Nomic-Embed, BERT-based | Infinity / TEI (High throughput) |
| **Function Calling** | Specialized fine-tunes (NexusRaven, Gorilla) | llama.cpp |

## 5. Development Roadmap
1.  **Infrastructure Setup**: Define the `docker-compose` stack for the core services (Vector DB, Graph DB).
2.  **Orchestrator MVP**: Simple UI to view status of containers and send a prompt to the "Brain".
3.  **Agent Integration**: Connect the "Brain" to the Docker tools (giving it tool use capabilities).
