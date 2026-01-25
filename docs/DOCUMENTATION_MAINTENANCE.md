# Documentation Maintenance Strategy

**Last Updated**: January 25, 2026  
**Purpose**: Guidelines for maintaining concise, up-to-date documentation

> **Note**: For actionable steps to maintain documentation, see the [Documentation Maintenance Workflow](../.agent/workflows/documentation-maintenance.md). This document provides the strategy and principles; the workflow provides step-by-step instructions for agents to execute.

## 📋 Core Documentation Structure

The repository maintains a **single source of truth** for each topic. All documentation lives in the `docs/` folder, with workflow guides in `.agent/workflows/`.

### Essential Documentation (Maintain)

| Document | Purpose | Update Frequency |
|----------|---------|------------------|
| `README.md` | Project overview, quick start | When setup changes |
| `docs/ARCHITECTURE.md` | System design, components | When architecture changes |
| `docs/DEVELOPMENT.md` | Dev environment, workflows | When dev process changes |
| `docs/TESTING.md` | Testing strategy, TDD workflow | When testing approach changes |
| `docs/STANDARDS.md` | Coding standards, patterns | When standards change |
| `docs/OPERATIONS.md` | Running, debugging, troubleshooting | When ops procedures change |
| `docs/DEPLOYMENT.md` | Production deployment guide | When deployment changes |
| `docs/CONFIG_FILES.md` | Configuration reference | When config changes |
| `docs/CURSOR_IDE.md` | IDE-specific setup | When IDE setup changes |
| `docs/ROADMAP.md` | Future improvements and planned work | When priorities change or items completed |
| `.agent/workflows/agent-development.md` | Agent creation workflow | When workflow changes |
| `.agent/workflows/agent-testing-checklist.md` | Agent testing checklist | When checklist changes |

### Agent-Specific Documentation

Each agent has its own `README.md` in `agents/<agent_name>/README.md`:
- Agent purpose and usage
- Run instructions
- Configuration requirements
- Agent-specific features

## 🗂️ Documentation Lifecycle

### Work-in-Progress Documents

**Rule**: Summary and review documents are **temporary** and should be archived after work is complete.

**Process**:
1. **During Work**: Create summary documents in root (e.g., `IMPLEMENTATION_SUMMARY.md`)
2. **After Completion**: 
   - Extract any permanent information into core docs
   - Move summary to `docs/archive/` or delete if no longer needed
   - Update core docs with completed changes

**Examples of Temporary Documents**:
- `*_SUMMARY.md` - Work completion summaries
- `*_REVIEW.md` - Codebase review documents
- `*_GAPS.md` - Gap analysis documents
- `*_FIXES.md` - Fix summaries

### When to Create New Documentation

✅ **Create new docs when**:
- Adding a new major feature that needs explanation
- Documenting a new workflow or process
- Creating agent-specific documentation

❌ **Don't create new docs when**:
- The information belongs in an existing doc (update existing instead)
- It's a temporary work summary (use archive)
- It's a duplicate of existing information

### Roadmaps, Improvements, and Issues Tracking

For tracking future work, improvements, and issues:

- **Use `docs/ROADMAP.md`**: For planned improvements, future features, and enhancement ideas
- **Update regularly**: Add new items when identified, mark completed items, archive when done
- **Keep it current**: Review monthly to ensure priorities are accurate
- **Link to issues**: If using GitHub issues, link to them from roadmap items
- **Archive completed**: Move completed roadmap items to `docs/archive/` after implementation

**Pattern**: 
- Roadmap items should be actionable and specific
- Include priority (High/Medium/Low) and status (Planned/In Progress/Completed)
- When an item is completed, update relevant core docs and archive the roadmap item

## 🔄 Maintenance Workflow

### Regular Maintenance (Monthly)

1. **Review root directory** for temporary summary files
2. **Archive or delete** completed work summaries
3. **Update core docs** with any changes from summaries
4. **Check for duplicates** and consolidate
5. **Update README** if structure changes

### After Major Work

1. **Extract permanent info** from summary docs into core docs
2. **Archive summary docs** to `docs/archive/` (or delete)
3. **Update relevant core docs** with completed changes
4. **Remove outdated information** from core docs

### Documentation Review Checklist

- [ ] All core docs in `docs/` are up-to-date
- [ ] No duplicate information across docs
- [ ] Temporary summary files are archived or deleted
- [ ] README links are correct
- [ ] Agent READMEs are current
- [ ] Workflow docs reflect current process

## 📁 Archive Structure

Completed work summaries and reviews are archived in `docs/archive/`:

```
docs/archive/
├── 2026-01/
│   ├── TECH_STACK_REVIEW.md
│   ├── AUTOMATION_FIXES_SUMMARY.md
│   └── ...
└── README.md  # Archive index
```

## 🎯 Documentation Principles

1. **Single Source of Truth**: Each topic has one authoritative document
2. **Living Documentation**: Core docs are updated as things change
3. **Temporary Summaries**: Work summaries are archived after completion
4. **Clear Structure**: Easy to find what you need
5. **No Duplication**: Information exists in one place only

## 📝 Writing Guidelines

### Core Documentation
- **Clear and concise**: Get to the point
- **Actionable**: Include commands, examples, steps
- **Current**: Remove outdated information
- **Organized**: Use clear headings and structure

### Work Summaries (Temporary)
- **Date-stamped**: Include completion date
- **Status**: Mark as complete/in-progress
- **Extractable**: Make it easy to pull info into core docs
- **Archived**: Move to archive after completion

## 🔍 Finding Documentation

### Quick Reference
- **Getting Started**: `README.md`
- **Architecture**: `docs/ARCHITECTURE.md`
- **Development**: `docs/DEVELOPMENT.md`
- **Testing**: `docs/TESTING.md`
- **Roadmap**: `docs/ROADMAP.md` (future improvements and planned work)
- **Agent Workflows**: `.agent/workflows/agent-development.md`
- **Documentation Maintenance**: `.agent/workflows/documentation-maintenance.md` (workflow)

### Full Index
See `README.md` for complete documentation index.

## 🔄 Using the Workflow

To perform documentation maintenance, use the [Documentation Maintenance Workflow](../.agent/workflows/documentation-maintenance.md). This workflow provides:

- Step-by-step instructions for agents to execute
- Specific tasks for common scenarios
- Checklists to ensure completeness
- Archive procedures
- Consolidation guidelines

The workflow can be run by agents or subagents with private context, allowing parallel work while you focus on other tasks.

## 🚨 Common Issues to Avoid

1. **Documentation Sprawl**: Too many docs saying the same thing
2. **Outdated Information**: Docs that don't match reality
3. **Orphaned Summaries**: Work summaries left in root
4. **Missing Updates**: Core docs not updated after changes
5. **Duplicate Content**: Same info in multiple places

## ✅ Success Criteria

Good documentation maintenance means:
- ✅ Easy to find what you need
- ✅ Information is current and accurate
- ✅ No duplicate or conflicting information
- ✅ Temporary docs are archived
- ✅ Core docs are comprehensive but concise
