# Documentation Maintenance

**Last Updated**: 2026-01-25

Strategy for keeping docs current. Step-by-step workflow → [.agent/workflows/documentation-maintenance.md](../.agent/workflows/documentation-maintenance.md).

## Structure

- **Core docs**: `docs/` only. One source of truth per topic.
- **Workflows**: `.agent/workflows/`
- **Root**: `README.md` only. No other docs in root.

## Lifecycle

1. **During work**: Summaries in root (e.g. `*_SUMMARY.md`) — OK temporarily.
2. **After completion**: Extract to core docs → move to `docs/archive/YYYY-MM/` → **delete root copy** → verify root clean.
3. **Temp patterns**: `*_SUMMARY.md`, `*_REVIEW.md`, `*_GAPS.md`, `*_FIXES.md`.

## When to add docs

- **Yes**: New major feature, new workflow, agent-specific.
- **No**: Belongs in existing doc; temporary summary; duplicate.

## Maintenance

**After major work**: Extract → archive → update core docs → remove outdated. Root check (only `README.md`) → archive/delete summaries → verify links.

## Principles

Single source of truth · Living docs · Temp summaries archived · No duplication.

## Quick links

[ARCHITECTURE](ARCHITECTURE.md) · [DEVELOPMENT](DEVELOPMENT.md) · [TESTING](TESTING.md) · [ROADMAP](ROADMAP.md) · [Agent workflows](../.agent/workflows/agent-development.md)
