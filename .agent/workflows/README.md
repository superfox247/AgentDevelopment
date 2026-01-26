# Agentic Development Workflows

This directory contains workflows for agentic development. These workflows can be chained together, run in parallel, or executed sequentially by different agents.

## Main Workflow

**[Main Development Workflow](main-development.md)** - The primary entry point for all development work.

This workflow orchestrates the complete development lifecycle:
1. Discovery
2. Research
3. Planning
4. Implementation (TDD)
5. Code Quality
6. Testing
7. Verification

## Workflow Structure

### Pre-Implementation Workflows

1. **[Discovery Workflow](discovery-workflow.md)**
   - Understand current state
   - Identify relevant files
   - Review architecture
   - Check issues and system status

2. **[Research Workflow](research-workflow.md)**
   - Research best practices
   - Review patterns
   - Security considerations
   - Edge cases

3. **[Planning Workflow](planning-workflow.md)**
   - Update documentation
   - Design implementation
   - Define test cases (TDD)
   - Create checklist

### Implementation Workflows

4. **[TDD Implementation Workflow](tdd-implementation-workflow.md)**
   - Red-Green-Refactor cycle
   - Write tests first
   - Implement functionality
   - Refactor code

5. **[Code Quality Workflow](code-quality-workflow.md)**
   - Linting and formatting
   - Type checking
   - Security checks
   - Clean builds
   - Clean command outputs

6. **[Testing Workflow](testing-workflow.md)**
   - Run all test layers
   - Review logs
   - Analyze failures
   - Fix issues

7. **[Verification Workflow](verification-workflow.md)**
   - Reset environment
   - Start full stack
   - Verify services
   - E2E tests
   - Manual verification

## Workflow Execution

### Sequential Execution (Default)

Run workflows one after another:

```
Discovery → Research → Planning → Implementation → Quality → Testing → Verification
```

### Parallel Execution

Some workflows can run in parallel:
- Research can run while reviewing discovery
- Code quality can run while writing tests
- Multiple test layers can run in parallel

### Branching

Workflows can branch based on findings:
- Discovery finds major issue → Branch to refactor workflow
- Testing finds architectural issue → Branch to refactor planning
- Quality finds pattern issue → Branch to update standards

## Supporting Documents

### Issue Tracking

**[`.agent/issues.md`](../issues.md)** - Tracks issues encountered during development.

### System Tracking & Lessons

**[`.agent/system-tracking.md`](../system-tracking.md)** - Runs (what worked, issues, suggestions); durable lessons.

## Quick Start

1. **Start with Main Development Workflow**:
   - Review [main-development.md](main-development.md)
   - Follow the phases in order

2. **For Specific Tasks**:
   - Use individual workflow documents
   - Follow the steps in each workflow

3. **Track progress**: Issues → `.agent/issues.md`; runs & lessons → `.agent/system-tracking.md`

## Workflow Principles

1. **Documentation First**: Update documentation to reflect planned state
2. **TDD Approach**: Write tests before implementation
3. **Clean Outputs**: All commands must produce clean output (no warnings)
4. **Log Visibility**: All logs must be easy to view and understand
5. **Issue Tracking**: Document all issues encountered
6. **Continuous improvement**: Track runs in system-tracking; refine workflows from suggestions

## Integration with Existing Workflows

These workflows integrate with:
- **[Agent Development Workflow](agent-development.md)** - For agent-specific work
- **[Agent Testing Checklist](agent-testing-checklist.md)** - For testing agents
- **[Documentation Maintenance](documentation-maintenance.md)** - For documentation work

## Best Practices

1. **Always start with Discovery**: Understand what exists before making changes
2. **Research before Planning**: Know best practices before designing
3. **Plan before Implementing**: Have a clear plan with test cases
4. **Test as you go**: Run tests frequently during implementation
5. **Quality continuously**: Fix issues immediately, don't accumulate
6. **Verify completely**: Ensure everything works in deployed environment
7. **Track everything**: Document issues and system performance
