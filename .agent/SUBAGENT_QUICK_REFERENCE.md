# Subagent System Quick Reference

> Quick visual reference for the subagent architecture

## Core Architecture

```
👤 User
  │
  └─→ 🎯 Orchestrator (Main Agent)
        │
        ├─→ 📚 Understanding Subagent
        ├─→ 💻 Development Subagent
        ├─→ ✅ Code Quality Subagent
        ├─→ 🧪 Testing Subagent
        ├─→ ✓ Verification Subagent
        └─→ 📊 Task Tracking Subagent (background)
```

## Nested Delegation

```
🎯 Orchestrator
  └─→ 💻 Development Subagent
        ├─→ 🔍 Research Subagent (when needed)
        ├─→ 🐛 Debugger Subagent (on error)
        └─→ 🏃 Test Runner Subagent (for tests)
              └─→ 📊 Analysis Subagent (deep dive)
```

## Execution Patterns

### Sequential (Default)
```
Orchestrator → Understanding → Development → Quality → Testing → Verification
```

### Parallel (Independent Tasks)
```
Orchestrator → [Development, Quality, Testing, Documentation] (simultaneous)
```

### Nested (Complex Tasks)
```
Orchestrator → Development → Debugger → Analysis → [Results flow back up]
```

## Subagent Roles

| Subagent | Purpose | Model | Mode |
|----------|---------|-------|------|
| **Orchestrator** | Delegates all work | inherit | foreground |
| **Understanding** | Codebase exploration | fast | foreground |
| **Development** | Code implementation | inherit | foreground |
| **Code Quality** | Linting, type checking | fast | foreground |
| **Testing** | Test execution | fast | foreground |
| **Verification** | Validate completion | fast | foreground |
| **Task Tracking** | Progress tracking | fast | background |
| **Research** | Deep research | fast | foreground |
| **Debugger** | Error debugging | inherit | foreground |
| **Test Runner** | Test automation | fast | foreground |

## Key Benefits

✅ **Context Isolation** - Each subagent has clean context  
✅ **Parallel Execution** - Multiple subagents run simultaneously  
✅ **Specialized Expertise** - Focused subagents = better results  
✅ **Reusability** - Subagents work across projects  
✅ **Nested Delegation** - Subagents can spawn subagents  

## File Locations

All subagents in: `.cursor/agents/*.md`

---

**See**: [SUBAGENT_ARCHITECTURE_PLAN.md](SUBAGENT_ARCHITECTURE_PLAN.md) for full details
