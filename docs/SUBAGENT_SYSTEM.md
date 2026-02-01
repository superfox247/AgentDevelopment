# Subagent System Architecture

> **Last updated**: 2026-01-26  
> **Status**: Active

## Overview

The subagent system uses Cursor's subagent capabilities to orchestrate workflows with context isolation, parallel execution, specialized expertise, and reusability. Instead of a monolithic agent handling all work, the orchestrator delegates to specialized subagents.

## Core Principles

1. **Orchestrator Pattern**: Main agent delegates ALL work to specialized subagents
2. **Nested Delegation**: Subagents can spawn their own subagents
3. **Context Isolation**: Each subagent operates in its own context window
4. **Parallel Execution**: Multiple subagents work simultaneously when possible
5. **Workflow Mapping**: Each workflow phase maps to specialized subagents

## Architecture

```
👤 User
  │
  └─→ 🎯 Orchestrator (Main Agent)
        │
        ├─→ 📚 Understanding Subagent
        ├─→ 💻 Development Subagent
        ├─→ ✅ Code Quality Subagent
        ├─→ 🧪 Testing Subagent
        ├─→ ✓ Verification Subagent
        └─→ 📊 Task Tracking Subagent (background)
```

### Nested Delegation

Subagents can spawn their own subagents:

```
🎯 Orchestrator
  └─→ 💻 Development Subagent
        ├─→ 🔍 Research Subagent (when needed)
        ├─→ 🐛 Debugger Subagent (on error)
        └─→ 🏃 Test Runner Subagent (for tests)
```

## Subagents

### Phase Subagents

| Subagent | Purpose | Model | Mode |
|----------|---------|-------|------|
| **Understanding** | Codebase exploration, research | fast | foreground |
| **Development** | Code implementation | inherit | foreground |
| **Code Quality** | Linting, type checking | fast | foreground |
| **Testing** | Test execution | fast | foreground |
| **Verification** | Validate completion | fast | foreground |

### Support Subagents

| Subagent | Purpose | Model | Mode |
|----------|---------|-------|------|
| **Orchestrator** | Delegates all work | inherit | foreground |
| **Task Tracking** | Progress tracking | fast | background |
| **Research** | Deep research | fast | foreground |
| **Debugger** | Error debugging | inherit | foreground |
| **Test Runner** | Test automation | fast | foreground |

## Execution Patterns

### Sequential (Default)

For feature implementation:
```
Orchestrator → Understanding → Development → Quality → Testing → Verification
```

### Parallel

For independent tasks:
```
Orchestrator → [Development, Quality, Testing, Documentation] (simultaneous)
```

### Nested

For complex tasks:
```
Orchestrator → Development → Debugger → Analysis → [Results flow back up]
```

## Benefits

| Benefit | How It Helps |
|---------|-------------|
| **Context Isolation** | Each phase runs in clean context. No bloat from intermediate outputs. |
| **Parallel Execution** | Multiple phases can run simultaneously (e.g., quality + testing + docs). |
| **Specialized Expertise** | Each subagent focused on one domain. Better results. |
| **Reusability** | Subagents can be used across projects. Consistent patterns. |
| **Nested Delegation** | Complex tasks can spawn specialized helpers. Deep nesting supported. |
| **Cost Efficiency** | Fast models for simple tasks, powerful models for complex work. |

## File Structure

```
.cursor/
  agents/
    - orchestrator.md          # Main orchestrator
    - understanding.md         # Understanding phase
    - development.md            # Development phase
    - code-quality.md          # Quality phase
    - testing.md                # Testing phase
    - verification.md           # Verification phase
    - task-tracking.md         # Task tracking (background)
    - research.md              # Research (nested)
    - debugger.md              # Debugging (nested)
    - test-runner.md           # Test running (nested)
```

## Usage

### For Users

Simply start a task. The orchestrator will:
1. Analyze the task
2. Break it into phases
3. Delegate to appropriate subagents
4. Aggregate results
5. Report completion

### For Developers

When creating new subagents:
1. Create subagent file in `.cursor/agents/`
2. Use YAML frontmatter for metadata
3. Document purpose, process, and delegation patterns
4. Keep focused on single domain

## Example: Feature Implementation

**User**: "Implement login feature"

**Orchestrator actions**:
1. Delegate to `understanding` subagent: "Understand authentication patterns in codebase"
2. Wait for understanding results
3. Delegate to `development` subagent: "Implement login feature based on understanding"
4. Delegate to `code-quality` subagent: "Check code quality"
5. Delegate to `testing` subagent: "Run tests"
6. Delegate to `verification` subagent: "Verify login works"
7. Aggregate results and report to user

**Throughout**: `task-tracking` subagent runs in background to track progress.

## Context Isolation Example

### Before (Monolithic)
```
Main Agent Context Window:
  - User request
  - Understanding phase output (large)
  - Development phase output (large)
  - Code quality checks (verbose)
  - Test results (verbose)
  - Verification results
  - [Context window full! ❌]
```

### After (Subagent)
```
Orchestrator Context:
  - User request
  - Delegation plan
  - Subagent results (summarized)

Understanding Subagent Context:
  - Understanding task
  - Research findings
  - [Isolated, doesn't bloat main context ✅]

Development Subagent Context:
  - Development task
  - Implementation details
  - [Isolated, doesn't bloat main context ✅]

[Each subagent has clean context window ✅]
```

## Quick Reference

### Core Architecture
```
👤 User
  │
  └─→ 🎯 Orchestrator (Main Agent)
        │
        ├─→ 📚 Understanding Subagent
        ├─→ 💻 Development Subagent
        ├─→ ✅ Code Quality Subagent
        ├─→ 🧪 Testing Subagent
        ├─→ ✓ Verification Subagent
        └─→ 📊 Task Tracking Subagent (background)
```

### Execution Patterns
- **Sequential**: Orchestrator → Understanding → Development → Quality → Testing → Verification
- **Parallel**: Orchestrator → [Development, Quality, Testing] (simultaneous)
- **Nested**: Orchestrator → Development → Debugger → Analysis

### Command Reference
All subagents should use Makefile commands for consistency. See [COMMANDS.md](COMMANDS.md) for a complete reference organized by subagent workflow phase.

---

**Last Updated**: 2026-01-26  
**Status**: Active
