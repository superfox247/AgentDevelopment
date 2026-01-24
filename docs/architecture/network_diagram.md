# Network Architecture Diagram

This document outlines the network interaction and flow between the Dashboard, the Orchestrator, and the Agent Swarm.

```mermaid
graph TD
    %% Define Styles
    classDef frontend fill:#3b82f6,stroke:#1d4ed8,color:white;
    classDef backend fill:#10b981,stroke:#059669,color:white;
    classDef agent fill:#8b5cf6,stroke:#7c3aed,color:white;
    classDef telemetry fill:#f59e0b,stroke:#d97706,color:white;
    classDef docker fill:#e5e7eb,stroke:#374151,color:black,stroke-dasharray: 5 5;

    %% Client Layer
    User[User Browser] -->|HTTP :5175| Dashboard[Dashboard UI]
    class Dashboard frontend

    %% Backend Layer
    Dashboard -->|API :8010 / WebSocket| DashboardServer[Dashboard Backend (FastAPI)]
    class DashboardServer backend

    %% Infrastructure
    DashboardServer -->|Docker Socket| DockerEngine[Docker Engine]

    %% Docker Bridge Network
    subgraph Docker_Network ["Agent Swarm (Docker Bridge Network)"]
        direction TB

        Orchestrator[Orchestrator Agent]
        class Orchestrator agent

        %% Sub-Agents
        CustomerService[Customer Service]
        ContentBuilder[Content Builder]
        ImageGen[Image Generator]
        Researcher[Researcher]
        Judge[Judge]

        class CustomerService,ContentBuilder,ImageGen,Researcher,Judge agent

        %% Telemetry
        Phoenix[Phoenix Tracing]
        class Phoenix telemetry

        %% Interactions
        Orchestrator <-->|HTTP| CustomerService

        %% Pipeline Flow
        Orchestrator -->|Routes Request| Pipeline(Course Creation Pipeline)
        Pipeline -->|HTTP| Researcher
        Researcher -->|HTTP| Judge
        Judge -->|Feedback Loop| Researcher

        Pipeline -->|HTTP| ContentBuilder
        Pipeline -->|HTTP| ImageGen

        %% Telemetry Flow
        Orchestrator -.->|gRPC/HTTP| Phoenix
        CustomerService -.->|gRPC/HTTP| Phoenix
        ContentBuilder -.->|gRPC/HTTP| Phoenix
        ImageGen -.->|gRPC/HTTP| Phoenix
        Researcher -.->|gRPC/HTTP| Phoenix
        Judge -.->|gRPC/HTTP| Phoenix
    end

    %% Host Verification (Special Case)
    DashboardServer -->|Subprocess call| VerificationRunner[Verification Script (Host)]
    VerificationRunner -.->|Imports| Agents_On_Host[Agent Code (Host)]
```

## Description from `GEMINI.md` Principles
The system follows a **Factory Pattern** where each agent is self-contained. The **Platform Layer** (Phoenix) provides shared observability.
- **Frontend**: React-based Dashboard v2.
- **Backend**: Python FastAPI serving status and logs.
- **Agents**: Dockerized services communicating via HTTP/REST (using `RemoteA2aAgent` or direct calls).
