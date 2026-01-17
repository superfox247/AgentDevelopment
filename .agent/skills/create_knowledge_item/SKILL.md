---
name: Create Knowledge Item
description: A skill to capture and standardize new knowledge into the project's brain.
---

# Create Knowledge Item

"If it's not documented, it didn't happen."

## 1. Load Context
- `.agent/knowledge/`: Existing KIs.
- `GEMINI.md`: Docs standards.
- `.agent/skills/create_knowledge_item/create_knowledge_item.py`: The automation script.

## 2. Usage (Automated)

Run the script:
```bash
uv run .agent/skills/create_knowledge_item/create_knowledge_item.py --title "My Topic" --description "Summary" --sources "url1" "url2"
```

This will automatically:
1. Create `.agent/knowledge/[topic]/artifacts/`.
2. Generate `metadata.json`.
3. Create `overview.md`.

## 3. Verification
1.  Check the generated files.
2.  Edit `overview.md` to add content.
