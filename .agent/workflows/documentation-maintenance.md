---
description: Process for maintaining concise, up-to-date documentation and archiving temporary work summaries
---

# Documentation Maintenance Workflow

This workflow defines how to maintain documentation in this repository. Use this when documentation needs review, consolidation, or cleanup.

## Core Principles

1. **Single Source of Truth**: Each topic has one authoritative document
2. **Living Documentation**: Core docs are updated as things change
3. **Temporary Summaries**: Work summaries are archived after completion
4. **Clear Structure**: Easy to find what you need
5. **No Duplication**: Information exists in one place only

## Documentation Structure

### Core Documentation (Maintain in `docs/`)

| Document | Purpose | Location |
|----------|---------|----------|
| `README.md` | Project overview, quick start | Root |
| `ARCHITECTURE.md` | System design, components | `docs/` |
| `DEVELOPMENT.md` | Dev environment, workflows | `docs/` |
| `TESTING.md` | Testing strategy, TDD workflow | `docs/` |
| `STANDARDS.md` | Coding standards, patterns | `docs/` |
| `OPERATIONS.md` | Running, debugging, troubleshooting | `docs/` |
| `DEPLOYMENT.md` | Production deployment guide | `docs/` |
| `CONFIG_FILES.md` | Configuration reference | `docs/` |
| `CURSOR_IDE.md` | IDE-specific setup | `docs/` |

### Workflow Guides (Maintain in `.agent/workflows/`)

- `agent-development.md` - Agent creation workflow
- `agent-testing-checklist.md` - Agent testing checklist
- `documentation-maintenance.md` - This workflow

### Agent-Specific Documentation

Each agent has its own `README.md` in `agents/<agent_name>/README.md`

## Step 1: Identify Documentation Issues

Review the repository for documentation problems:

1. **Check root directory** for temporary summary files:
   - `*_SUMMARY.md` - Work completion summaries
   - `*_REVIEW.md` - Codebase review documents
   - `*_GAPS.md` - Gap analysis documents
   - `*_FIXES.md` - Fix summaries

2. **Check for duplicates**:
   - Same information in multiple files
   - Outdated information in core docs
   - Conflicting information across docs

3. **Check for outdated content**:
   - References to removed features
   - Outdated commands or examples
   - Broken links

4. **Check documentation structure**:
   - Files in wrong locations
   - Missing documentation for new features
   - Orphaned documentation

## Step 2: Archive Temporary Documents

For each temporary summary/review document found:

1. **Extract permanent information**:
   - Review the document for information that should be in core docs
   - Identify which core doc should be updated
   - Note the key information to extract

2. **Move to archive**:
   ```bash
   # Create archive directory if needed (YYYY-MM format)
   mkdir -p docs/archive/$(date +%Y-%m)
   
   # Move temporary document
   mv <document>.md docs/archive/$(date +%Y-%m)/
   ```

3. **Update archive README**:
   - Add entry to `docs/archive/README.md` listing the archived document
   - Include brief description and date

## Step 3: Update Core Documentation

For each piece of permanent information extracted:

1. **Identify target document**:
   - Architecture changes → `docs/ARCHITECTURE.md`
   - Development process → `docs/DEVELOPMENT.md`
   - Testing changes → `docs/TESTING.md`
   - Standards changes → `docs/STANDARDS.md`
   - Operations changes → `docs/OPERATIONS.md`
   - Deployment changes → `docs/DEPLOYMENT.md`

2. **Update the document**:
   - Add new information in appropriate section
   - Update outdated information
   - Remove references to removed features
   - Fix broken links
   - Ensure consistency with current codebase

3. **Maintain structure**:
   - Use clear headings
   - Keep sections organized
   - Include examples and commands
   - Add cross-references where helpful

## Step 4: Consolidate Duplicates

For duplicate information:

1. **Identify the authoritative source**:
   - Prefer core docs in `docs/` over root-level files
   - Prefer workflow guides in `.agent/workflows/` over scattered docs
   - Prefer most recent/complete version

2. **Merge content**:
   - Combine best information from all sources
   - Remove duplicates
   - Update all references to point to single source

3. **Delete or archive duplicates**:
   - Delete if completely redundant
   - Archive if has historical value

## Step 5: Update README Documentation Index

Ensure `README.md` has accurate documentation index:

1. **Review current index**:
   - Check all links work
   - Verify all core docs are listed
   - Ensure workflow guides are mentioned

2. **Update if needed**:
   - Add new core docs
   - Remove references to archived docs
   - Update descriptions if docs changed

## Step 6: Verify Documentation Quality

Run final checks:

1. **Link verification**:
   - All internal links work
   - All external links are valid
   - No broken references

2. **Content verification**:
   - Information is current
   - Examples work
   - Commands are correct
   - No contradictions

3. **Structure verification**:
   - Clear organization
   - Consistent formatting
   - Appropriate detail level

## Step 7: Document Changes

After maintenance work:

1. **Update `docs/DOCUMENTATION_MAINTENANCE.md`** if:
   - New patterns discovered
   - Process improvements identified
   - Structure changes made

2. **Note in commit message**:
   - What was archived
   - What was consolidated
   - What was updated

## Regular Maintenance Schedule

### Monthly Review

1. Scan root directory for temporary files
2. Check for outdated information in core docs
3. Archive any completed work summaries
4. Update core docs with recent changes

### After Major Work

1. Extract permanent info from summaries
2. Archive summary documents
3. Update relevant core docs
4. Remove outdated information

## Archive Structure

```
docs/archive/
├── YYYY-MM/
│   ├── <summary_doc_1>.md
│   ├── <summary_doc_2>.md
│   └── ...
└── README.md  # Archive index
```

## Common Tasks

### Task: Archive Work Summary

**When**: After completing a major feature or refactoring

**Steps**:
1. Review summary document for permanent information
2. Extract and update core docs as needed
3. Move summary to `docs/archive/YYYY-MM/`
4. Update archive README

### Task: Consolidate Duplicate Docs

**When**: Same information exists in multiple places

**Steps**:
1. Identify authoritative source
2. Merge best content
3. Update all references
4. Delete or archive duplicates

### Task: Update Outdated Documentation

**When**: Codebase changed but docs weren't updated

**Steps**:
1. Identify outdated sections
2. Update with current information
3. Remove references to removed features
4. Fix broken examples/commands

### Task: Add Documentation for New Feature

**When**: New major feature added

**Steps**:
1. Determine if new doc needed or update existing
2. If new: Create in appropriate location (`docs/` or `.agent/workflows/`)
3. If existing: Update relevant core doc
4. Update README index
5. Cross-reference related docs

## Checklist

Before completing documentation maintenance:

- [ ] All temporary summary files archived
- [ ] Permanent information extracted to core docs
- [ ] Duplicates consolidated
- [ ] Core docs updated with recent changes
- [ ] Outdated information removed
- [ ] Links verified and working
- [ ] README index accurate
- [ ] Archive README updated
- [ ] No orphaned documentation
- [ ] Documentation structure clear

## Success Criteria

Good documentation maintenance results in:

- ✅ Easy to find what you need
- ✅ Information is current and accurate
- ✅ No duplicate or conflicting information
- ✅ Temporary docs are archived
- ✅ Core docs are comprehensive but concise
- ✅ Clear structure and organization
