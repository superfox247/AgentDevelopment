# Docker Agent Architecture

## Overview

This document explains how agents are built and deployed using Docker, and how the ADK web UI works in this setup.

## Architecture Diagram

```mermaid
graph TB
    subgraph DevMachine["Development Machine (Windows)"]
        Project["ai-agent-architecture/"]
        Agents["agents/"]
        ResearcherAgent["researcher_agent/"]
        AgentPy["agent.py<br/>(root_agent definition)"]
        InitPy["__init__.py<br/>(exports root_agent)"]
        Entrypoint["docker-entrypoint.sh"]
        PyProject["pyproject.toml"]
        OtherAgents["[other_agents]/"]
        Platform["agent_platform/"]
        Dockerfile["Dockerfile.agent<br/>(universal agent builder)"]
        Compose["docker-compose.yml"]
        
        Project --> Agents
        Project --> Platform
        Project --> Compose
        Agents --> ResearcherAgent
        Agents --> OtherAgents
        ResearcherAgent --> AgentPy
        ResearcherAgent --> InitPy
        ResearcherAgent --> Entrypoint
        ResearcherAgent --> PyProject
        Platform --> Dockerfile
    end
    
    subgraph Container["Docker Container (Linux)"]
        AppDir["/app/"]
        BaseAgent["base_agent/<br/>(Agent 1)"]
        BaseAgentPy["agent.py"]
        BaseAgentInit["__init__.py"]
        ResAgent["researcher_agent/<br/>(Agent 2)"]
        ResAgentPy["agent.py"]
        ResAgentInit["__init__.py"]
        CSAgent["customer_service_agent/<br/>(Agent 3)"]
        CSAgentPy["agent.py"]
        CSAgentInit["__init__.py"]
        SharedPlatform["agent_platform/<br/>(shared platform code)"]
        WorkflowDocs[".agent/<br/>(workflow docs)"]
        Dependencies[".venv/<br/>(Python dependencies)"]
        
        AppDir --> BaseAgent
        AppDir --> ResAgent
        AppDir --> CSAgent
        AppDir --> SharedPlatform
        AppDir --> WorkflowDocs
        AppDir --> Dependencies
        BaseAgent --> BaseAgentPy
        BaseAgent --> BaseAgentInit
        ResAgent --> ResAgentPy
        ResAgent --> ResAgentInit
        CSAgent --> CSAgentPy
        CSAgent --> CSAgentInit
    end
    
    subgraph ADKServer["ADK Web Server (port 8501)"]
        Scan["Scans /app/ for directories<br/>with agent.py"]
        Find1["Finds: /app/base_agent/agent.py"]
        Find2["Finds: /app/researcher_agent/agent.py"]
        Find3["Finds: /app/customer_service_agent/agent.py"]
        Dropdown["Dropdown shows all 3 agents<br/>(by dir name)"]
        AgentDropdown["Agent dropdown:<br/>- base_agent<br/>- researcher_agent<br/>- customer_service_agent"]
        Chat["Chat interface"]
        Tabs["Events/Trace tabs"]
        
        Scan --> Find1
        Scan --> Find2
        Scan --> Find3
        Find1 --> Dropdown
        Find2 --> Dropdown
        Find3 --> Dropdown
        Dropdown --> AgentDropdown
        AgentDropdown --> Chat
        AgentDropdown --> Tabs
    end
    
    DevMachine -->|docker build| Container
    AppDir -->|exec adk web| Scan
    Scan -.->|discovers| BaseAgent
    Scan -.->|discovers| ResAgent
    Scan -.->|discovers| CSAgent
    
    style DevMachine fill:#e1f5ff
    style Container fill:#fff4e1
    style ADKServer fill:#e8f5e9
    style ResearcherAgent fill:#f3e5f5
    style BaseAgent fill:#f3e5f5
    style ResAgent fill:#f3e5f5
    style CSAgent fill:#f3e5f5
```

## Build Process

### 1. Docker Build

```bash
docker build -f agent_platform/Dockerfile.agent \
  --build-arg AGENT_PATH=agents/researcher_agent \
  -t researcher-agent:latest .
```

