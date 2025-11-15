# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an MCP (Model Context Protocol) server designed as a personal assistant system. The server integrates with multiple productivity tools to support:
- Learning AI and French
- Improving English fluency
- Note-taking and knowledge management in Obsidian
- Task management via Todoist
- Calendar management via Google Calendar
- Flashcard learning via Anki (using AnkiConnect)
- Workflow automation exploration via n8n

The entire MCP server runs within a Docker container for portability and isolation.

## Architecture

### Current Implementation

The MCP server is built using Python 3.10+ with the official MCP SDK. The server runs via stdio (standard input/output) to communicate with MCP clients.

**Core Components:**

- `src/bird_mcp/server.py`: Main MCP server that registers tools and handles protocol communication
- `src/bird_mcp/todoist_tools.py`: Todoist API integration with async methods
- Tools are exposed via MCP protocol with JSON schema validation

### Integration Points

1. **Todoist Integration** (IMPLEMENTED)

   - Uses official `todoist-api-python` library
   - API documentation: <https://doist.github.io/todoist-api-python/>
   - Implemented tools:
     - `todoist_create_task`: Create tasks with content, description, due dates, priority, labels
     - `todoist_get_tasks`: Retrieve tasks with filters (project, label, Todoist filter syntax)
     - `todoist_complete_task`: Mark tasks as completed
     - `todoist_update_task`: Update any task field
     - `todoist_analyze_stats`: Comprehensive statistics (priority distribution, project breakdown, due date analysis)
     - `todoist_get_projects`: List all projects
   - Located in: `src/bird_mcp/todoist_tools.py:13`

2. **Anki Integration** (IMPLEMENTED)

   - Uses AnkiConnect HTTP API (port 8765 by default)
   - AnkiConnect add-on code: `2055492159`
   - Implemented tools:
     - `anki_create_deck`: Create new decks
     - `anki_get_decks`: List all decks with IDs
     - `anki_create_note`: Create basic flashcards (front/back)
     - `anki_create_cloze_note`: Create cloze deletion cards
     - `anki_get_deck_stats`: Statistics for specific deck
     - `anki_get_all_stats`: Comprehensive stats across all decks
     - `anki_update_deck_config`: Update daily limits (new cards, reviews)
     - `anki_find_notes`: Search notes using Anki query syntax
     - `anki_suspend_cards` / `anki_unsuspend_cards`: Manage card suspension
   - Located in: `src/bird_mcp/anki_tools.py:7`
   - Connection is optional - server works even if AnkiConnect is unavailable

3. **Obsidian Integration** (PLANNED)

   - Obsidian vault is synced via a GitHub repository
   - MCP server should be able to read/write notes and manage vault structure
   - Consider markdown parsing and frontmatter handling

4. **Google Calendar Integration** (PLANNED)

   - Use Google Calendar API for event management
   - Handle OAuth2 authentication securely
   - Support event creation, updates, and queries

5. **n8n Workflows** (PLANNED)

   - Consider webhook triggers or REST API integration
   - Design MCP tools that can be invoked from n8n workflows

### Docker Container Structure

- Python 3.11 slim base image
- Dependencies defined in `requirements.txt` and `pyproject.toml`
- Environment variables for API keys (via `.env` file)
- Volume mounts for persistent data (Obsidian vault when implemented)
- Runs server via CMD: `python -m bird_mcp.server`

## Development Commands

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Install dev dependencies
pip install -e ".[dev]"

# Run the MCP server
python -m bird_mcp.server

# Run tests
pytest

# Format code
black src/

# Lint code
ruff check src/
```

### Docker Commands

```bash
# Build and run with docker-compose
docker-compose up -d
docker-compose logs -f
docker-compose down

# Or build and run directly
docker build -t bird-mcp .
docker run -i --rm --env-file .env bird-mcp
```

### Environment Setup

1. Copy `.env.example` to `.env`
2. Add your Todoist API token from <https://todoist.com/app/settings/integrations/developer>
3. (Optional) Install AnkiConnect in Anki: Tools → Add-ons → Get Add-ons → Code `2055492159`
4. Environment variables:
   - Required: `TODOIST_API_TOKEN`
   - Optional: `ANKI_CONNECT_URL` (default: `http://localhost:8765`)

## Security Considerations

- API keys and tokens must be stored in environment variables, never in code
- Use .env files (excluded from git) for local development
- OAuth tokens should be securely stored and refreshed
- The GitHub repository for Obsidian vault may contain sensitive notes - handle with care

## MCP Server Design

### Tool Registration

All tools are registered in `src/bird_mcp/server.py:29` via the `@server.list_tools()` decorator. Each tool includes:

- Name (e.g., `todoist_create_task`)
- Description for LLM understanding
- JSON Schema for input validation
- Required vs optional parameters

Tool execution happens in `src/bird_mcp/server.py:157` via the `@server.call_tool()` decorator.

### Implemented Tools

**Todoist:** (6 tools)

- Task management: create, read, update, complete
- Project listing
- Statistics and analytics

**Anki:** (9 tools)

- Deck management: create, list
- Note creation: basic cards, cloze deletions
- Statistics: per-deck and overall
- Configuration: update daily limits
- Search and card management: find, suspend, unsuspend

### Future Tools (Planned)

**Obsidian:**

- Note creation, reading, updating
- Vault structure management
- Tag and frontmatter manipulation

**Anki:**

- Card creation and scheduling
- Deck management
- Study statistics

**Google Calendar:**

- Event creation, updates, deletion
- Calendar queries

**Cross-System:**

- Create coordinated workflows (note + task + event)
- Learning progress tracking across all systems
