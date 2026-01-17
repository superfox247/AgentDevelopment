# Architecture Guide: The Agent Factory

This document provides a comprehensive overview of the **Agent Factory** architecture. It is designed to be a reference for understanding how the system works and a guide for extending it.

## 1. High-Level Overview

The system follows a **Domain-Driven Design (DDD)** approach within a **Monorepo Structure**:
*   **Domains**: Vertical slices of backend business logic (AI Agents).
*   **Apps**: Consumer applications (Frontend UIs, CLIs).
*   **Platform**: Shared infrastructure.
*   **Registry**: Shared definitions.

### System Diagram

```mermaid
graph TD
    subgraph Apps ["🖥️ Client Apps"]
        Web[apps/web (Dashboard)]
        CLI[apps/cli (Terminal)]
    end

    subgraph Registry ["📚 Registry (Definitions)"]
        Models[Pydantic Models]
        Prompts[System Instructions]
    end

    subgraph Platform ["🛠️ Agent Platform (Infrastructure)"]
        Config[Configuration]
        Auth[Authentication]
        Comms[A2A Communication]
        Flow[Control Flow & Callbacks]
    end

    subgraph Domains ["🧠 Business Logic (Headless Backend)"]
        Research[Researcher Agent]
        Judge[Judge Agent]
        Content[Content Builder]
        Image[Image Generator]
        Orch[Orchestrator]
    end

    Web -- "REST/JSON" --> Orch
    Models --> Domains
    Prompts --> Domains
    Config --> Domains
    Flow --> Domains
    Domains -- "Standard A2A Protocol" --> Domains
```

## 2. Core Components

### 🖥️ Apps (`apps/`)
**Purpose**: Deployable client applications.
*   **`apps/web/`**: The Agent Debug Dashboard (Nginx + Vanilla JS). A standalone container that consumes the Agent API.

### 📚 The Registry (`registry/`)
**Purpose**: The Single Source of Truth for all data structures and prompts.
*   **`registry/models/`**: Contains shared Pydantic models. All agents must import their Request/Response models from here.
*   **`registry/prompts/`**: Contains Markdown files with system instructions. Never hardcode prompts in Python files.

### 🛠️ The Agent Platform (`agent_platform/`)
**Purpose**: Shared infrastructure to prevent code duplication.
*   **`agent_platform.callbacks`**: Utilities for saving agent state (e.g., `create_save_output_callback`).
*   **`agent_platform.control_flow`**: Reusable logic for loop management (e.g., `StateConditionEscalator`).
*   **`agent_platform.config`**: Centralized configuration and environment variable parsing.
*   **`agent_platform.models`**: Standard API models (`ChatRequest`, `FeedbackRequest`).
*   **`agent_platform.observability`**: Standardized logging and tracing configuration.

### 🏢 Domains (`domains/`)
**Purpose**: Self-contained business logic units (Microservices).
Each domain folder (e.g., `domains/course_creator`) corresponds to a specific capability.
*   **`agent.py`**: Defines the Agent logic, tools, and sub-agents.
*   **`server.py`**: Exposes the Agent via a standard FastAPI server using `create_platform_app`.

## 3. Developer Guide

### How to Add a New Agent

1.  **Define Interface**: detailed in `registry/models/<domain>.py`.
2.  **Create Domain**: detailed in `domains/<domain>/`.
3.  **Implement Logic**:
    *   Import prompts from `registry`.
    *   Import infrastructure from `agent_platform`.
4.  **Register**: Add services to `docker-compose.yml`.

### Common Patterns

#### 1. Feedback Loops (Judge/Critic)
To implement a loop that continues until a condition is met (e.g., "Pass" from a Judge), use the **StateConditionEscalator**.

```python
from agent_platform.control_flow import StateConditionEscalator

# 1. Define the check
def is_passing(feedback: dict) -> bool:
    return feedback.get("status") == "pass"

# 2. Add as a sub-agent
checker = StateConditionEscalator(
    name="checker",
    state_key="judge_feedback", # The state key to watch
    success_predicate=is_passing
)
```

#### 2. Pipeline Data Flow
To ensure one agent's output is available for the next agent (or for a Judge), use **Callbacks**.

```python
from agent_platform.callbacks import create_save_output_callback

researcher = Agent(
    ...,
    # Saves the final response to ctx.session.state["findings"]
    after_agent_callback=create_save_output_callback("findings")
)
```

#### 3. Hosting a Frontend UI (Decoupled Pattern)
**Do NOT host UIs inside the Agent.** Agents should be headless APIs.
Instead, create a separate application in `apps/`.

1.  **Backend**: Keep `orchestrator/server.py` pure.
2.  **Frontend**: Create `apps/my_ui/` (React, Nginx, Streamlit).
3.  **Docker**: Run the UI as a separate service that talks to the Backend container.

## 4. Project Structure

```text
.
├── apps/                 # CLIENT APPLICATIONS
│   └── web/              # Dashboard UI (Nginx)
├── agent_platform/       # SHARED INFRASTRUCTURE
│   ├── callbacks.py      # State management helpers
│   ├── control_flow.py   # Loop control agents
│   ├── config.py         # Global config
│   └── models.py         # Shared API models
├── domains/              # BUSINESS LOGIC (AGENTS)
│   └── course_creator/
│       ├── orchestrator/ # The brain (API)
│       ├── researcher/   # A worker
│       └── judge/        # A worker
├── artifacts/            # PERSISTENT AGENT OUTPUTS
├── registry/             # DEFINITIONS
│   ├── models/           # Pydantic schemas
│   └── prompts/          # System prompts (.md)
└── docker-compose.yml    # Deployment config
```

## 5. Official Documentation

Essential references for the core technologies used in this platform:

### 🧠 AI Models & API
*   **Imagen 3 / 4**: [Google AI for Developers - Imagen](https://ai.google.dev/gemini-api/docs/imagen) (Use `google-genai` SDK)
*   **Gemini API**: [Google AI for Developers - Gemini API](https://ai.google.dev/gemini-api/docs)

### 🐍 Python SDKs
*   **Google Gen AI SDK**: [PyPI](https://pypi.org/project/google-genai/) | [GitHub](https://github.com/googleapis/python-genai) | [API Reference](https://googleapis.github.io/python-genai/)
*   **Agent Development Kit**: [GitHub](https://github.com/google/project-id-728889814494/adk) | [Google Cloud Agents](https://cloud.google.com/agents)

### 🐳 Infrastructure
*   **Docker Compose**: [Compose File V3 Reference](https://docs.docker.com/compose/compose-file/compose-file-v3/)
*   **FastAPI**: [Usage Guide](https://fastapi.tiangolo.com/tutorial/)
*   **Pydantic**: [Models](https://docs.pydantic.dev/latest/concepts/models/)

### 📚 Documentation
*   **Standards**: [Documentation Standards](file:///c:/Users/Aaron/Workspace2/course-creation-ai-agent-architecture/docs/documentation_standards.md) (includes Mermaid Syntax)
*   **Available Models**: [Gemini Models](file:///c:/Users/Aaron/Workspace2/course-creation-ai-agent-architecture/docs/available_models.md) (Auto-updated)
