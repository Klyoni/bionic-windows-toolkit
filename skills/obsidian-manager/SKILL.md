---
name: obsidian-manager
description: Rules for reading, searching, creating, and organizing Markdown notes in the Obsidian vault using the Obsidian MCP tools.
---
You have access to the user's Obsidian vault via the `Obsidian` MCP tools. Since the user is currently building and experimenting with their knowledge base without a rigid folder structure, follow these clean, safe rules:

1. Search Before Creating: Before creating any new note, ALWAYS search the vault first to check if a note on that topic already exists. If it does, offer to update or append to it instead of creating a duplicate.
2. Clean Markdown Formatting: Format all notes cleanly using Obsidian-flavored Markdown:
   - Include a concise YAML frontmatter block at the top (`created: YYYY-MM-DD`, `tags: [...]`). Get the exact current date from the `Time` MCP tool if needed.
   - Use internal wikilinks (`[[Note Title]]`) to connect related concepts, projects, or tools whenever relevant.
   - Use clear headings (`##`), bullet points, and callouts (`> [!info]`, `> [!tip]`) for readability.
3. Simple Default Organization: If the user does not specify a folder:
   - Save quick ideas, drafts, and AI experiments into an `Inbox/` (or `AI Notes/`) folder.
   - Group structured reference guides or project notes into clear top-level folders (e.g., `Projects/`, `Knowledge/`).
4. Safety First: NEVER delete, overwrite, or bulk-move existing user notes without explicitly asking for confirmation first. Appending to the end of a note is safe.

