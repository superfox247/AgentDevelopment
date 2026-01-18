---
name: review_code_practices
description: Review code implementation against best practices and library documentation.
---

# Review Code Practices
This skill orchestrates a deep, research-backed code review process. It mandates a rigorous "Research -> Plan -> Execute" workflow to ensure code is reviewed against *current* library standards and *verified* internal patterns.

## Critical Philosophy
-   **Living Documentation**: Pattern artifacts (`patterns/*.md`) are the Source of Truth. If the code proves the doc wrong (or outdated), **UPDATE THE DOC**.
-   **Deep Discovery**: Don't just check `package.json`. Check Docker, Python, and internal framework usage.
-   **Ad-Hoc Research**: If you are unsure during a review, **STOP**, research, and update the pattern doc immediately.

## Workflow

### Phase 1: Deep Discovery & Living Documentation
**Goal**: Identify the *entire* stack (including hidden internal frameworks) and ensure our knowledge base is current.

1.  **Full Stack Scan (Automated)**:
    -   **Run**: `python .agent/skills/review_code_practices/scripts/deep_discover.py`
    -   **Analyze Output**: Review the summary of frameworks, libraries, and Docker base images.
    -   **Internal Frameworks**: Look for repeated imports (e.g., `from adk import agent`) in the file list if not caught by discovery.

2.  **Pattern Verification (The "Living Doc" Protocol)**:
    -   For EACH identified technology (e.g., "Docker", "ADK", "React"):
        -   **Check**: Does `patterns/<tech>.md` exist in `<appDataDir>/.../patterns/`?
        -   **Verify**: Is it up to date? (e.g., If we see `React 19` code but the doc says `React 18`, **UPDATE THE DOC**).
        -   **Research**: If missing or outdated, spawn `search_web` calls to find the *current* best practices.
    -   **Create/Update Artifact**: `patterns/<technology>_v<version>.md`.

### Phase 2: Planning & Orchestration
**Goal**: Deconstruct the review into manageable chunks.

3.  **Create Master Checklist**:
    -   Create/Update `review_checklist.md` (Use `resources/checklist_template.md` as a base).
    -   **Deconstruct**: List every file, component, or module to be reviewed.
    -   **Group**: Organize by type (e.g., "UI Components", "State Logic", "API Handlers", "Docker Config").

### Phase 3: Execution (Iterative & Dynamic)
**Goal**: Review files. **Crucially: If you see something new, STOP and Research.**

4.  **Review Loop**:
    -   **Select**: Pick a file from `review_checklist.md`.
    -   **Check History**: Run `python .agent/skills/review_code_practices/scripts/review_tracker.py get --file <filename>` to see past issues.
    -   **Context Loading**: Load relevant `patterns/*.md`.
    -   **Analyze & Verify**: Check code against patterns.
    -   **🚨 Ad-Hoc Research Trigger**:
        -   *Trigger*: You see a pattern usage you are unsure about.
        -   *Action*: **STOP**. Run a search. **UPDATE** the relevant `patterns/*.md`. **RESUME**.
    -   **Record**: 
        -   Update `review_checklist.md`.
        -   Append findings to `review_findings.md`.
        -   **LOG RESULT**: Run `python .agent/skills/review_code_practices/scripts/review_tracker.py log --file <filename> --status <PASSED/FAILED/WARNING> --notes "..."`

### Phase 4: Reporting
5.  **Final Report**:
    -   Compile `review_findings.md`.
    -   Categorize: 🔴 Critical, 🟡 Warning, 🔵 Nitpick.
