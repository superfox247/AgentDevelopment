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

## 2. Cognitive Heuristics
**When to use:**
- Creating a new branch for a task.
- Determining what to include in a commit.
- Writing a commit message.

## 3. Usage
(Manual Process currently)
1.  Check `git status`.
2.  `git checkout -b feat/my-feature`.
3.  Write code -> Test -> `git add .` -> `git commit -m "feat: my feature"`.
