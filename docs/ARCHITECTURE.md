# System Architecture

## Overview
Antigravity operates as a **Local Cloud**, treating your development machine as a private cluster. All services, including specialist agents, are defined in a unified `docker-compose.yml` stack.

## 🏗 High-Level Topology

```mermaid
graph TD
    User["User / IDE"] --> Orchestrator["Orchestrator UI (React)"]
    Orchestrator --> Brain["Brain Router (Ollama/Gemini)"]
    
    subgraph LocalCloud ["Local Cloud (Docker)"]
        Brain --> VectorDB[("Qdrant Vector Store")]
        Brain --> GraphDB[("Neo4j Graph Store")]
        
        Orchestrator --> AgentFleet["Agent Fleet"]
        
        subgraph AgentFleetGroup ["Agent Fleet"]
            BaseAgent["Base Agent"]
        end
        
        AgentFleet -- Tools --> Browser["Headless Browser"]
    end
```

## 🧩 Core Components

### 1. Orchestrator (Dashboard)
*   **Role**: The central command center. A React v19 application referenced in `frontend/`.
*   **Function**: Manages agent lifecycles, visualizes "thoughts", and provides a chat interface for complex task delegation.

### 2. The "Brain"
*   **Role**: Inference and Context Management.
*   **Implementation**: A hybrid router that selects between:
    *   **Online**: Google Gemini / OpenAI (for reasoning/planning).
    *   **Local**: Ollama running Llama-3/DeepSeek (for speed/privacy).
*   **Data Stores**:
    *   **Neo4j**: Storing code relationships and concepts (Knowledge Graph).
    *   **Qdrant**: Fast embedding search for RAG.

### 3. Agent Fleet
Agents are standalone Docker containers that expose a standardized API (Google ADK protocol).
*   **Location**: `agents/` (Source of Truth).
*   **Pattern**: Python-based agents defined in `agent.py` with `root_agent`.

## 🧠 Hybrid Intelligence Strategy

We leverage a "Best Tool for the Job" approach:

| Capability | Model Source | Examples | Use Case |
| :--- | :--- | :--- | :--- |
| **Reasoning & Planning** | **Cloud** | Gemini Ultra, GPT-4o | Architecting features, complex refactors. |
| **Speed & Privacy** | **Local (GPU)** | Llama-3, DeepSeek-Coder | Syntax fixing, simple chat, auto-complete. |
| **Vision** | **Cloud** | Imagen, Gemini Pro Vision | UI design generation, screenshot analysis. |

## 📂 Directory Structure

*   `agents/`: Domain-specific agent implementations (The Fleet).
*   `agent_platform/`: Shared core libraries, auth, and config.
*   `frontend/`: The React-based Orchestrator UI.
*   `docs/`: This documentation.

## 🕸 Detailed Network Topology

The following diagram illustrates the detailed interaction between the Dashboard, Orchestrator, and the Agent Swarm.

```mermaid
graph TD
    %% Define Styles
    classDef frontend fill:#3b82f6,stroke:#1d4ed8,color:white;
    classDef backend fill:#10b981,stroke:#059669,color:white;
    classDef agent fill:#8b5cf6,stroke:#7c3aed,color:white;
    classDef telemetry fill:#f59e0b,stroke:#d97706,color:white;
    classDef docker fill:#e5e7eb,stroke:#374151,color:black,stroke-dasharray: 5 5;

    %% Client Layer
    User["User Browser"] -->|HTTP :5173| Dashboard["Dashboard UI"]
    class Dashboard frontend

    %% Backend Layer
    Dashboard -->|API :8000 / WebSocket| AgentPlatform["Agent Platform (FastAPI)"]
    class AgentPlatform backend

    %% Infrastructure
    AgentPlatform -->|"Docker Socket"| DockerEngine["Docker Engine"]

    %% Docker Bridge Network
    subgraph DockerNetwork ["Agent Swarm (Docker Bridge Network)"]
        direction TB

        BaseAgent["Base Agent"]
        class BaseAgent agent

        %% Telemetry
        Phoenix["Phoenix Tracing"]
        class Phoenix telemetry

        %% Interactions
        AgentPlatform <-->|HTTP| BaseAgent

        %% Telemetry Flow
        AgentPlatform -.->|"gRPC/HTTP"| Phoenix
        BaseAgent -.->|"gRPC/HTTP"| Phoenix
    end
```

