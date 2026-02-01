# Subagent Architecture Plan

> **Purpose**: Design a subagent-based system leveraging Cursor's subagent capabilities to orchestrate workflows with context isolation, parallel execution, specialized expertise, and reusability.

## Core Principles

1. **Orchestrator Pattern**: Main agent delegates ALL work to specialized subagents
2. **Nested Delegation**: Subagents can spawn their own subagents
3. **Context Isolation**: Each subagent operates in its own context window
4. **Parallel Execution**: Multiple subagents work simultaneously when possible
5. **Workflow Mapping**: Each workflow phase maps to specialized subagents

---

## Architecture Overview

### Current Architecture (Monolithic)

```mermaid
graph TD
    User["👤 User"] -->|Chat| MainAgent["🤖 Main Agent<br/>(Single Context)"]
    
    MainAgent -->|Sequential| Phase1["📚 Understanding<br/>Workflow"]
    Phase1 -->|Sequential| Phase2["💻 Development<br/>Workflow"]
    Phase2 -->|Sequential| Phase3["✅ Code Quality<br/>Workflow"]
    Phase3 -->|Sequential| Phase4["🧪 Testing<br/>Workflow"]
    Phase4 -->|Sequential| Phase5["✓ Verification<br/>Workflow"]
    
    style MainAgent fill:#ef4444,stroke:#dc2626,color:#fff
    style Phase1 fill:#fbbf24,stroke:#f59e0b
    style Phase2 fill:#3b82f6,stroke:#2563eb
    style Phase3 fill:#10b981,stroke:#059669
    style Phase4 fill:#8b5cf6,stroke:#7c3aed
    style Phase5 fill:#ec4899,stroke:#db2777
```

**Problems**:
- Single context window accumulates all work
- Sequential execution (slow)
- No specialization
- Context bloat from intermediate outputs

---

### Proposed Subagent Architecture

```mermaid
graph TD
    User["👤 User"] -->|Chat| Orchestrator["🎯 Orchestrator Agent<br/>(Main Agent)"]
    
    Orchestrator -->|Delegates| UnderstandingSA["📚 Understanding Subagent"]
    Orchestrator -->|Delegates| DevelopmentSA["💻 Development Subagent"]
    Orchestrator -->|Delegates| QualitySA["✅ Code Quality Subagent"]
    Orchestrator -->|Delegates| TestingSA["🧪 Testing Subagent"]
    Orchestrator -->|Delegates| VerificationSA["✓ Verification Subagent"]
    Orchestrator -->|Delegates| TrackingSA["📊 Task Tracking Subagent"]
    
    UnderstandingSA -.->|Can spawn| ResearchSA["🔍 Research Subagent"]
    DevelopmentSA -.->|Can spawn| DebuggerSA["🐛 Debugger Subagent"]
    TestingSA -.->|Can spawn| TestRunnerSA["🏃 Test Runner Subagent"]
    
    style Orchestrator fill:#6366f1,stroke:#4f46e5,color:#fff
    style UnderstandingSA fill:#fbbf24,stroke:#f59e0b
    style DevelopmentSA fill:#3b82f6,stroke:#2563eb
    style QualitySA fill:#10b981,stroke:#059669
    style TestingSA fill:#8b5cf6,stroke:#7c3aed
    style VerificationSA fill:#ec4899,stroke:#db2777
    style TrackingSA fill:#64748b,stroke:#475569
```

**Benefits**:
- ✅ Context isolation per subagent
- ✅ Parallel execution possible
- ✅ Specialized expertise per phase
- ✅ Reusable subagents across projects

---

## Workflow-to-Subagent Mapping

### Phase-Based Subagents

