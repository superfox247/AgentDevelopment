# GEMINI.md - Agent Router

## Protocol
1. Load `_core/router.md` → route intent to skill branch
2. Load `_core/context.md` → smart context loading
3. Execute branch skill with product overrides
4. Log issues to `_core/issues.md` → continuous improvement
5. **Before skill updates** → run `_core/review_skill.md` (automated)

## Skill Branches
| Intent | Branch | Keywords |
|--------|--------|----------|
| Plan | `sdlc/plan/` | design, spec, architect |
| Develop | `sdlc/develop/` | build, create, implement |
| Test | `sdlc/test/` | test, verify, validate |
| Review | `sdlc/review/` | review, audit, security |
| Deploy | `sdlc/deploy/` | deploy, release, ship |
| Operate | `sdlc/operate/` | debug, fix, monitor |
| Research | `sdlc/research/` | explore, prototype, evaluate |

## Products
See `products/{name}/manifest.yaml` for product-specific config.

## Issue Tracking
Log problems to `.agent/tracking/issues.md` for skill improvement.

## Invariants
- Schema-first (Pydantic/Zod before logic)
- No cross-domain imports
- Logging only (`logging.getLogger(__name__)`)
- **No skill updates without structural review** (automated via `review_skill.md`)


