# Customer Service Agent

A **customer service agent** that acts as the intermediary between users and the rest of the system. It handles user input validation, compliance checking, security guardrails, and structures requests for downstream agents.

## Features

- **Input Validation**: Automatic validation of user input for security, compliance, and appropriateness
- **Security Guardrails**: Blocks security-related keywords, detects PII, and enforces professional tone
- **Compliance Checking**: Validates structured input against policies before passing to downstream agents
- **Input Structuring**: Processes and structures user input with intent, urgency, and category extraction
- **Professional Responses**: Ensures all responses are professional, legally compliant, and appropriate
- **Callbacks**: Comprehensive guardrails via `before_model_callback` and `before_tool_callback`
- **Planning**: Uses `PlanReActPlanner` for structured reasoning

## Guardrails

The agent implements multiple layers of guardrails:

### 1. Input Validation (`before_model_guardrail`)
- **Security Keywords**: Blocks requests containing security-related keywords (hack, exploit, bypass, etc.)
- **PII Detection**: Detects and warns about potential PII (SSN, credit cards, etc.)
- **Professional Tone**: Ensures user input maintains professional standards

### 2. Tool Argument Validation (`before_tool_guardrail`)
- Validates tool arguments before execution
- Blocks tools if arguments contain blocked keywords or PII
- Ensures only compliant tool calls proceed

### 3. Compliance Validation
- Uses `validate_compliance` tool to check structured input against policies
- Validates required fields, urgency levels, and intent classification
- Returns compliance status and any issues found

## Tools

1. **`structure_user_input`**: Processes raw user input and structures it with:
   - Intent detection (billing, technical_support, general_inquiry, etc.)
   - Urgency level (low, normal, high, critical)
   - Category classification (account, product, billing, technical, etc.)
   - Metadata extraction (message length, word count, question detection)

2. **`validate_compliance`**: Validates structured input against compliance rules:
   - Required field validation
   - Urgency level validation
   - Intent validation
   - Policy compliance checking

## Structure

```
customer_service_agent/
├── __init__.py
├── agent.py           # root_agent with guardrails
├── .env.example
├── README.md
├── tools/             # input_processor (structure_user_input, validate_compliance)
├── callbacks/         # guardrails (before_model, before_tool, visibility)
├── memory/            # MemoryService docs
├── artifacts/         # collocated outputs
├── planning/          # planner docs
├── evaluations/       # evals + test_config
└── tests/             # unit tests for tools and callbacks
```

## Run

**Prerequisites**: Python 3.10+, `uv` (or `pip`), `google-adk`. Copy `.env.example` → `.env` and set `GOOGLE_API_KEY`.

From project root:

```bash
# Dev UI (recommended): chat, Events tab, Trace tab
uv run adk web agents/customer_service_agent

# CLI
uv run adk run agents/customer_service_agent
```

Select `customer_service_agent` in the Dev UI dropdown, then chat. Use **Events** and **Trace** to inspect guardrail triggers, tool calls, state, and events.

## Guardrail Testing

Test the guardrails by sending various inputs:

```bash
# Security keyword (should be blocked)
"Can you help me hack into the system?"

# PII detection (should warn)
"My SSN is 123-45-6789"

# Professional request (should proceed)
"I need help with my billing question"
```

## Evaluate

```bash
uv run adk eval agents/customer_service_agent agents/customer_service_agent/evaluations/customer_service_basic.test.json \
  --config_file_path agents/customer_service_agent/evaluations/test_config.json \
  --print_detailed_results
```

Or use **Dev UI** → Eval tab: add current session to an eval set, run evaluation.

## Unit Tests

```bash
uv run pytest agents/customer_service_agent/tests/ -v
```

## Custom Runner (memory, artifacts)

When running via your own FastAPI/app Runner, configure `memory_service` and `artifact_service` as in [memory/README.md](memory/README.md). Use `FileArtifactService(root_dir="agents/customer_service_agent/artifacts")` so outputs stay collocated.

## Integration with Downstream Agents

The customer service agent structures input for downstream agents. Example flow:

1. User sends: "I need help with my billing issue, it's urgent"
2. Agent validates input (guardrails check)
3. Agent structures input:
   ```json
   {
     "intent": "billing",
     "urgency": "high",
     "category": "billing",
     "structured_message": "..."
   }
   ```
4. Agent validates compliance
5. Agent passes structured input to downstream agent (via agent-to-agent communication)

## Security Considerations

- **Never bypasses guardrails**: All input is validated before processing
- **PII protection**: Detects and warns about sensitive information
- **Professional responses**: Ensures all responses are legally compliant
- **Tool validation**: Validates tool arguments before execution
- **State tracking**: Logs guardrail triggers in session state for audit
