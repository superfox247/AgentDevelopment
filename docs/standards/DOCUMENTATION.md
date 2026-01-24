# Documentation Standard
Version: 2026.01
Status: Active

## Overview
This document establishes the mandatory documentation standards for the Course Creation AI Agent Architecture. Strict adherence is required to ensure:
1.  **Agentic Context Optimization**: Agents use docstrings as tools/context. Poor docs = Poor Agent performance.
2.  **Maintainability**: Clear contracts for inputs/outputs.
3.  **Onboarding**: New developers (and AI agents) can understand intent without full code reading.

---

## 1. Python (Backend, Agents, Tests)

### Standard: Google Style
We strictly follow the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings) for docstrings.

### Rules
1.  **Coverage**: All functions, classes, and modules must have a docstring.
    *   *Exception*: Extremely simple one-line methods (e.g., getters) if self-explanatory.
2.  **Format**: Triple double codes `"""..."""`.
3.  **Testing**: Docstrings in tests must explain the *scenario* and *expected outcome*, not just repeat the function name.

### Example (Function)
```python
def generate_image(prompt: str, model: str | None = None) -> str:
    """Generates an image using the specified AI model.

    This function handles the prompt engineering, API call routing, and
    response parsing. It saves the resulting image to the local artifacts directory.

    Args:
        prompt: The user description of the image.
        model: Optional model ID (e.g. 'imagen-3.0'). Defaults to config.

    Returns:
        str: Absolute path to the generated image file.

    Raises:
        RuntimeError: If generation fails or no image is returned.
    """
    ...
```

### Example (Class)
```python
class ImageGeneratorService:
    """Service encapsulating image generation logic.

    Uses dependency injection for the GenAI client to facilitate testing.
    """
    ...
```

---

## 2. TypeScript (Dashboard Frontend)

### Standard: TSDoc
We use [TSDoc](https://tsdoc.org/) standards.

### Rules
1.  **Coverage**: All **exported** components, types, interfaces, and API client methods must have JSDoc/TSDoc comments.
2.  **Components**: Must document `Props` interfaces and the component itself.

### Example (Component)
```typescript
interface CardProps {
    /** The title displayed at the top of the card. */
    title: string;
    /** Optional click handler. */
    onClick?: () => void;
}

/**
 * A 3D-effect card component used for dashboard widgets.
 *
 * @param props - The properties for the card.
 * @returns The rendered JSX element.
 */
export function Card3D({ title, onClick }: CardProps) { ... }
```

### Example (API Client)
```typescript
/**
 * Fetches the current stats for all tracking Docker containers.
 *
 * @returns A promise resolving to the DockerStatsResponse.
 */
async getDockerStats(): Promise<DockerStatsResponse> { ... }
```
