# Bird MCP Server

A personal assistant MCP (Model Context Protocol) server that integrates with Todoist, Anki, Obsidian, Google Calendar, and n8n to help you learn, organize, and stay productive.

## Features

### Currently Implemented

**Todoist Integration:**
- Create tasks with descriptions, due dates, priorities, and labels
- Retrieve and filter tasks by project, label, or custom filters
- Complete and update existing tasks
- Analyze task statistics (priority distribution, project breakdown, due dates)
- List all projects

**Anki Integration:**
- Create and manage decks
- Create basic flashcards (front/back)
- Create cloze deletion cards
- Get comprehensive statistics (per deck and overall)
- Update deck configuration (daily limits)
- Find notes with Anki search syntax
- Suspend/unsuspend cards

### Planned Features

- Obsidian vault management (synced via GitHub)
- Google Calendar event management
- n8n workflow triggers

## Setup

### Prerequisites

- Python 3.10 or higher
- Docker (optional, for containerized deployment)
- Todoist account and API token
- Anki with AnkiConnect add-on (optional, for Anki features)

### Get Your Todoist API Token

1. Go to [Todoist Integrations](https://todoist.com/app/settings/integrations/developer)
2. Scroll to "API token" section
3. Copy your API token

### Set Up AnkiConnect (Optional)

1. Open Anki
2. Go to Tools → Add-ons → Get Add-ons
3. Enter code: `2055492159`
4. Restart Anki
5. AnkiConnect will run on `http://localhost:8765` by default

### Local Development Setup

1. Clone the repository:
```bash
cd /path/to/bird
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
pip install -e .
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your TODOIST_API_TOKEN
# Optionally set ANKI_CONNECT_URL if different from default
```

5. Run the MCP server:
```bash
python -m bird_mcp.server
```

### Docker Setup

1. Build and run with Docker Compose:
```bash
# Create .env file with your API token
cp .env.example .env
# Edit .env and add your TODOIST_API_TOKEN

# Build and start the container
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

2. Or build and run with Docker directly:
```bash
docker build -t bird-mcp .
docker run -d --name bird-mcp --env-file .env bird-mcp
```

## MCP Client Configuration

To use this MCP server with Claude Desktop or other MCP clients, add the following to your MCP settings:

```json
{
  "mcpServers": {
    "bird": {
      "command": "python",
      "args": ["-m", "bird_mcp.server"],
      "env": {
        "TODOIST_API_TOKEN": "your_token_here"
      }
    }
  }
}
```

Or if using Docker:

```json
{
  "mcpServers": {
    "bird": {
      "command": "docker",
      "args": ["run", "-i", "--rm", "--env-file", "/path/to/.env", "bird-mcp"]
    }
  }
}
```

## Available Tools

### Todoist Tools (6 tools)

- **todoist_create_task**: Create a new task with optional description, project, due date, priority, and labels
- **todoist_get_tasks**: Retrieve tasks with optional filters (project, label, or Todoist filter syntax)
- **todoist_complete_task**: Mark a task as completed
- **todoist_update_task**: Update task content, description, due date, priority, or labels
- **todoist_analyze_stats**: Get comprehensive statistics about your tasks
- **todoist_get_projects**: List all your Todoist projects

### Anki Tools (9 tools)

- **anki_create_deck**: Create a new deck in Anki
- **anki_get_decks**: Get all Anki decks with their IDs
- **anki_create_note**: Create a basic flashcard with front and back
- **anki_create_cloze_note**: Create a cloze deletion card (e.g., "{{c1::Paris}} is the capital of {{c2::France}}")
- **anki_get_deck_stats**: Get statistics for a specific deck (card counts, due cards, etc.)
- **anki_get_all_stats**: Get comprehensive statistics across all decks
- **anki_update_deck_config**: Update deck settings (new cards per day, reviews per day)
- **anki_find_notes**: Find notes using Anki search syntax (e.g., "deck:French tag:verb")
- **anki_suspend_cards** / **anki_unsuspend_cards**: Suspend or unsuspend cards

## Development

### Project Structure

```
bird/
├── src/
│   └── bird_mcp/
│       ├── __init__.py
│       ├── __main__.py        # Module entry point
│       ├── server.py          # Main MCP server
│       ├── todoist_tools.py   # Todoist integration
│       └── anki_tools.py      # Anki integration
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── requirements.txt
└── README.md
```

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Code Formatting

```bash
black src/
ruff check src/
```

## License

MIT
