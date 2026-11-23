---
name: memory-manager
description: Rules for reading and updating persistent cross-chat memory using the Memory MCP server (entities, observations, relations).
---
You have access to a persistent Knowledge Graph via the `memory` MCP tools (`read_graph`, `search_nodes`, `create_entities`, `add_observations`, `create_relations`). Follow these rules strictly:

1. Recall on Start: At the beginning of a new conversation or when the user mentions past projects, hardware, or preferences, ALWAYS call `search_nodes` or `read_graph` first to check what you already know.
2. What to Save: Automatically save durable facts about the user using `create_entities` and `add_observations` without asking for permission:
   - Hardware & OS setup (Windows 11, Ryzen 7 7700, RTX 5070 12GB, 32GB RAM, Bionic).
   - Active coding projects, folder paths (e.g., Obsidian vault at `<YOUR_OBSIDIAN_VAULT_PATH>`), tech stack, and recurring tasks.
   - Explicit user preferences and formatting rules.
3. What NOT to Save: Never save temporary debugging steps, one-off math questions, passwords, or sensitive API keys.
4. Keep it Concise: Store observations as short, atomic factual sentences in Russian or English.
5. Exact JSON Schemas (CRITICAL — avoid schema validation errors):
   - For `create_entities`, ALWAYS pass: `{"entities": [{"name": "...", "entityType": "...", "observations": ["..."]}]}`
   - For `add_observations`, ALWAYS pass: `{"observations": [{"entityName": "...", "contents": ["..."]}]}`

