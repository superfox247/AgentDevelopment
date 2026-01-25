---
description: Comprehensive checklist for testing agents end-to-end
---

# Agent Testing Checklist

This workflow provides a systematic approach to verify all parts of an agent work correctly. Use this checklist after creating or modifying an agent.

## Pre-Testing Setup

- [ ] **Environment**: Ensure `.env` file exists with `GOOGLE_API_KEY` (or Vertex credentials)
- [ ] **Dependencies**: Run `uv sync` to ensure all dependencies are installed
- [ ] **Agent Structure**: Verify agent folder structure matches expected pattern
- [ ] **Registry Discovery**: Verify agent appears in `GET /api/agents` endpoint

## 1. Agent Registry & Discovery

### Backend API Tests

- [ ] **List Agents Endpoint**
  ```bash
  curl http://localhost:8010/api/agents
  ```
  - Should return agent in list
  - Response includes `name`, `domain`, `path`

- [ ] **Agent Metadata Endpoint**
  ```bash
  curl http://localhost:8010/api/agents/<agent_name>/metadata
  ```
  - Returns `name`, `path`, `description`, `model`, `has_server`
  - `description` matches agent definition
  - `model` matches agent definition
  - `has_server` is `true` if `server.py` exists

- [ ] **Agent Config Endpoint**
  ```bash
  curl http://localhost:8010/api/agents/<agent_name>
  ```
  - Returns `agent.py` source code
  - Content is valid Python

### Frontend UI Tests

- [ ] **Agents View Loads**
  - Navigate to Agents tab in dashboard
  - Agent list displays without errors
  - Loading states work correctly

- [ ] **Agent Metadata Display**
  - Select an agent from the list
  - Description is visible
  - Model name is displayed
  - Server status indicator shows correctly
  - Agent code viewer shows `agent.py` content

- [ ] **Agent List Item Preview**
  - Agent cards show description preview
  - Model name visible in list
  - Server indicator (if available) shows

## 2. Agent Core Functionality

### ADK Web UI Testing

