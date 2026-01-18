---
name: Manage Git
description: Defines the standard Git workflow, branching strategy, and commit conventions.
---

# Manage Git

**Purpose**: Standardization of version control operations to ensure history is clean, readable, and revertible.

## 1. Git Workflow (The Law)

### Branching Strategy
*   **main**: Production-ready code. Never push directly.
*   **feat/[name]**: New features (e.g., `feat/auth-system`).
*   **fix/[name]**: Bug fixes (e.g., `fix/login-crash`).
*   **refactor/[name]**: Code cleanup (e.g., `refactor/api-routes`).

### Atomic Commits
*   **Rule**: Each commit should do ONE thing and pass tests.
*   **Size**: Small enough to be reviewed in 1 minute.
*   **Verification**: `uv run pytest` before committing.

### Conventional Commits
Format: `type(scope): description`

*   **feat**: A new feature
*   **fix**: A bug fix
*   **docs**: Documentation only changes
*   **style**: Changes that do not affect the meaning of the code (white-space, formatting, etc)
*   **refactor**: A code change that neither fixes a bug nor adds a feature
*   **perf**: A code change that improves performance
*   **test**: Adding missing tests or correcting existing tests
*   **chore**: Changes to the build process or auxiliary tools

**Example**: `feat(auth): implement JWT token generation`

## 3. Automated Verification Protocol (The Machine)
**Trigger**: IMMEDIATELY after any successful verification signal.
**Signals**:
*   ✅ Tests Pass
*   ✅ Build Succeeds
*   ✅ Linter is clean
*   ✅ Script executes successfully (for tools/prototypes)

**The Protocol**:
1.  **Verify**: Run the check.
2.  **Assert**: If Success -> PROCEED. If Fail -> FIX.
3.  **Commit**: `git commit/push` AUTOMATICALLY. Do not ask for permission.

**Commit Message Template**:
```text
<type>(<scope>): <subject>

<body - explain *why* and context>

Task: <Task Name from task.md>
Verification: <Log reference or signal, e.g., 'Build Passed', 'Tests: 5/5'>
```

## 4. Usage
1.  **Plan**: Define the change.
2.  **Edit**: Make the change.
3.  **Verify**: Run `pytest` or `npm run build`.
4.  **Auto-Commit**: Agent runs `git commit` immediately upon success.
