---
description: Research phase workflow - identify best practices, patterns, and solutions
---

# Research Workflow

**Phase**: Pre-Implementation  
**Purpose**: Research best practices, patterns, and solutions for the work to be done.

## Objectives

1. Identify industry best practices
2. Review patterns and conventions
3. Research security considerations
4. Identify edge cases
5. Find examples and references

## Steps

### Step 1: Technology Stack Research

**Action**: Research best practices for each technology in the stack

**Technologies to Research**:
- Python (FastAPI, Pydantic, etc.)
- TypeScript/React (Vite, React Query, etc.)
- Docker and Docker Compose
- Testing frameworks (pytest, Playwright, Vitest)
- ADK (Google Agent Development Kit)

**Tasks**:
1. Research official documentation
2. Review community best practices
3. Check for security best practices
4. Review performance considerations

**Output**: Best practices document for each technology

---

### Step 2: Codebase Pattern Review

**Action**: Review existing patterns in the codebase

**Tasks**:
1. Review similar implementations
2. Identify established patterns
3. Review coding conventions
4. Check testing patterns

**Files to Review**:
- Similar feature implementations
- Test files for patterns
- Configuration files
- Documentation for patterns

**Output**: Pattern reference document

---

### Step 3: Security Research

**Action**: Research security considerations

**Tasks**:
1. Review security best practices
2. Identify potential vulnerabilities
3. Research authentication/authorization patterns
4. Review data validation approaches
5. Check for injection risks
6. Review CORS and API security

**Output**: Security considerations document

---

### Step 4: Edge Cases and Error Handling

**Action**: Research edge cases and error handling patterns

**Tasks**:
1. Identify edge cases for the feature
2. Review error handling patterns in codebase
3. Research industry error handling best practices
4. Plan for failure scenarios
5. Review logging and monitoring approaches

**Output**: Edge cases and error handling plan

---

### Step 5: Examples and References

**Action**: Find examples and references

**Tasks**:
1. Find similar implementations in codebase
2. Research external examples
3. Review documentation examples
4. Check for reference implementations

**Output**: Examples and references list

---

## Research Document Template

Create a research document with:

```markdown
# Research: [Feature/Task Name]

## Best Practices

### Technology Stack
- [Technology 1]: Best practices
- [Technology 2]: Best practices
- ...

### Patterns
- Pattern 1: Description and usage
- Pattern 2: Description and usage
- ...

## Security Considerations
- Security concern 1: Mitigation approach
- Security concern 2: Mitigation approach
- ...

## Edge Cases
- Edge case 1: Handling approach
- Edge case 2: Handling approach
- ...

## Error Handling
- Error type 1: Handling strategy
- Error type 2: Handling strategy
- ...

## Examples and References
- Example 1: Link/description
- Example 2: Link/description
- ...

## Patterns to Follow
- Pattern from codebase: Location and usage
- Pattern from industry: Description
- ...
```

---

## Integration with Standards

**Action**: Ensure research aligns with project standards

**Review**:
- `docs/STANDARDS.md` - Coding standards
- `docs/TESTING.md` - Testing standards
- `docs/DEVELOPMENT.md` - Development practices

**Output**: Confirmation that research aligns with standards

---

## Exit Criteria

Research is complete when:

- ✅ Best practices identified for all technologies
- ✅ Patterns reviewed and selected
- ✅ Security considerations documented
- ✅ Edge cases identified
- ✅ Error handling approach defined
- ✅ Examples and references collected
- ✅ Research document created
- ✅ Alignment with project standards confirmed

---

## Next Phase

After Research, proceed to: **[Planning Workflow](planning-workflow.md)**
