# Test Runner Guide

**Smart Test Execution with Early Exit on Failure**

## Overview

The `run_tests.py` script provides a smart test runner that executes tests in optimal order and exits immediately on first failure. This enables fast fix-retry cycles during development.

## Quick Start

```bash
# Run all tests (recommended for pre-commit)
python run_tests.py

# Run tests for a specific agent
python run_tests.py --agent researcher_agent

# Run tests without evaluations (faster, no API keys)
python run_tests.py --skip-evals

# Using Makefile
make test                    # Run all tests
make test-agent AGENT=researcher_agent  # Test specific agent
make test-fast              # Skip evaluations
```

## Test Execution Order

Tests are executed in this order (fastest to slowest, most critical first):

1. **Verification** - Setup checks and agent discovery
   - Verifies researcher agent is discoverable
   - Checks metadata extraction
   - Validates file structure

2. **Unit Tests - Core Utilities**
   - Agent Registry tests
   - Model tests

3. **API Tests**
   - Agent endpoint tests
   - Metadata endpoint tests

4. **Integration Tests**
   - Real agent discovery
   - Metadata extraction from actual files

5. **Agent Tests**
   - Agent-specific unit tests (tools, callbacks, server)

6. **Evaluations** (optional, requires API keys)
   - ADK evaluations
   - Can be skipped with `--skip-evals`

## Command Line Options

```bash
python run_tests.py [OPTIONS]

Options:
  --agent AGENT           Run tests for a specific agent
  --skip-evals            Skip evaluation tests (no API keys needed)
  --skip-verification     Skip verification script
  --verbose, -v           Show verbose output
  --help                  Show help message
```

## Usage Examples

### Pre-Commit Verification

Before committing, run all tests:

```bash
python run_tests.py
```

If any test fails, the runner stops immediately and shows the error. Fix the issue and run again.

### Testing a Specific Agent

When working on a specific agent:

```bash
python run_tests.py --agent researcher_agent
```

This runs:
- Verification
- Core unit tests
- API tests
- Integration tests
- Researcher agent tests
- Researcher agent evaluations (if not skipped)

### Fast Development Cycle

During active development, skip slow evaluations:

```bash
python run_tests.py --skip-evals
```

This runs all tests except evaluations, which require API keys and are slower.

### Verbose Output

See detailed command output:

```bash
python run_tests.py --verbose
```

## Integration with Development Workflow

### Agent Development

When developing a new agent or modifying an existing one:

1. Make your changes
2. Run tests: `python run_tests.py --agent <agent_name>`
3. If tests fail, fix the issue and retry
4. When all tests pass, commit

### Pre-Commit Hook

You can integrate this into a pre-commit hook:

```bash
#!/bin/bash
# .git/hooks/pre-commit

python run_tests.py --skip-evals
exit $?
```

Or use it in CI/CD pipelines to ensure tests pass before merging.

## Exit Codes

- `0` - All tests passed (ready to commit)
- `1` - Test failed (fix and retry)

## Benefits

1. **Fast Feedback**: Exits on first failure, no need to wait for all tests
2. **Smart Order**: Runs fastest tests first, slowest last
3. **Easy Retry**: Quick fix-retry cycles during development
4. **Commit Readiness**: When all pass, you're ready to commit
5. **Flexible**: Can skip slow tests or focus on specific agents

## Troubleshooting

### Tests Fail Immediately

This is expected! The runner exits on first failure to help you:
1. See the error immediately
2. Fix the issue
3. Run again quickly

### Evaluation Tests Fail

If evaluation tests fail due to missing API keys:
- Use `--skip-evals` to skip them
- Or set up your `.env` file with `GOOGLE_API_KEY`

### Command Not Found

Make sure you're in the project root:
```bash
cd /path/to/ai-agent-architecture
python run_tests.py
```

### Verbose Output Needed

If you need to see what commands are being run:
```bash
python run_tests.py --verbose
```

## Integration with Makefile

The Makefile provides convenient shortcuts:

```bash
make test              # Run all tests
make test-fast         # Skip evaluations
make test-agent AGENT=researcher_agent  # Test specific agent
make test-pytest       # Legacy: run pytest directly
```

## Best Practices

1. **Run before committing**: Always run `python run_tests.py` before committing
2. **Use --skip-evals during development**: Faster iteration
3. **Run full suite before PR**: Include evaluations before creating PR
4. **Fix immediately**: When a test fails, fix it before continuing
5. **Keep tests fast**: Unit tests should be fast; save slow tests for CI

## See Also

- [Agent Development Workflow](../.agent/workflows/agent-development.md)
- [Testing Strategy](docs/TESTING.md)
- [Agent Testing Checklist](../.agent/workflows/agent-testing-checklist.md)
