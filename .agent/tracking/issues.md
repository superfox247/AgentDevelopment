# Agent Issue Log

Track problems encountered during work for skill improvement.

---

## 2026-01-20 - Type Error - Mock data missing fields

**Context**: Creating AgentsView component tests
**Error**: `Property 'path' is missing in type '{ domain: string; name: string; }'`
**Root Cause**: Mock data didn't match the actual API schema
**Resolution**: Added `path` field to mock agents
**Skill Update**: `sdlc/test/SKILL.md` should mention checking schema types for mocks
**Status**: resolved

---

## 2026-01-20 - Import Error - Wrong export type

**Context**: DockerMonitor test
**Error**: `getDockerContainers` does not exist on type 'ApiClient'
**Root Cause**: Guessed method name instead of checking actual client
**Resolution**: Changed to correct method `getDockerStats`
**Skill Update**: `sdlc/test/SKILL.md` should say "verify API method names"
**Status**: resolved

---

## 2026-01-20 - Skills Not Loaded - Skill system not consulted

**Context**: Full test implementation session
**Error**: Agent didn't load any SKILL.md files before working
**Root Cause**: No enforcement mechanism in old GEMINI.md
**Resolution**: Created hierarchical skill system with router
**Skill Update**: `_core/router.md` now requires skill loading
**Status**: resolved

---

## 2026-01-20 - Schema Path Mismatch - Alias hack created

**Context**: Docker containers failing on startup
**Error**: `No module named 'schemas.models'` - code referenced `schemas.models.protocol` but directory was `schemas/llm_models/`
**Root Cause**: Directory was named `llm_models` but all code imported from `models`
**Resolution**: Renamed `schemas/llm_models/` → `schemas/models/` to match imports
**Skill Update**: `sdlc/develop/SKILL.md` - always align directory names with import paths
**Status**: resolved

---

## 2026-01-20 - Tool Path Fragility - Docker vs Local paths differ

**Context**: image_generator container failing on startup
**Error**: `No module named 'domains'` - YAML used absolute path `domains.course_creator.image_generator.tools.func`
**Root Cause**: Dockerfile copies agent to `/app/orchestrator/` but YAML used full local path
**Resolution**: Added relative import support to `yaml_loader.py` - tools can now use `.tools.func_name`
**Skill Update**: `sdlc/develop/SKILL.md` - agents should use relative imports for local tools
**Status**: resolved

