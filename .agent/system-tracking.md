# System Tracking & Lessons Learned

**Last Updated**: 2026-01-25

Tracks workflow runs (what worked, issues, suggestions) and **durable lessons** we apply. Raw capture = per-run entries; curated lessons = section below. SYSTEM_REVIEW_* holds per-review notes (What Worked, Challenges, Suggestions).

---

## Durable Lessons

Extract from runs and SYSTEM_REVIEW when a lesson proves durable; trim when outdated.

- **Doc cleanup**: Archive summaries and delete root copies **immediately** after work. Root = `README.md` only.
- **Dynamic discovery**: Prefer dynamic discovery over hardcoded lists for agents/services. *(See [ADR-0002](../docs/adr/0002-dynamic-agent-discovery.md).)*
- **Verify before "done"**: Check actual state vs docs before marking items complete.

---

## Run Template

```markdown
### [Task Description] - [Date]
**Duration**: [time] | **Status**: Success | Partial | Failure
**Task Summary**: [Link to `.agent/tasks/TASK-[DATE]-[ID].md`]

**Phases**: [x] Understanding [x] Development [x] Code Quality [x] Testing [x] Verification

**What worked**: Bullets.
**Issues**: Bullets.
**Suggestions**: Bullets.
*(Optional: Commands that worked/had issues; log clarity.)*

**Detailed Summary**: See task execution summary for complete details.
```

---

## Recent Runs

### 2026-01-25: Discovery – System Review

**Duration**: ~15 min | **Status**: Success

**Phases**: [x] Doc review [x] Codebase exploration [x] Architecture [x] Issues [x] Deps [x] System review doc

**What worked**: Discovery workflow gave clear structure; docs and codebase well-organized; semantic search, `read_file`, `grep` effective.

**Issues**: TECH_STACK_REVIEW marked items complete but some mismatch with codebase (e.g. base_agent); no historical run data.

**Suggestions**: Add verification step to discovery (check prior issues resolved); "last verified" dates in key docs; link review status to implementation verification; track execution times.

**Output**: `.agent/SYSTEM_REVIEW_2026-01-25.md`

---

## Metrics

| Phase | Avg Time | Notes |
| :--- | :--- | :--- |
| Discovery | — | — |
| Research | — | — |
| Planning | — | — |
| Implementation | — | — |
| Testing | — | — |
| Verification | — | — |

| Command | Success | Issues |
| :--- | :--- | :--- |
| `make dev-reset` | — | — |
| `make dev-up` | — | — |
| `make test` | — | — |
| `make dev-verify` | — | — |

---

## Patterns

**Success**: Discovery workflow structure; colocated tests; AgentRegistry.  
**Problems**: *(Add as encountered.)*

---

## Action Items

- **Per run**: 
  - Create task execution summary (`.agent/tasks/TASK-[DATE]-[ID].md`)
  - Add entry to Recent Runs with link to task summary
  - Note what worked, issues, suggestions
  - Extract durable lessons when appropriate
  - Reference task summary for detailed information