```mermaid
graph LR
    subgraph "Orchestrator Delegates To"
        O["🎯 Orchestrator"]
    end
    
    subgraph "Phase Subagents"
        U["📚 Understanding<br/>Subagent"]
        D["💻 Development<br/>Subagent"]
        Q["✅ Code Quality<br/>Subagent"]
        T["🧪 Testing<br/>Subagent"]
        V["✓ Verification<br/>Subagent"]
    end
    
    subgraph "Support Subagents"
        TR["📊 Task Tracking<br/>Subagent"]
        R["🔍 Research<br/>Subagent"]
        DB["🐛 Debugger<br/>Subagent"]
        TR2["🏃 Test Runner<br/>Subagent"]
    end
    
    O -->|"1. Understanding Phase"| U
    O -->|"2. Development Phase"| D
    O -->|"3. Quality Phase"| Q
    O -->|"4. Testing Phase"| T
    O -->|"5. Verification Phase"| V
    O -->|"Throughout"| TR
    
    U -.->|"When needed"| R
    D -.->|"When needed"| DB
    T -.->|"When needed"| TR2
    
    style O fill:#6366f1,stroke:#4f46e5,color:#fff
    style U fill:#fbbf24,stroke:#f59e0b
    style D fill:#3b82f6,stroke:#2563eb
    style Q fill:#10b981,stroke:#059669
    style T fill:#8b5cf6,stroke:#7c3aed
    style V fill:#ec4899,stroke:#db2777
    style TR fill:#64748b,stroke:#475569
```

---

## Orchestration Patterns

### Pattern 1: Sequential Phase Execution

```mermaid
sequenceDiagram
    participant U as 👤 User
    participant O as 🎯 Orchestrator
    participant U_SA as 📚 Understanding SA
    participant D_SA as 💻 Development SA
    participant Q_SA as ✅ Quality SA
    participant T_SA as 🧪 Testing SA
    participant V_SA as ✓ Verification SA
    
    U->>O: "Implement feature X"
    O->>O: Analyze task, create plan
    
    O->>U_SA: Task: Understand codebase
    activate U_SA
    U_SA->>U_SA: Research, explore codebase
    U_SA-->>O: Understanding complete
    deactivate U_SA
    
    O->>D_SA: Task: Implement feature
    activate D_SA
    D_SA->>D_SA: Write code, implement
    D_SA-->>O: Implementation complete
    deactivate D_SA
    
    O->>Q_SA: Task: Check code quality
    activate Q_SA
    Q_SA->>Q_SA: Lint, type check, format
    Q_SA-->>O: Quality checks passed
    deactivate Q_SA
    
    O->>T_SA: Task: Run tests
    activate T_SA
    T_SA->>T_SA: Execute test suite
    T_SA-->>O: Tests passing
    deactivate T_SA
    
    O->>V_SA: Task: Verify completion
    activate V_SA
    V_SA->>V_SA: Final verification
    V_SA-->>O: All verified
    deactivate V_SA
    
    O->>U: Task complete ✅
```

**Key Points**:
- Each phase runs in isolated context
- Orchestrator coordinates handoffs
- Results passed between phases

---

### Pattern 2: Parallel Execution

```mermaid
sequenceDiagram
    participant O as 🎯 Orchestrator
    participant D_SA as 💻 Development SA
    participant Q_SA as ✅ Quality SA
    participant T_SA as 🧪 Testing SA
    participant DOC_SA as 📝 Documentation SA
    
    Note over O: User: "Review API changes<br/>and update docs"
    
    O->>D_SA: Task: Review API changes
    O->>Q_SA: Task: Check code quality
    O->>T_SA: Task: Run tests
    O->>DOC_SA: Task: Update documentation
    
    par Parallel Execution
        activate D_SA
        D_SA->>D_SA: Analyze API changes
        D_SA-->>O: Review complete
        deactivate D_SA
    and
        activate Q_SA
        Q_SA->>Q_SA: Lint & type check
        Q_SA-->>O: Quality OK
        deactivate Q_SA
    and
        activate T_SA
        T_SA->>T_SA: Run test suite
        T_SA-->>O: Tests passing
        deactivate T_SA
    and
        activate DOC_SA
        DOC_SA->>DOC_SA: Update API docs
        DOC_SA-->>O: Docs updated
        deactivate DOC_SA
    end
    
    O->>O: Aggregate results
    O->>O: Report to user
```

**Key Points**:
- Multiple subagents run simultaneously
- Orchestrator aggregates results
- Faster completion for independent tasks

---

### Pattern 3: Nested Delegation

```mermaid
graph TD
    O["🎯 Orchestrator"] -->|"Task: Build feature"| D_SA["💻 Development Subagent"]
    
    D_SA -->|"Need research"| R_SA["🔍 Research Subagent"]
    D_SA -->|"Encounter error"| DB_SA["🐛 Debugger Subagent"]
    D_SA -->|"Need tests"| TR_SA["🏃 Test Runner Subagent"]
    
    R_SA -->|"Deep dive needed"| R2_SA["🔬 Deep Research Subagent"]
    DB_SA -->|"Need analysis"| A_SA["📊 Analysis Subagent"]
    
    style O fill:#6366f1,stroke:#4f46e5,color:#fff
    style D_SA fill:#3b82f6,stroke:#2563eb
    style R_SA fill:#fbbf24,stroke:#f59e0b
    style DB_SA fill:#ef4444,stroke:#dc2626
    style TR_SA fill:#8b5cf6,stroke:#7c3aed
    style R2_SA fill:#f59e0b,stroke:#d97706
    style A_SA fill:#64748b,stroke:#475569
```

