---
description: TDD Workflow - Guide for implementing features using Test-Driven Development
---

# TDD Workflow

This workflow guides you through implementing a feature using the mandatory TDD cycle.

## Step 1: Define Schemas
Before writing any logic, define the data structures.
- Create/Update Pydantic models in `schemas/`
- Ensure types are strict and comprehensively defined.

## Step 2: Write Failing Test (Red)
Create a new test file or add a new test case *before* implementing the logic.
- **Location**:
    - Unit: `tests/unit/`
    - Integration: `tests/integration/`
    - Agent: `tests/agents/`
    - Dashboard: `tests/dashboard/`
- **Action**: Write a test that asserts the expected behavior of the new feature.
- **Verify**: Run the test to confirm it fails (Red state).
    ```bash
    uv run pytest path/to/test.py
    ```

## Step 3: Implement Logic (Green)
Write the minimal code necessary to make the test pass.
- Focus *only* on satisfying the test.
- Do not over-engineer.

## Step 4: Verify (Refactor)
Run the test again to confirm it passes.
- **Action**: Refactor code for readability and structure if needed.
- **Verify**: ensure tests still pass.
    ```bash
    uv run pytest path/to/test.py
    ```

## Step 5: Commit
Once the cycle is complete (Red -> Green -> Refactor), commit the changes.
