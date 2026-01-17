# Documentation Standards

This document outlines the standards for documentation within the Agent Factory.

## Diagramming with Mermaid

We use [Mermaid](https://mermaid.js.org/) for all diagrams.

**Reference**: [Mermaid Syntax Documentation](https://mermaid.js.org/intro/syntax-reference.html)

### Best Practices

1.  **Quoting Subgraph Titles**: Always quote subgraph titles to avoid parsing errors.
    *   ✅ `subgraph "My Subgraph"`
    *   ❌ `subgraph My Subgraph`
2.  **Class Definitions**: Define styles (`classDef`) at the top of the diagram.
3.  **Direction**: Use `TD` (Top-Down) or `LR` (Left-Right) explicitly.

## Available Models

We maintain an up-to-date list of available Gemini models in [available_models.md](./available_models.md). This list is automated and should not be manually edited.