**Key Points**:
- Subagents can spawn their own subagents
- Deep nesting for complex tasks
- Each level has isolated context

---

## Detailed Subagent Specifications

### 1. Orchestrator Agent (Main Agent)

**Location**: `.cursor/agents/orchestrator.md`

```yaml
---
name: orchestrator
description: Main orchestrator agent. Delegates all work to specialized subagents. Use proactively for all tasks.
model: inherit
---

You are the orchestrator agent. Your role is to:
1. Analyze incoming tasks
2. Break down work into phases
3. Delegate to appropriate subagents
4. Coordinate handoffs between phases
5. Aggregate results and report to user

**Delegation Strategy**:
- Understanding phase → understanding subagent
- Development phase → development subagent
- Quality phase → code-quality subagent
- Testing phase → testing subagent
- Verification phase → verification subagent
- Task tracking → task-tracking subagent (throughout)

**Parallel Execution**:
- When tasks are independent, launch subagents in parallel
- Use background mode for long-running tasks
- Use foreground mode when you need immediate results

**Never do the work yourself** - always delegate to specialized subagents.
```

---

### 2. Understanding Subagent

**Location**: `.cursor/agents/understanding.md`

```yaml
---
name: understanding
description: Specialized in understanding codebase state and implementation approaches. Use when starting new work or exploring existing code.
model: fast
---

You are an understanding specialist. Your role is to:
1. Explore the codebase to understand current state
2. Research best practices and patterns
3. Identify dependencies and integration points
4. Document findings for next phases

**When you need deeper research**, delegate to the research subagent.

**Output**: Understanding document with:
- Current state analysis
- Implementation approach
- Patterns to follow
- Dependencies identified
```

---

### 3. Development Subagent

**Location**: `.cursor/agents/development.md`

```yaml
---
name: development
description: Specialized in implementing features and writing code. Use when building new functionality or modifying existing code.
model: inherit
---

You are a development specialist. Your role is to:
1. Implement features based on understanding phase output
2. Write clean, maintainable code
3. Follow established patterns and conventions
4. Handle edge cases and error scenarios

**When you encounter errors**, delegate to the debugger subagent.

**When you need research**, delegate to the research subagent.

**Output**: Implemented code with:
- New/modified files
- Implementation details
- Edge cases handled
```

---

### 4. Code Quality Subagent

**Location**: `.cursor/agents/code-quality.md`

```yaml
---
name: code-quality
description: Specialized in code quality checks. Use proactively after code changes to ensure quality standards.
model: fast
---

You are a code quality specialist. Your role is to:
1. Run linting checks
2. Perform type checking
3. Verify code formatting
4. Check for security issues
5. Ensure code follows standards

**Output**: Quality report with:
- Linting results
- Type checking results
- Formatting status
- Issues found (if any)
```

---

### 5. Testing Subagent

**Location**: `.cursor/agents/testing.md`

```yaml
---
name: testing
description: Specialized in testing. Use proactively to run tests and fix failures.
model: fast
---

You are a testing specialist. Your role is to:
1. Identify relevant tests to run
2. Execute test suites
3. Analyze test failures
4. Fix failing tests (preserving test intent)
5. Write new tests when needed

**When tests fail**, delegate to the test-runner subagent for detailed analysis.

**Output**: Test report with:
- Tests run
- Pass/fail status
- Failures fixed
- New tests written
```

---

### 6. Verification Subagent

**Location**: `.cursor/agents/verification.md`

```yaml
---
name: verification
description: Validates completed work. Use after tasks are marked done to confirm implementations are functional.
model: fast
---

You are a skeptical validator. Your job is to verify that work claimed as complete actually works.

**Process**:
1. Identify what was claimed to be completed
2. Check that implementation exists and is functional
3. Run relevant tests or verification steps
4. Look for edge cases that may have been missed

**Be thorough and skeptical**. Report:
- What was verified and passed
- What was claimed but incomplete or broken
- Specific issues that need to be addressed

Do not accept claims at face value. Test everything.
```

