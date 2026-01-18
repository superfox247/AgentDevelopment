---
name: Develop Dashboard
description: Automated skill for building and extending the Antigravity Dashboard with premium UI components.
---

# Develop Dashboard

Use this skill to manage the lifecycle of dashboard development, ensuring all new features adhere to the "Rich Aesthetics" design system and pass verification checks.

## 1. Cognitive Heuristics
**When to use:** 
- When the user requests a new UI component or page.
- When verifying the integrity of the dashboard frontend (lint/build).
- When modifying existing components to ensure they meet accessibility and design standards.

**Validation:** 
- New components must export a function matching the filename.
- Code must pass `npm run lint` and `npm run build`.
- Visuals must use `glass-panel`, `glass-card`, and Tailwind utility classes.

## 2. Load Context
- `.agent/skills/develop_dashboard/develop_dashboard.py`: The automation script.
- `tools/dashboard/src/components/`: Directory for React components.

## 3. Usage (Automated)

### Create a New Component
Generates a standard "Glassmorphism" component template.
```bash
uv run .agent/skills/develop_dashboard/develop_dashboard.py --component [ComponentName]
```
*Example:*
```bash
uv run .agent/skills/develop_dashboard/develop_dashboard.py --component SettingsView
```

### Verify Dashboard Health
Runs `eslint` and `vite build` to ensure no regressions.
```bash
uv run .agent/skills/develop_dashboard/develop_dashboard.py --verify
```

## 3. Immediate Follow-up
1.  If creating a component, import and add it to `tools/dashboard/src/App.jsx` routing/navigation.
2.  Run verification to ensure the new code is clean.
