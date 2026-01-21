---
name: Skill Review Protocol
description: Pre-update review before modifying any skill file
---

# Skill Review Protocol

## Purpose
Gate all skill modifications with a structural review. Ensures scalability and prevents skill sprawl.

## Automation Level
**FULLY AUTOMATED** - Agent runs all checks autonomously and proceeds based on heuristics. No user approval required for standard cases. Only escalate to user if:
- Proposing a new SDLC category
- Skill refactor affects 5+ files
- Conflicting patterns detected in Knowledge Base
- **Platform-level design issue detected** (4+ occurrences or core abstraction affected)

## When to Trigger

| Event | Action |
|-------|--------|
| Issue marked for skill update | Run review before modifying |
| New skill file proposed | Run review before creating |
| Skill file exceeds 100 lines | Trigger split review |
| New SDLC pattern identified | Evaluate for new category |

## Pre-Update Checklist

Before modifying ANY skill file, complete this checklist:

### 1. Category Fit
```
□ Does this update belong in the target skill?
□ Is the skill file the most specific location for this content?
□ Could this be tech-specific (→ stacks/) vs platform-wide (→ sdlc/)?
```

### 2. Scope Check
```
□ Will the skill exceed 100 lines after update?
  → YES: Consider splitting into sub-skills
□ Does the skill already cover 5+ distinct topics?
  → YES: Consider refactoring to sub-directory
```

### 3. SDLC Fit
```
□ Is this a fundamentally new lifecycle activity?
  → Has 3+ distinct use cases? → Propose new branch
  → Otherwise: Add as sub-section in existing branch
□ Potential new branches to consider:
  - document/  → Dedicated documentation generation
  - maintain/  → Dependency management, upgrades
  - optimize/  → Performance tuning, profiling
  - migrate/   → Refactoring, major version upgrades
```

### 4. Cross-Reference Impact
```
□ Will other skills need updating after this change?
□ Does this change affect smart loading order?
□ Will product manifests need updates?
```

### 5. Knowledge Base Sync
```
□ Does this change require Knowledge Item updates?
□ Are there conflicting patterns in existing KIs?
```

### 6. Design Impact Analysis
Issues often indicate deeper architectural problems. Before applying fixes:

```
□ Is this a symptom of a design flaw?
  → Look for: repeated workarounds, similar issues in other modules
□ Are there other modules using the same pattern?
  → Search for: identical imports, similar class structures, shared utilities
□ Should the fix be applied at:
  - Component level (just this module)
  - Domain level (all modules in this domain)
  - Platform level (architectural change across all domains)
```

**Decision Matrix:**

| Signal | Scope | Action |
|--------|-------|--------|
| Single occurrence, unique context | Component | Fix locally |
| 2-3 occurrences, similar pattern | Domain | Fix all + update domain skill |
| 4+ occurrences OR core abstraction | Platform | Architectural review required |

**Questions to Ask:**
1. "Would a new developer hit this same issue?"
2. "If I fix this here, will it break elsewhere?"
3. "Is there a shared abstraction that should handle this?"

## Scaling Heuristics

Automated triggers for deeper review:

| Metric | Threshold | Action |
|--------|-----------|--------|
| Skill line count | > 100 | Split into sub-skills |
| Skills per category | > 5 files | Propose category refactor |
| Cross-references | > 3 skills | Document dependency map |
| Product overrides | > 3 | Consider platform promotion |

## New Category Decision Tree

```
Is this a fundamentally new lifecycle activity?
│
├─ YES: Does it have 3+ distinct use cases?
│   │
│   ├─ YES: Does it cross-cut multiple existing branches?
│   │   │
│   │   ├─ YES → Propose as new sdlc/ branch
│   │   │   - Create directory structure
│   │   │   - Add to router.md routing table
│   │   │   - Update GEMINI.md branch list
│   │   │
│   │   └─ NO → Add as sub-directory in closest branch
│   │       - Example: sdlc/develop/migrations/
│   │
│   └─ NO → Add as section in existing branch SKILL.md
│
└─ NO → Extend existing branch skill
```

## Review Output Format

After completing review, document findings:

```markdown
## Skill Review - [Date]

**Target**: `path/to/SKILL.md`
**Change Type**: extend | split | new-category | refactor

### Checklist Results
- Category Fit: ✓/✗
- Scope Check: ✓/✗
- SDLC Fit: ✓/✗
- Cross-Reference: ✓/✗
- KB Sync: ✓/✗
- Design Impact: component | domain | platform

### Decision
[Proceed | Split Required | New Category Proposed | Blocked]

### Notes
[Any relevant context or concerns]
```

## Integration Points

1. **Issue Tracking**: `issues.md` references this before skill updates
2. **Auto-Documentation**: `document.md` logs review outcomes
3. **Router**: New categories require `router.md` updates
4. **GEMINI.md**: New branches require entry point updates
