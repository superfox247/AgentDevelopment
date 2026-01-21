---
name: Auto-Documentation
description: Automatically documents patterns, decisions, and artifacts
---

# Auto-Documentation

## Purpose
Every skill execution should update the knowledge base. No orphan artifacts.

## Triggers

| Event | Action |
|-------|--------|
| File created | Log to knowledge/{scope}/artifacts.md |
| Pattern used | Update knowledge/{scope}/patterns.md |
| Decision made | Log to knowledge/{scope}/decisions.md |
| Error resolved | Update knowledge/{scope}/troubleshooting.md |

## Knowledge Scope

```
knowledge/
├── platform/           # Cross-product learnings
│   ├── patterns.md
│   ├── decisions.md
│   └── troubleshooting.md
└── products/
    ├── course_creator/
    └── dashboard/
```

## Documentation Format

```markdown
## [Date] - [Topic]

**Context**: Why this was needed
**Decision**: What was decided
**Outcome**: Result/pattern established
**Files**: Links to relevant files
```

## Auto-Sync Protocol

1. **On Skill Complete**: Extract key learnings
2. **On Error Resolution**: Document fix
3. **On New Pattern**: Add to patterns.md
4. **Weekly**: Prune stale entries

## Linking

- Skills reference knowledge: `See: knowledge/platform/patterns.md#error-boundaries`
- Knowledge references skills: `Source: sdlc/develop/SKILL.md`

## No Orphans Rule

Every created artifact must be:
1. Logged in knowledge
2. Referenced from at least one skill or doc
3. Tested (if code)
