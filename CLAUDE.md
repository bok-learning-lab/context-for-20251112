# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This repository serves as a curated documentation collection and reference codebase for AI agent development. It contains:

- **Documentation Archive** (`_context/documentation/`): 47 markdown files of vendor documentation for Anthropic, OpenAI, Slack, and Vercel APIs and SDKs
- **Web Component** (`web/`): Next.js 16 application (starter template, minimal customization)
- **Utility Scripts** (`scripts/`): Python utilities including word count analysis for markdown files

## Project Structure

### Documentation Organization (`_context/documentation/`)

The documentation is organized by vendor and categorized by topic. Use `_context/documentation/anthropic/index.md` as a navigation guide—it provides summaries of each document's focus area.

**Key Categories:**
- `anthropic/claude-agents-sdk/`: Complete SDK guides covering streaming, permissions, hosting, MCP integration, custom tools, subagents, and cost tracking
- `anthropic/claude-skills/`: Skills API usage, authoring best practices, CRUD operations
- `anthropic/claude-code/`: Hooks system and configuration reference
- `anthropic/api/`: Message Batches and core API patterns
- `openai/`: Realtime API guides (WebRTC, WebSocket, transcription, conversations)
- `slack/`: Bolt framework (Python/JavaScript), CLI, app manifests
- `vercel/`: (Present but not yet documented)

### Web Application (`web/`)

Standard Next.js 16 project using:
- React 19.2.0
- TypeScript 5
- Tailwind CSS 4
- pnpm for package management

**Development commands:**
```bash
cd web
pnpm dev        # Start development server on localhost:3000
pnpm build      # Production build
pnpm start      # Run production server
pnpm lint       # Run ESLint
```

### Utility Scripts (`scripts/`)

**Word Counter** (`scripts/wordcount.py`):
- Executable Python script (shebang: `#!/usr/bin/env python3`)
- Recursively counts words in `.md`, `.mdx`, and `.txt` files
- Usage: `./scripts/wordcount.py <folder_path>`
- Uses only standard library (no dependencies required)

## Architecture Notes

### Documentation as Context

The `_context/` directory is structured for efficient retrieval and reference. When working with AI agent implementations:

1. Check the relevant index file first (`anthropic/index.md`, etc.)
2. Documentation files are named descriptively and organized by API/SDK feature area
3. Many files contain complete code examples in Python, TypeScript, and cURL

### Next.js Application Structure

The `web/` directory is a minimal Next.js 16 setup:
- App Router architecture (not Pages Router)
- Tailwind CSS configured via `postcss.config.mjs`
- TypeScript strict mode enabled
- ESLint configured via `eslint.config.mjs`

## Common Workflows

### Working with Documentation

When asked about Anthropic, OpenAI, or Slack APIs:
1. Reference `_context/documentation/` files rather than making assumptions
2. Use the index files as navigation guides
3. Documentation files contain authoritative examples—prefer copying patterns from docs

### Analyzing Documentation Scope

Use `scripts/wordcount.py` to measure documentation coverage:
```bash
./scripts/wordcount.py _context/documentation/anthropic
./scripts/wordcount.py _context/documentation/openai
```

### Next.js Development

The Next.js app follows standard conventions:
- Entry point: `web/app/page.tsx`
- Layout: `web/app/layout.tsx`
- Build output: `web/.next/` (git-ignored)
- Static assets: `web/public/`

## Special Considerations

### Skills Integration

This repository can be used as a reference for Claude Skills development:
- See `_context/documentation/anthropic/claude-skills/` for API usage patterns
- See `_context/documentation/anthropic/claude-code/skills.md` for CLI-based Skills creation
- Skills can be added to `.claude/skills/` for project-level capabilities

### Hooks Configuration

Claude Code hooks can reference documentation dynamically:
- Hook definitions go in `.claude/hooks/`
- See `_context/documentation/anthropic/claude-code/hooks-reference.md` for configuration schemas
- Use hooks to inject relevant documentation context based on user queries
