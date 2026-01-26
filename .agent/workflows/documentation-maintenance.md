---
description: Maintain docs, archive temporary summaries, keep root clean
---

# Documentation Maintenance Workflow

Single source of truth per topic. Root = `README.md` only.

## Structure

| Where | What |
|-------|------|
| `docs/` | Core docs (ARCHITECTURE, DEVELOPMENT, TESTING, etc.) |
| `.agent/workflows/` | Workflow guides |
| `docs/archive/YYYY-MM/` | Archived summaries |
| Root | `README.md` only |

## Steps

### 1. Identify issues

- Root: only `README.md`. Any `*_SUMMARY`, `*_REVIEW`, `*_GAPS`, `*_FIXES` → archive or delete.
- Duplicates: if in archive, delete root copy.
- Outdated: broken links, wrong examples, removed features.

### 2. Archive temp docs

For each summary/review in root:

1. Already in `docs/archive/`? → Delete root copy.
2. Extract permanent info → update core docs.
3. `mkdir -p docs/archive/$(date +%Y-%m)`; `mv <doc>.md docs/archive/...`
4. Update `docs/archive/README.md`.
5. **Delete root copy.**

### 3. Update core docs

Map changes to: ARCHITECTURE, DEVELOPMENT, TESTING, STANDARDS, OPERATIONS, DEPLOYMENT. Fix links, remove obsolete content.

### 4. Consolidate duplicates

Prefer `docs/` over root, workflows over scattered docs. Merge best content, delete or archive rest.

### 5. Verify

Links work; README index accurate; root clean.

## Common tasks

**Archive summary**: Extract → archive → delete root → verify.

**Consolidate**: Pick canonical doc → merge → delete duplicates.

**Update outdated**: Edit sections → fix examples → remove old refs.

## Checklist

- [ ] Root = `README.md` only
- [ ] Summaries archived, root copies deleted
- [ ] Core docs updated
- [ ] No duplicates; links OK
