---
description: TDD implementation workflow - Red-Green-Refactor cycle
---

# TDD Implementation Workflow

**Phase**: Implementation  
**Purpose**: Implement planned work following Test-Driven Development (TDD) principles.

## TDD Cycle

Follow the **Red-Green-Refactor** cycle strictly:

1. **🔴 Red**: Write a failing test
2. **🟢 Green**: Write minimal code to pass the test
3. **🔵 Refactor**: Improve code while keeping tests green

## Steps

### Step 1: Write Failing Tests (Red Phase)

**Action**: Write tests for the planned functionality

**Order** (from planning document):
1. Start with unit tests (Layer 1)
2. Then agent structure tests (Layer 2)
3. Then integration tests (Layer 3) if applicable
4. Then component tests (Layer 4) for frontend
5. Finally E2E tests (Layer 5)

**For Each Test**:
1. Write the test following the test case from planning
2. Ensure test fails for the right reason (not a syntax error)
3. Run test to confirm it fails (Red phase)

**Commands**:
```bash
# Run specific test file
uv run pytest path/to/test_file.py -v

# Run tests for specific agent
make test-agent AGENT=agent_name

# Run frontend tests
make frontend-test
```

**Output**: All tests written and failing (Red)

---

### Step 2: Implement Minimal Code (Green Phase)

**Action**: Write the minimal code needed to make tests pass

**Principle**: Write the simplest code that makes the test pass. Don't over-engineer.

**For Each Test**:
1. Implement minimal functionality
2. Run test to confirm it passes
3. Move to next test

**Commands**:
```bash
# Run tests to check progress
uv run pytest path/to/test_file.py -v

# Run all tests
make test-fast
```

**Output**: All tests passing (Green)

---

### Step 3: Refactor (Blue Phase)

**Action**: Improve code structure while keeping tests green

**Refactoring Guidelines**:
1. Improve code structure
2. Remove duplication
3. Improve naming
4. Add documentation
5. Optimize performance
6. **Always run tests after refactoring**

**After Each Refactor**:
```bash
# Verify tests still pass
uv run pytest path/to/test_file.py -v
```

**Output**: Clean, well-structured code with all tests passing

---

### Step 4: Follow Code Standards

**Action**: Ensure code follows project standards

**Standards to Follow**:
- Review `docs/STANDARDS.md`
- Follow Python/TypeScript conventions
- Use established patterns from codebase
- Follow naming conventions
- Add appropriate documentation

**Output**: Code that follows all standards

---

### Step 5: Update Documentation

**Action**: Update documentation as code changes

**Tasks**:
1. Update code comments
2. Update docstrings
3. Update README files if needed
4. Update API documentation if interfaces change

**Output**: Documentation updated to match implementation

---

## Implementation Order

Follow the implementation checklist from planning:

1. **Write Tests First** (Red)
   - Unit tests
   - Integration tests
   - Component tests
   - E2E tests

2. **Implement Functionality** (Green)
   - Component by component
   - Make each test pass before moving on

3. **Refactor** (Blue)
   - After each component
   - After all components complete

4. **Update Documentation**
   - As you implement
   - Final review at end

---

## Testing During Implementation

**Continuous Testing**:
- Run tests frequently (after each small change)
- Use test-driven approach (test first, then code)
- Fix tests immediately if they break

**Commands**:
```bash
# Quick test run (fast feedback)
make test-fast

# Full test run
make test

# Specific test
uv run pytest path/to/test_file.py::test_function -v
```

---

## Code Quality During Implementation

**Continuous Quality Checks**:
- Run linting frequently
- Fix issues immediately
- Keep code clean as you go

**Commands**:
```bash
# Lint and format
make lint

# Type check
uv run mypy .
```

---

## Handling Issues During Implementation

**If You Encounter Issues**:

1. **Document in `.agent/issues.md`**:
   - Issue description
   - Impact
   - Proposed solution

2. **Assess Impact**:
   - Is it a wider architectural issue?
   - Does it require refactoring?
   - Can it be fixed locally?

3. **Take Action**:
   - If wider issue: Document and plan refactor
   - If local issue: Fix and continue

---

## Exit Criteria

Implementation is complete when:

- ✅ All planned test cases written and passing
- ✅ All functionality implemented
- ✅ Code refactored and clean
- ✅ Code follows all standards
- ✅ Documentation updated
- ✅ No unresolved issues
- ✅ Ready for code quality phase

---

## Next Phase

After Implementation, proceed to: **[Code Quality Workflow](code-quality-workflow.md)**