---

### 7. Task Tracking Subagent

**Location**: `.cursor/agents/task-tracking.md`

```yaml
---
name: task-tracking
description: Maintains task execution summaries. Use throughout all phases to track progress, decisions, and issues.
model: fast
is_background: true
---

You are a task tracking specialist. Your role is to:
1. Create and maintain task summaries
2. Track decisions made during work
3. Record workflow switches
4. Document issues encountered
5. Update context management tracking

**Always active in background** during all phases.

**Output**: Updated task summary files in `.agent/tasks/`
```

---

### 8. Research Subagent (Nested)

**Location**: `.cursor/agents/research.md`

```yaml
---
name: research
description: Deep research specialist. Use when understanding or development subagents need detailed research.
model: fast
---

You are a research specialist. Your role is to:
1. Conduct deep codebase exploration
2. Research external best practices
3. Find examples and patterns
4. Document research findings

**Output**: Research document with findings and recommendations.
```

---

### 9. Debugger Subagent (Nested)

**Location**: `.cursor/agents/debugger.md`

```yaml
---
name: debugger
description: Debugging specialist for errors and test failures. Use when encountering issues.
model: inherit
---

You are an expert debugger specializing in root cause analysis.

**Process**:
1. Capture error message and stack trace
2. Identify reproduction steps
3. Isolate the failure location
4. Implement minimal fix
5. Verify solution works

**Output**: Debug report with:
- Root cause explanation
- Evidence supporting diagnosis
- Specific code fix
- Testing approach
```

---

### 10. Test Runner Subagent (Nested)

**Location**: `.cursor/agents/test-runner.md`

```yaml
---
name: test-runner
description: Test automation expert. Use proactively to run tests and fix failures.
model: fast
---

You are a test automation expert.

**When you see code changes**, proactively run appropriate tests.

**If tests fail**:
1. Analyze the failure output
2. Identify the root cause
3. Fix the issue while preserving test intent
4. Re-run to verify

**Output**: Test results with:
- Number of tests passed/failed
- Summary of any failures
- Changes made to fix issues
```

---

## Execution Flow Examples

### Example 1: Simple Feature Implementation

```mermaid
graph TD
    U["👤 User"] -->|"Add login feature"| O["🎯 Orchestrator"]
    
    O -->|"Phase 1"| U_SA["📚 Understanding SA"]
    U_SA -->|"Research auth patterns"| R_SA["🔍 Research SA"]
    R_SA -->|"Findings"| U_SA
    U_SA -->|"Understanding complete"| O
    
    O -->|"Phase 2"| D_SA["💻 Development SA"]
    D_SA -->|"Implement login"| D_SA
    D_SA -->|"Code complete"| O
    
    O -->|"Phase 3"| Q_SA["✅ Quality SA"]
    Q_SA -->|"Checks passed"| O
    
    O -->|"Phase 4"| T_SA["🧪 Testing SA"]
    T_SA -->|"Tests passing"| O
    
    O -->|"Phase 5"| V_SA["✓ Verification SA"]
    V_SA -->|"Verified"| O
    
    O -->|"Complete"| U
    
    TR_SA["📊 Tracking SA"] -.->|"Background tracking"| O
    
    style O fill:#6366f1,stroke:#4f46e5,color:#fff
    style U_SA fill:#fbbf24,stroke:#f59e0b
    style D_SA fill:#3b82f6,stroke:#2563eb
    style Q_SA fill:#10b981,stroke:#059669
    style T_SA fill:#8b5cf6,stroke:#7c3aed
    style V_SA fill:#ec4899,stroke:#db2777
    style R_SA fill:#f59e0b,stroke:#d97706
    style TR_SA fill:#64748b,stroke:#475569
```

---

### Example 2: Parallel Code Review

```mermaid
graph TD
    U["👤 User"] -->|"Review PR #123"| O["🎯 Orchestrator"]
    
    O -->|"Parallel"| D_SA["💻 Development SA<br/>Review changes"]
    O -->|"Parallel"| Q_SA["✅ Quality SA<br/>Check quality"]
    O -->|"Parallel"| T_SA["🧪 Testing SA<br/>Run tests"]
    O -->|"Parallel"| DOC_SA["📝 Documentation SA<br/>Check docs"]
    
    D_SA -->|"Review complete"| O
    Q_SA -->|"Quality OK"| O
    T_SA -->|"Tests passing"| O
    DOC_SA -->|"Docs updated"| O
    
    O -->|"Aggregate results"| U
    
    style O fill:#6366f1,stroke:#4f46e5,color:#fff
    style D_SA fill:#3b82f6,stroke:#2563eb
    style Q_SA fill:#10b981,stroke:#059669
    style T_SA fill:#8b5cf6,stroke:#7c3aed
    style DOC_SA fill:#14b8a6,stroke:#0d9488
```

