# UX Patterns: Antigravity Prime Design System

The Antigravity Prime (v2/v3) design system is a modern, futuristic, spatial UI featuring liquid glassmorphism and high-density Bento Grid layouts.

## 1. Visual Hierarchy & Contrast
### A. The "Ring" Pattern
High-fidelity glassmorphism can suffer from poor edge definition against dark backgrounds.
- **Rule**: All glass cards must have a `ring-1 ring-white/10` border.
- **Accent**: Use `border-l-4` status accents (e.g., emerald for active) for high-scannability.
- **Gloss**: Use `backdrop-filter: blur(20px) saturate(140%)` for a "viscous" glass feel.

### B. Status Mapping Matrix
- **ACTIVE/UP**: `emerald` - Healthy/In-use.
- **CAUTION/STARTING**: `amber` - Transition states or non-critical logs.
- **ERROR/EXITED**: `rose` - Process failure or critical error logs.
- **NEUTRAL/OFFLINE**: `zinc` - Stopped or neutral state.

## 2. Information Density
### A. Progressive Disclosure
- **Status-First**: Default view shows only name and descriptive status. Metadata (Container ID, Runtime) is hidden until expanded.
- **Expanded Interaction**: Clicking a card expands a drawer revealing controls (Start, Stop, Restart) and recent log snippets.

### B. Interest-First Log Snippets
When displaying log snippets in cards, the client scans for `ERROR`, `CRITICAL`, or `WARNING`. If found, these lines are prioritized over the most recent sequential logs to ensure immediate triage.

## 3. Resilience & Navigation
### A. Emergency Exit Standard
- **Backdrop Closing**: All overlays (modals/drawers) must close on backdrop click.
- **Escape Key**: All modals must listen for the `Escape` key.
- **Explicit Close**: A prominent `X` button must be present in the top-right.

### B. Cross-Tab Linking
Selecting a container card's "View Logs" button must trigger a callback that lifts state to the parent, switches the primary view to the "Logs" tab, and auto-filters the stream to the selected container.

## 4. Component Implementation
### A. Key-based Remounting
Pass the resource ID (e.g., `container.id`) as a `key` to streaming components. This forces React to clean up the previous connection (EventSource) and mount a fresh instance, preventing "stale stream" race conditions.

### B. Safe Identification
Never call `crypto.randomUUID()` directly in render paths without a fallback. Use a utility that defaults to `Date.now()` logic in non-secure contexts to prevent crashes in headless or local-dev environments.
