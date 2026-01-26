---
description: Planning phase workflow - create detailed implementation plan with TDD test cases
---

# Planning Workflow

**Phase**: Pre-Implementation  
**Purpose**: Create a detailed plan for implementation, including TDD test cases.

## Objectives

1. Update documentation to reflect planned changes
2. Design the implementation approach
3. Define test cases (TDD - tests first)
4. Identify dependencies and integration points
5. Plan refactoring if needed
6. Create implementation checklist

## Steps

### Step 1: Update Documentation

**Action**: Update relevant documentation to add/remove features as planned

**Principle**: Documentation is the source of truth. Update it first to reflect what will exist.

**Tasks**:
1. Review discovery and research documents
2. Identify documentation that needs updates
3. Add new features to relevant docs
4. Remove deprecated features from docs
5. Update architecture docs if structure changes
6. Update API docs if interfaces change

**Files to Update**:
- `docs/ARCHITECTURE.md` - If architecture changes
- `docs/DEVELOPMENT.md` - If dev process changes
- `docs/STANDARDS.md` - If standards change
- Feature-specific documentation
- README files if needed

**Output**: Updated documentation reflecting planned state

---

### Step 2: Design Implementation Approach

**Action**: Design how the implementation will work

**Tasks**:
1. Design component structure
2. Define interfaces and APIs
3. Plan data flow
4. Design error handling
5. Plan integration points
6. Design testing strategy

**Output**: Implementation design document

---

### Step 3: Define Test Cases (TDD)

**Action**: Define all test cases before implementation

**TDD Principle**: Write tests first, then implement to pass them.

**Test Layers** (from `docs/TESTING.md`):

1. **Layer 1: Unit Tests** (Colocated)
   - Test individual functions/classes
   - Location: Next to source files (`test_*.py`)
   - Define: Function inputs, expected outputs, edge cases

2. **Layer 2: Agent Structure Tests**
   - Test agent configuration and tools
   - Location: `agents/<agent>/tests/`
   - Define: Agent behavior, tool functionality

3. **Layer 3: Integration Tests** (if applicable)
   - Test service boundaries
   - Location: `tests/integration/`
   - Define: Component interactions

4. **Layer 4: Component Tests** (Frontend)
   - Test UI components
   - Location: `frontend/tests/components/`
   - Define: Component behavior, user interactions

5. **Layer 5: E2E Tests**
   - Test full user journeys
   - Location: `frontend/tests/e2e/`
   - Define: User workflows, system integration

**Test Case Template**:
```markdown
## Test: [Test Name]

**Layer**: [1-5]
**Location**: [File path]
**Description**: [What it tests]

**Given**: [Initial state]
**When**: [Action performed]
**Then**: [Expected result]

**Edge Cases**:
- Edge case 1: Expected behavior
- Edge case 2: Expected behavior

**Security Considerations**:
- Security test 1: Expected behavior
```

**Output**: Complete test case definitions for all layers

---

### Step 4: Identify Dependencies and Integration Points

**Action**: Map out dependencies and integration requirements

**Tasks**:
1. List code dependencies
2. Identify API integration points
3. Plan database/storage changes
4. Identify external service dependencies
5. Plan Docker/service changes

**Output**: Dependency and integration map

---

### Step 5: Refactoring Assessment

**Action**: Determine if refactoring is needed

**Based on**:
- Discovery findings
- Research insights
- Test case requirements
- Architecture needs

**If Refactoring Needed**:
1. Document current issues
2. Design refactoring approach
3. Plan refactoring steps
4. Update test cases for refactored code
5. Add to implementation checklist

**Output**: Refactoring plan (if needed)

---

### Step 6: Create Implementation Checklist

**Action**: Create step-by-step implementation checklist

**Checklist Should Include**:
1. Test cases to write (TDD - write tests first)
2. Code to implement (by component)
3. Documentation updates
4. Integration steps
5. Refactoring steps (if any)
6. Quality checks
7. Testing steps

**Format**:
```markdown
## Implementation Checklist

### Phase 1: Tests (TDD - Red)
- [ ] Write failing unit test 1
- [ ] Write failing unit test 2
- [ ] Write failing integration test 1
- [ ] Write failing E2E test 1

### Phase 2: Implementation (Green)
- [ ] Implement component 1
- [ ] Implement component 2
- [ ] Make tests pass

### Phase 3: Refactor (Blue)
- [ ] Refactor component 1
- [ ] Ensure tests still pass

### Phase 4: Integration
- [ ] Integrate with service A
- [ ] Integrate with service B

### Phase 5: Quality
- [ ] Run linting
- [ ] Run type checking
- [ ] Fix all warnings

### Phase 6: Testing
- [ ] Run unit tests
- [ ] Run integration tests
- [ ] Run E2E tests
- [ ] Review logs

### Phase 7: Verification
- [ ] Reset dev environment
- [ ] Verify all services healthy
- [ ] Manual verification
```

**Output**: Detailed implementation checklist

---

## Planning Document Template

Create a planning document with:

```markdown
# Planning: [Feature/Task Name]

## Documentation Updates
- [ ] Doc 1: Changes made
- [ ] Doc 2: Changes made

## Implementation Design
- Component structure
- Interfaces and APIs
- Data flow
- Error handling

## Test Cases

### Layer 1: Unit Tests
- Test 1: Description
- Test 2: Description

### Layer 2: Agent Structure Tests
- Test 1: Description

### Layer 3: Integration Tests
- Test 1: Description

### Layer 4: Component Tests
- Test 1: Description

### Layer 5: E2E Tests
- Test 1: Description

## Dependencies
- Dependency 1: Integration approach
- Dependency 2: Integration approach

## Refactoring Plan (if needed)
- Current issue
- Refactoring approach
- Steps

## Implementation Checklist
[See Step 6 above]
```

---

## Exit Criteria

Planning is complete when:

- ✅ Documentation updated to reflect planned state
- ✅ Implementation design complete
- ✅ All test cases defined (TDD approach)
- ✅ Dependencies mapped
- ✅ Refactoring planned (if needed)
- ✅ Implementation checklist created
- ✅ Ready for implementation

---

## Next Phase

After Planning, proceed to: **[TDD Implementation Workflow](tdd-implementation-workflow.md)**
