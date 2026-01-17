---
name: Review Code
description: Standards for Pull Requests, Code Reviews, and Release Versioning.
---

# Review Code

**Purpose**: The Gatekeeper. Ensures quality, security, and standards before code merges to `main`.

## 1. The PR Checklist (The Law)
Before merging, you MUST verify:

1.  **Tests**: `pytest` passes clean?
2.  **Lint**: `smart_lint` passes clean?
3.  **SoC**: `compliance_check` passes clean?
4.  **Docs**: Docstrings and SKILL.md/README.md updated?
5.  **Scope**: Does the PR match the Ticket/Task?

## 2. Code Review Criteria
**Human & Agent Reviewers must check:**
*   **Readability**: Is the code self-documenting?
*   **Simplicity**: Is there a simpler way?
*   **Security**: Any new secrets or unvalidated inputs?
*   **Performance**: Any N+1 queries or massive loops?

## 3. Release Strategy
*   **Versioning**: Semantic Versioning (`MAJOR.MINOR.PATCH`).
    *   **Major**: Breaking changes.
    *   **Minor**: New features (backwards compatible).
    *   **Patch**: Bug fixes.
*   **Changelog**: Update `CHANGELOG.md` with the new version and changes.

## 4. Cognitive Heuristics
**When to use:**
- When opening a Pull Request.
- When reviewing someone else's code.
- When tagging a release.
