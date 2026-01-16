---
description: Perform a comprehensive architectural and code-level review as a Senior Architect.
---

# Codebase Review Workflow

Follow this workflow to perform a deep architectural and code-level review of the codebase. You act as a Senior Architect and Principal Software Engineer.

## Phase 1: Context & Architecture Scan

1.  **Identify Project Structure**:
    -   Use `list_dir` on the project root to understand the layout.
    -   Identify key frameworks and languages (e.g., Python/FastAPI, TypeScript/React, Docker).

2.  **Infrastructure & Security Scan**:
    -   Read `Dockerfile`s and `docker-compose.yml` (if present).
    -   **Check for**:
        -   Security risks (e.g., running as root, exposed secrets in env vars).
        -   Scalability issues (e.g., hardcoded resource limits, lack of replicas).
        -   Development vs. Production parity.
    -   **Dependency Check**:
        -   Read `pyproject.toml`, `requirements.txt`, or `package.json`.
        -   Note outdated dependencies or lack of pinned versions.

## Phase 2: Code Quality Audit

3.  **Code Pattern Analysis**:
    -   Use `view_file` to sample critical files (e.g., entry points like `main.py`, `server.py`, or core agent logic).
    -   **Check for**:
        -   **Typing**: Usage of strict typing (e.g., Pydantic models, TypeScript interfaces).
        -   **Error Handling**: Are raw `try/except` blocks swallowing errors? Is there global error handling?
        -   **Configuration**: Are values hardcoded (e.g., `model="gemini-1.5"`) vs. loaded from env/config?

4.  **Static Analysis & Credential Hunt**:
    -   Use `grep_search` to find "TODO", "FIXME", or potential hardcoded secrets (e.g., "API_KEY", "Bearer").
    // turbo
    -   (Optional) If `ruff` or `mypy` is installed, run them via `run_command` to get objective metrics.

## Phase 3: Test Coverage Verification

5.  **Test Suite Audit**:
    -   List the `tests/` directory.
    -   If tests exist, run a sample (`pytest` or `npm test`) to verify they pass.
    -   **Critical**: deeply analyze if tests are *missing* or if they only cover happy paths.

## Phase 4: Report Generation

6.  **Compile Report**:
    -   Create a file named `CODEBASE_REVIEW.md` in the current artifact directory.
    -   Use the following structure:
        -   **Executive Summary**: High-level health check (Red/Amber/Green).
        -   **Architectural Risks**: Infrastructure, security, and scalability findings.
        -   **Code Quality Findings**: Patterns, typing, and specific refactoring recommendations.
        -   **Test Coverage Assessment**: Status of automated testing.
        -   **Action Plan**: Prioritized list of remediations (Immediate, Short-term, Medium-term).

7.  **User Notification**:
    -   Notify the user that the review is complete and point them to the `CODEBASE_REVIEW.md` artifact.
