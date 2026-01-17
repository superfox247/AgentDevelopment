# Local AI Stack Evaluation

**Objective**: Define the "Standard" ecosystem for a 4090-powered Local AI Orchestrator. We prioritize industry adoption, Docker support, and stability.

## 1. Inference Engine (The "Brain" Runner)
We need a dockerized service to run the LLM.

| Option | Pros | Cons | Verdict |
| :--- | :--- | :--- | :--- |
| **Ollama** | **Industry Standard**. Strong Docker support, auto-GPU detection, huge model library. | Less granular sampling control than raw backends. | **Winner (Ease of Use)** |
| **ExLlamaV2** | **Performance King**. Highest tokens/sec on 4090. | Python integration can be custom. | **Winner (Raw Speed)** |
| **vLLM** | Production Server standard. | High VRAM Usage (KV Cache). | Too heavy for mixed workloads. |

## 2. Knowledge Store (Vector + Graph)
Where do we store the "Knowledge Graph" and embeddings?

| Option | Type | Verdict | Notes |
| :--- | :--- | :--- | :--- |
| **Neo4j** | Graph | **Winner** | The absolute standard for GraphRAG. Native Docker support. |
| **Weaviate** | Vector | **Winner** | Best "Hybrid" search. excellent integration with Graph concepts. |
| **ChromaDB** | Vector | Runner Up | Simple, lightweight, often default for local devs. |

## 3. Orchestration Framework
The code that ties it all together (The "App").

| Option | Focus | Verdict |
| :--- | :--- | :--- |
| **Haystack** | Production Pipelines | **Recommended for Stability**. Clean, modular, less "magic" than LangChain. |
| **LangGraph** | Agent Control | **Recommended for Agents**. **Free/Open Source** library. Can be easily containerized (just Python code). |
| **LlamaIndex** | Data Ingestion | **Recommended for RAG**. Best connectors for data. |

## 4. "Browser Control" & Agents
| Option | Stack | Notes |
| :--- | :--- | :--- |
| **BrowserUse** | Python + Playwright | rising library for simple browser tasks. |
| **OpenDevin** | Dockerized Agent | Full open source "Devin" clone. |

## 5. Proposed "Super Powered" Stack
Based on 3090/4090 hardware constraints and 2025 trends:

### Core Services (Docker Compose)
1.  **Inference**: `Ollama` (Primary) + `ExLlamaV2` (Optional High-Speed Worker).
2.  **Graph Store**: `Neo4j` (Community Edition).
3.  **Vector Store**: `Weaviate` or `Qdrant`.
4.  **Browser**: `Browserless/Chrome` (Headless docker browser).

### Application Layer (The Orchestrator)
*   **Language**: Python (for AI ecosystem dominance).
*   **Framework**: **LlamaIndex** (for Data/RAG) + **LangGraph** (for Agent flows).
*   **UI**: **Streamlit** (MVP) or **Next.js** (Production).

## Decision Required
*   **Inference**: Confirm **Ollama** as the base? (User can swap to ExLlama later for speed).
*   **Graph**: Confirm **Neo4j**?
*   **Orchestration**: Do you prefer a "Pipeline" approach (Haystack) or "Agent" approach (LangGraph)?