- [ ] **Launch ADK Web UI**
  ```bash
  cd agents/<agent_name>
  uv run adk web .
  ```
  - UI opens at default port (usually http://localhost:8080)
  - Agent appears in agent selector
  - No errors in console

- [ ] **Basic Chat Interaction**
  - Send a simple message to the agent
  - Agent responds (may take time for LLM)
  - Response is coherent and relevant

- [ ] **Events Tab**
  - Navigate to Events tab
  - See user message event
  - See agent response event
  - Tool calls visible (if agent uses tools)

- [ ] **Trace Tab**
  - Navigate to Trace tab
  - See execution trace
  - Tool invocations visible
  - State changes visible (if applicable)

- [ ] **Session Management**
  - Start new session
  - Previous session history preserved
  - Can switch between sessions

### Tool Functionality

- [ ] **Tool Invocation**
  - Agent uses tools when appropriate
  - Tool results are visible in Events/Trace
  - Tool errors handled gracefully

- [ ] **Tool Output**
  - Tool returns expected data format
  - Agent can process tool results
  - Multiple tool calls work correctly

### Callbacks

- [ ] **Callback Execution**
  - Check logs for callback execution
  - Before/after callbacks fire correctly
  - Callback logic works as expected

## 3. Agent Server (FastAPI)

### Server Entry Point

- [ ] **Server File Exists**
  - `agents/<agent_name>/server.py` exists
  - Imports are correct
  - No syntax errors

- [ ] **Server Starts**
  ```bash
  cd agents/<agent_name>
  uv run uvicorn server:app --host 0.0.0.0 --port 8080
  ```
  - Server starts without errors
  - Health check endpoint works: `GET /health`
  - Root route works: `GET /`

- [ ] **API Endpoints**
  - Chat endpoint: `POST /chat` (if implemented)
  - A2A protocol endpoints work (if enabled)
  - OpenAPI docs available: `GET /docs`

### Docker Deployment

- [ ] **Dockerfile Works**
  ```bash
  docker build -f agent_platform/Dockerfile.agent \
    --build-arg AGENT_PATH=agents/<agent_name> \
    -t <agent_name>:latest .
  ```
  - Build succeeds
  - No errors in build logs

- [ ] **Container Runs**
  ```bash
  docker run -p 8080:8080 <agent_name>:latest
  ```
  - Container starts
  - Health check passes
  - API endpoints accessible

## 4. Frontend Integration

### Dashboard Integration

- [ ] **Agent Appears in UI**
  - Agent listed in Agents view
  - Metadata displays correctly
  - No console errors

- [ ] **Agent Interaction** (if chat UI implemented)
  - Can send messages to agent
  - Responses display correctly
  - Streaming works (if implemented)
  - Error handling works

### Status Panel

- [ ] **Service Status**
  - Agent service shows correct status
  - Online/offline indicator accurate
  - Logs accessible (if implemented)

## 5. Evaluations

### Unit-Style Evaluations

- [ ] **Run Test File**
  ```bash
  uv run adk eval agents/<agent_name> \
    agents/<agent_name>/evaluations/<test>.test.json
  ```
  - Evaluation runs without errors
  - Scores meet thresholds in `test_config.json`
  - Results are readable

### EvalSet Evaluations

- [ ] **Run EvalSet**
  ```bash
  uv run adk eval agents/<agent_name> \
    agents/<agent_name>/evaluations/<set>.evalset.json
  ```
  - All sessions in evalset run
  - Aggregate scores calculated
  - Results summary is clear

### Evaluation Results

- [ ] **Review Results**
  - Check tool trajectory scores
  - Check response match scores
  - Identify any failures
  - Document issues for improvement

## 6. Unit Tests

### Tool Tests

- [ ] **Run Tool Tests**
  ```bash
  uv run pytest agents/<agent_name>/tests/test_tools.py -v
  ```
  - All tests pass
  - Coverage is adequate
  - Edge cases handled

### Callback Tests (if applicable)

- [ ] **Run Callback Tests**
  ```bash
  uv run pytest agents/<agent_name>/tests/test_callbacks.py -v
  ```
  - All tests pass
  - Callback logic verified

## 7. Documentation

- [ ] **README.md**
  - Purpose clearly stated
  - Usage instructions complete
  - Environment setup documented
  - Examples provided

- [ ] **Code Documentation**
  - Docstrings on public functions
  - Type hints present
  - Complex logic explained

## 8. Integration Testing

### End-to-End Flow

- [ ] **Complete User Journey**
  1. Agent discovered by registry
  2. Metadata visible in dashboard
  3. Agent can be launched via ADK web
  4. Agent responds to queries
  5. Tools work correctly
  6. Results are usable

### Error Handling

- [ ] **Error Scenarios**
  - Invalid input handled gracefully
  - Tool failures don't crash agent
  - Network errors handled
  - Timeout scenarios work

## 9. Performance

- [ ] **Response Times**
  - Initial response within acceptable range
  - Tool calls complete in reasonable time
  - No memory leaks observed

- [ ] **Resource Usage**
  - CPU usage reasonable
  - Memory usage stable
  - No excessive API calls

## 10. Security

- [ ] **API Keys**
  - Keys not hardcoded
  - `.env` file in `.gitignore`
  - `.env.example` provided

- [ ] **Input Validation**
  - User input sanitized
  - Tool inputs validated
  - No injection vulnerabilities

## Quick Test Script

For rapid verification, run this script:

```bash
#!/bin/bash
AGENT_NAME="researcher_agent"

echo "1. Testing registry discovery..."
curl -s http://localhost:8010/api/agents | jq ".agents[] | select(.name==\"$AGENT_NAME\")"

echo "2. Testing metadata endpoint..."
curl -s http://localhost:8010/api/agents/$AGENT_NAME/metadata | jq

echo "3. Testing agent config..."
curl -s http://localhost:8010/api/agents/$AGENT_NAME | head -20

echo "4. Testing ADK web UI..."
cd agents/$AGENT_NAME
uv run adk web . &
WEB_PID=$!
sleep 5
curl -s http://localhost:8080/health || echo "Health check failed"
kill $WEB_PID 2>/dev/null

echo "5. Running unit tests..."
uv run pytest agents/$AGENT_NAME/tests/ -v

echo "6. Running evaluations..."
uv run adk eval agents/$AGENT_NAME agents/$AGENT_NAME/evaluations/*.test.json
```

## Troubleshooting

### Agent Not Discovered
- Check `agent.py` exists and has `root_agent` variable
- Verify agent folder is in `agents/` directory
- Check registry logs for parsing errors

### Metadata Missing
- Ensure `description` and `model` are keyword arguments in `LlmAgent()` call
- Check AST parsing didn't fail (see logs)

### Server Won't Start
- Verify `server.py` imports are correct
- Check `root_agent` is exported from `agent.py`
- Ensure dependencies are installed

### ADK Web UI Issues
- Check `GOOGLE_API_KEY` is set
- Verify model name is correct
- Check network connectivity for API calls

## Next Steps After Testing

1. **Document Issues**: Create issues for any failures
2. **Update Checklist**: Add agent-specific test cases
3. **Improve Coverage**: Add tests for uncovered scenarios
4. **Performance Tuning**: Optimize slow operations
5. **User Feedback**: Gather feedback from actual usage
