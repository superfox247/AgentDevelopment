---
description: Discovery phase workflow - understand current state, requirements, and context
---

# Discovery Workflow

**Phase**: Pre-Implementation  
**Purpose**: Understand the current state, requirements, and context before starting work.

## Objectives

1. Understand what currently exists
2. Identify relevant files and components
3. Understand architecture and patterns
4. Identify dependencies and related work
5. Review existing issues and system status

## Steps

### Step 1: Review Documentation

**Action**: Review all relevant documentation in `docs/`

**Files to Review**:
- `docs/ARCHITECTURE.md` - System architecture
- `docs/DEVELOPMENT.md` - Development practices
- `docs/STANDARDS.md` - Coding standards
- `docs/TESTING.md` - Testing strategy
- `docs/DEPLOYMENT.md` - Deployment guide
- `docs/CONFIG_FILES.md` - Configuration reference
- Any feature-specific documentation

**Output**: List of relevant documentation and key points

---

### Step 2: Codebase Exploration

**Action**: Search and explore the codebase to understand current implementation

**Tasks**:
1. Search for related code using semantic search
2. Identify relevant modules, classes, functions
3. Understand code organization and patterns
4. Review similar implementations

**Tools**:
- Codebase semantic search
- File system exploration
- Grep for specific patterns

**Output**: 
- List of relevant files
- Understanding of code structure
- Patterns identified

---

### Step 3: Architecture Understanding

**Action**: Understand how components fit together

**Tasks**:
1. Review architecture diagrams
2. Understand component interactions
3. Identify integration points
4. Understand data flow

**Output**: Architecture understanding document

---

### Step 4: Review Issues and System Status

**Action**: Check for existing issues and system performance

**Files to Review**:
- `.agent/issues.md` - Current issues
- `.agent/system-tracking.md` - Runs, lessons

**Tasks**:
1. Review open issues
2. Check if work relates to existing issues
3. Review system performance notes
4. Identify any known problems

**Output**: 
- List of related issues
- System status understanding

---

### Step 5: Dependency Analysis

**Action**: Identify dependencies and related work

**Tasks**:
1. Identify code dependencies
2. Identify related features
3. Check for blocking dependencies
4. Identify parallel work opportunities

**Output**: Dependency map

---

## Discovery Document Template

Create a discovery document with:

```markdown
# Discovery: [Feature/Task Name]

## Current State
- What exists now
- Relevant files identified
- Architecture understanding

## Requirements
- What needs to be done
- User stories or requirements

## Relevant Files
- List of files to modify/create
- Related components

## Architecture Context
- How this fits into the system
- Integration points
- Data flow

## Dependencies
- Code dependencies
- Related features
- Blocking items

## Related Issues
- Links to related issues
- Known problems

## System Status
- Any relevant system tracking notes
```

---

## Exit Criteria

Discovery is complete when:

- ✅ All relevant documentation reviewed
- ✅ Codebase explored and understood
- ✅ Architecture context clear
- ✅ Relevant files identified
- ✅ Dependencies mapped
- ✅ Related issues reviewed
- ✅ Discovery document created

---

## Next Phase

After Discovery, proceed to: **[Research Workflow](research-workflow.md)**
