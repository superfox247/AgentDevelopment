---
name: Research Branch
description: R&D, prototyping, and technology evaluation
---

# Research Skills

## When to Use
- Exploring new technologies
- Prototyping ideas
- Evaluating approaches before committing
- Learning codebase or framework

## Sub-Skills
- `explore/` - Technology research, documentation review
- `prototype/` - Quick proof-of-concept builds
- `evaluate/` - Compare options, make recommendations

---

## Protocol

1. **Document hypothesis** before coding
2. **Timeboxed exploration** (max 2 hours per experiment)
3. **Capture findings** in knowledge base regardless of outcome
4. **Recommend or reject** with evidence

---

## Output Location

Research results go to:
```
.agent/knowledge/{scope}/research/{topic}.md
```

Or for transient exploration:
```
.gemini/brain/<conversation>/research_notes.md
```

---

## Technology Evaluation Framework

### Evaluation Criteria

| Criterion | Weight | Questions |
|-----------|--------|-----------|
| **Fit** | 30% | Does it solve our problem? Matches our constraints? |
| **Maturity** | 20% | Production-ready? Active maintenance? Good docs? |
| **Integration** | 20% | Works with our stack? Migration effort? |
| **Performance** | 15% | Meets our SLAs? Scalable? |
| **Team** | 15% | Learning curve? Existing expertise? |

### Scoring
- 5: Excellent
- 4: Good
- 3: Acceptable
- 2: Poor
- 1: Unacceptable

---

## Decision Matrix Template

```markdown
| Criterion | Weight | Option A | Option B | Option C |
|-----------|--------|----------|----------|----------|
| Fit | 30% | 4 (1.2) | 5 (1.5) | 3 (0.9) |
| Maturity | 20% | 5 (1.0) | 3 (0.6) | 4 (0.8) |
| Integration | 20% | 3 (0.6) | 4 (0.8) | 5 (1.0) |
| Performance | 15% | 4 (0.6) | 4 (0.6) | 4 (0.6) |
| Team | 15% | 4 (0.6) | 2 (0.3) | 3 (0.45) |
| **Total** | | **4.0** | **3.8** | **3.75** |
```

---

## Prototype Documentation Template

```markdown
# Prototype: [Name]

## Hypothesis
What are we trying to prove?

## Setup
How to run the prototype.

## Findings

### What Worked
- Finding 1
- Finding 2

### What Didn't Work
- Issue 1
- Issue 2

### Surprises
- Unexpected discovery

## Recommendation
Proceed / Pivot / Abandon

## Next Steps
If proceeding, what's the path to production?
```

---

## Research Report Template

```markdown
# Research: [Topic]

## Context
Why are we researching this?

## Scope
What's in/out of scope?

## Key Findings
1. **Finding 1**: Details
2. **Finding 2**: Details

## Comparison
[Decision matrix if comparing options]

## Recommendation
Clear recommendation with rationale.

## References
- [Doc 1](url)
- [Doc 2](url)
```