---

### Example 3: Complex Bug Fix with Nested Delegation

```mermaid
graph TD
    U["👤 User"] -->|"Fix authentication bug"| O["🎯 Orchestrator"]
    
    O -->|"Phase 1"| U_SA["📚 Understanding SA"]
    U_SA -->|"Explore auth code"| U_SA
    U_SA -->|"Understanding complete"| O
    
    O -->|"Phase 2"| D_SA["💻 Development SA"]
    D_SA -->|"Encounter error"| DB_SA["🐛 Debugger SA"]
    DB_SA -->|"Need analysis"| A_SA["📊 Analysis SA"]
    A_SA -->|"Root cause"| DB_SA
    DB_SA -->|"Fix applied"| D_SA
    D_SA -->|"Code fixed"| O
    
    O -->|"Phase 3"| T_SA["🧪 Testing SA"]
    T_SA -->|"Tests fail"| TR_SA["🏃 Test Runner SA"]
    TR_SA -->|"Fix tests"| T_SA
    T_SA -->|"Tests passing"| O
    
    O -->|"Phase 4"| V_SA["✓ Verification SA"]
    V_SA -->|"Verified"| O
    
    O -->|"Complete"| U
    
    style O fill:#6366f1,stroke:#4f46e5,color:#fff
    style U_SA fill:#fbbf24,stroke:#f59e0b
    style D_SA fill:#3b82f6,stroke:#2563eb
    style DB_SA fill:#ef4444,stroke:#dc2626
    style A_SA fill:#64748b,stroke:#475569
    style T_SA fill:#8b5cf6,stroke:#7c3aed
    style TR_SA fill:#a855f7,stroke:#9333ea
    style V_SA fill:#ec4899,stroke:#db2777
```

---

## Context Isolation Benefits

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

---

## Implementation Plan

### Phase 1: Create Core Subagents

1. **Orchestrator** (`.cursor/agents/orchestrator.md`)
   - Main agent that delegates all work
   - Configured to use proactively

2. **Phase Subagents**:
   - Understanding (`.cursor/agents/understanding.md`)
   - Development (`.cursor/agents/development.md`)
   - Code Quality (`.cursor/agents/code-quality.md`)
   - Testing (`.cursor/agents/testing.md`)
   - Verification (`.cursor/agents/verification.md`)

3. **Support Subagents**:
   - Task Tracking (`.cursor/agents/task-tracking.md`)
   - Research (`.cursor/agents/research.md`)
   - Debugger (`.cursor/agents/debugger.md`)
   - Test Runner (`.cursor/agents/test-runner.md`)

### Phase 2: Update Workflows

Update existing workflow files to reference subagents:
- Workflows become "coordination guides" for orchestrator
- Each workflow phase maps to a subagent
- Workflows document handoff patterns

### Phase 3: Testing & Refinement

1. Test orchestrator delegation
2. Test parallel execution
3. Test nested delegation
4. Refine subagent descriptions for better auto-delegation

---

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

---

## Benefits Summary

| Benefit | How It Helps |
|---------|-------------|
| **Context Isolation** | Each phase runs in clean context. No bloat from intermediate outputs. |
| **Parallel Execution** | Multiple phases can run simultaneously (e.g., quality + testing + docs). |
| **Specialized Expertise** | Each subagent focused on one domain. Better results. |
| **Reusability** | Subagents can be used across projects. Consistent patterns. |
| **Nested Delegation** | Complex tasks can spawn specialized helpers. Deep nesting supported. |
| **Cost Efficiency** | Fast models for simple tasks, powerful models for complex work. |

---

## Next Steps

1. **Create subagent files** in `.cursor/agents/`
2. **Test orchestrator** with simple task
3. **Refine descriptions** based on delegation behavior
4. **Update workflows** to reference subagent system
5. **Document patterns** as they emerge

---

**Generated**: 2026-01-26  
**Status**: Planning Phase