**Steps:**
1. **Builder stage**: Installs dependencies using `uv`
2. **Runtime stage**: Copies agent to `/app/{agent_name}/` (not `/app/agent/`)
3. **Entrypoint**: Runs `adk web` from `/app/` to discover agents

### 2. Agent Discovery

ADK web discovers agents by:
- Scanning `/app/` for subdirectories
- Looking for `agent.py` files with `root_agent` variable
- Using the **directory name** (not the agent's `name` field) in the dropdown

**Important**: The directory name in the container must match the desired display name.

## Key Files

### Dockerfile.agent
- **Universal builder** for any agent
- Takes `AGENT_PATH` as build argument
- Extracts agent name from path: `agents/researcher_agent` → `researcher_agent`
- Copies agent to `/app/{agent_name}/` to preserve name

### docker-entrypoint.sh
- Runs `adk web` from `/app/` directory
- ADK automatically discovers agents in subdirectories
- Port: 8501 (configurable)

### docker-compose.yml
- Defines `researcher_agent` service
- Maps port `8501:8501`
- Uses common build configuration

## Why This Works

1. **Linux Environment**: Docker runs Linux, avoiding Windows path issues with `adk web`
2. **Proper Naming**: Agent directory keeps its name (`researcher_agent`), not generic `agent`
3. **Discovery**: ADK web scans from parent directory, finds agent by directory name
4. **Isolation**: Each agent runs in its own container

## Multi-Agent Setup

The `all_agents` service contains all 3 agents in a single container:
- `base_agent` - Baseline agent for testing
- `researcher_agent` - Web-capable research assistant
- `customer_service_agent` - Customer service with guardrails

All agents appear in the ADK web UI dropdown at `http://localhost:8501`.

### Running All Agents

```bash
# Build and start the multi-agent container (recommended)
make dev-up-adk              # Uses Makefile command

# Or manually:
docker compose build all_agents
docker compose up -d all_agents

# View logs (recommended)
make dev-logs-service SERVICE=all_agents

# Or manually:
docker compose logs -f all_agents

# Access ADK web UI
# Open http://localhost:8501 in your browser
# Select any agent from the dropdown
```

## Adding New Agents

To add a new agent to the multi-agent container:

1. **Create agent structure**:
   ```bash
   agents/new_agent/
   ├── agent.py          # Must define root_agent
   ├── __init__.py       # Must export root_agent
   └── [other files]
   ```

2. **Update Dockerfile.multi-agent**:
   Add the agent copy step:
   ```dockerfile
   COPY agents/new_agent /app/new_agent
   ```

3. **Update docker-compose.yml**:
   Add volume mount for hot-reload during development:
   ```yaml
   volumes:
     - ./agents/new_agent:/app/new_agent
   ```

4. **Rebuild and restart**:
   ```bash
   docker compose build all_agents
   docker compose up -d all_agents
   ```

The new agent will automatically appear in the ADK web UI dropdown.

## Troubleshooting

### Agent shows as "agent" instead of actual name
- **Cause**: Agent was copied to `/app/agent/` instead of `/app/{agent_name}/`
- **Fix**: Ensure Dockerfile extracts agent name and uses it as directory name

### "agent_platform" appears in dropdown
- **Cause**: `agent_platform/` directory might have an `agent.py` file
- **Fix**: Ensure `agent_platform/` doesn't contain `agent.py` or exclude it from discovery

### ADK web not finding agent
- **Cause**: Running from wrong directory or missing `__init__.py`
- **Fix**: Ensure `adk web` runs from `/app/` and agent has `__init__.py` that exports `root_agent`

## Windows-Specific Notes

- **`adk web` CLI**: Fails on Windows with "Failed to canonicalize script path" error
- **Solution**: Run in Docker (Linux) where it works correctly
- **Proxy Issues**: Docker proxy may need to be disabled for builds:
  ```powershell
  $env:HTTP_PROXY=""; $env:HTTPS_PROXY=""; $env:NO_PROXY="*"
  docker build ...
  ```

## Port Mapping

- **Container**: ADK web runs on port 8501 inside container
- **Host**: Mapped to `localhost:8501` via docker-compose
- **Multiple Agents**: Use different ports (8501, 8502, 8503, etc.)
