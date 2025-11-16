# Bird MCP Server

A personal assistant MCP (Model Context Protocol) server that integrates with Todoist, Anki, and Obsidian to help you learn, organize, and stay productive. Built with Python and FastMCP, fully packaged with `uv` and Docker-compatible.

## Features

### Currently Implemented

**Todoist Integration (11 tools):**
- Create tasks with descriptions, due dates, priorities, and labels
- Retrieve and filter tasks by project, label, or custom filters
- Complete, update, and delete tasks
- Add and retrieve comments on tasks
- Analyze task statistics (priority distribution, project breakdown, due dates)
- List all projects, labels, and sections

**Anki Integration (14 tools):**
- Create and manage decks
- Create basic flashcards (front/back)
- Create cloze deletion cards
- Get comprehensive statistics (per deck and overall)
- Update deck configuration (daily limits)
- Find notes with Anki search syntax
- Suspend/unsuspend cards
- Get note types and detailed note information
- Update and delete notes

**Obsidian Integration (8 tools):**
- Create, read, update, and delete notes
- Search notes by content, folder, or tag
- List notes in vault or specific folders
- Get or create daily notes
- Get vault statistics

**Health Check:**
- Monitor connectivity and status of all integrated services

## Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Docker (optional, for containerized deployment)
- Todoist account and API token
- Anki with AnkiConnect add-on (optional, for Anki features)
- Obsidian vault (optional, for Obsidian features)

## Quick Start

### 1. Get Your API Tokens

**Todoist API Token:**
1. Go to [Todoist Integrations](https://todoist.com/app/settings/integrations/developer)
2. Scroll to "API token" section
3. Copy your API token

**AnkiConnect Setup (Optional):**
1. Open Anki
2. Go to Tools → Add-ons → Get Add-ons
3. Enter code: `2055492159`
4. Restart Anki
5. AnkiConnect will run on `http://localhost:8765` by default

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Required
TODOIST_API_TOKEN=your_todoist_token_here

# Optional
ANKI_CONNECT_URL=http://localhost:8765
OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault
```

## Installation & Running

### Option 1: Using uv (Recommended)

`uv` is a fast Python package installer and resolver. The project is fully configured to work with `uv`.

#### Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or with pip
pip install uv
```

#### Install Dependencies

```bash
# Install all dependencies (including the package itself)
uv sync

# Or install in editable mode
uv pip install -e .
```

#### Run the Server

```bash
# Direct execution
uv run python -m bird_mcp.server

# Or using mcp CLI (for development with inspector)
uv run mcp dev src/bird_mcp/server.py
```

The `mcp dev` command will start the MCP Inspector on `http://localhost:6274` for testing and debugging.

### Option 2: Using pip

#### Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### Install Dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

#### Run the Server

```bash
python -m bird_mcp.server
```

### Option 3: Using Docker

#### Build and Run with Docker Compose

```bash
# Create .env file with your API token
cp .env.example .env
# Edit .env and add your TODOIST_API_TOKEN

# Build and start the production container
docker-compose up -d

# Or start the development container with MCP Inspector
docker-compose --profile dev up -d bird-mcp-dev

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

#### Build and Run with Docker Directly

```bash
# Build production image
docker build -t bird-mcp .

# Run production container
docker run -d --name bird-mcp --env-file .env bird-mcp

# Build development image (with MCP Inspector)
docker build -f Dockerfile.dev -t bird-mcp-dev .

# Run development container
docker run -d --name bird-mcp-dev \
  --env-file .env \
  -p 6274:6274 -p 6277:6277 \
  bird-mcp-dev
```

## Packaging

The project is properly configured for packaging with both `uv` and standard Python tools.

### Package Structure

The project uses a `src` layout:

```
bird/
├── src/
│   └── bird_mcp/
│       ├── __init__.py
│       ├── server.py          # Main MCP server
│       ├── todoist_tools.py  # Todoist integration
│       ├── anki_tools.py      # Anki integration
│       ├── obsidian_tools.py  # Obsidian integration
│       └── utils.py           # Utility functions
├── pyproject.toml            # Package configuration
├── requirements.txt          # Dependencies (for pip)
├── uv.lock                   # Locked dependencies (for uv)
├── Dockerfile                # Production Docker image
└── Dockerfile.dev            # Development Docker image
```

### Building the Package

#### With uv

```bash
# Install in editable mode (development)
uv pip install -e .

# Build distribution packages
uv build

# This creates:
# - dist/bird_mcp-0.1.0.tar.gz (source distribution)
# - dist/bird_mcp-0.1.0-py3-none-any.whl (wheel)
```

#### With pip/setuptools

```bash
# Install in editable mode (development)
pip install -e .

# Build distribution packages
python -m build

# This creates distribution files in dist/
```

### Installing from Source

```bash
# From local source
pip install -e /path/to/bird

# Or with uv
uv pip install -e /path/to/bird
```

### Publishing to PyPI (Future)

```bash
# Build packages
uv build

# Upload to PyPI (requires credentials)
uv publish
```

## MCP Client Configuration

### Claude Desktop / Cursor Configuration

To use this MCP server with Claude Desktop or Cursor, add the following to your MCP settings file:

**Location:**
- **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**: `~/.config/Claude/claude_desktop_config.json`

**Configuration (using Python directly):**

```json
{
  "mcpServers": {
    "bird": {
      "command": "python",
      "args": ["-m", "bird_mcp.server"],
      "env": {
        "TODOIST_API_TOKEN": "your_token_here",
        "ANKI_CONNECT_URL": "http://localhost:8765",
        "OBSIDIAN_VAULT_PATH": "/path/to/vault"
      }
    }
  }
}
```

**Configuration (using uv):**

```json
{
  "mcpServers": {
    "bird": {
      "command": "uv",
      "args": ["run", "python", "-m", "bird_mcp.server"],
      "env": {
        "TODOIST_API_TOKEN": "your_token_here",
        "ANKI_CONNECT_URL": "http://localhost:8765",
        "OBSIDIAN_VAULT_PATH": "/path/to/vault"
      }
    }
  }
}
```

**Configuration (using Docker):**

```json
{
  "mcpServers": {
    "bird": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--env-file",
        "/path/to/.env",
        "bird-mcp"
      ]
    }
  }
}
```

**Note:** After updating the configuration file, restart Claude Desktop or Cursor for changes to take effect.

## Development

### Project Structure

```
bird/
├── src/
│   └── bird_mcp/
│       ├── __init__.py
│       ├── server.py          # Main MCP server with tool registrations
│       ├── todoist_tools.py   # Todoist API integration
│       ├── anki_tools.py      # AnkiConnect API integration
│       ├── obsidian_tools.py  # Obsidian vault filesystem integration
│       └── utils.py           # Shared utility functions
├── Dockerfile                 # Production Docker image (uses uv)
├── Dockerfile.dev            # Development Docker image (uses uv)
├── docker-compose.yml        # Docker Compose configuration
├── pyproject.toml            # Package configuration (PEP 621)
├── requirements.txt          # Dependencies list
├── uv.lock                   # Locked dependencies (uv)
└── README.md                 # This file
```

### Adding New MCP Tools

To add a new MCP tool to the server, follow these steps:

#### 1. Create or Update Tool Implementation

Create a new tool class in a separate file (e.g., `src/bird_mcp/my_service_tools.py`) or add methods to an existing tool class:

```python
"""My Service integration tools."""

from typing import Any
import httpx

class MyServiceTools:
    """Tools for interacting with My Service API."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = httpx.AsyncClient()
    
    async def do_something(self, param: str) -> dict[str, Any]:
        """Do something with the service.
        
        Args:
            param: Some parameter
            
        Returns:
            Dictionary with success status and result/error
        """
        try:
            # Your implementation here
            response = await self.client.get(
                "https://api.example.com/endpoint",
                headers={"Authorization": f"Bearer {self.api_key}"},
                params={"param": param}
            )
            response.raise_for_status()
            return {"success": True, "data": response.json()}
        except Exception as e:
            return {"success": False, "error": str(e)}
```

#### 2. Initialize the Tool in server.py

Add initialization code in `src/bird_mcp/server.py`:

```python
# At the top with other imports
from bird_mcp.my_service_tools import MyServiceTools

# In the initialization section (around line 40-67)
my_service_key = os.getenv("MY_SERVICE_API_KEY")
my_service = None
if my_service_key:
    try:
        logger.info("Initializing My Service integration...")
        my_service = MyServiceTools(my_service_key)
        logger.info("My Service integration initialized successfully")
    except Exception as e:
        logger.warning(f"My Service integration disabled: {e}")
else:
    logger.info("My Service integration disabled (MY_SERVICE_API_KEY not set)")
```

#### 3. Register the Tool with MCP

Add tool registration functions in `src/bird_mcp/server.py`:

```python
# My Service Tools

@mcp.tool()
async def my_service_do_something(param: str) -> dict[str, Any]:
    """Do something with My Service.
    
    Args:
        param: Some parameter description
        
    Returns:
        Dictionary with success status and result
    """
    if not my_service:
        return {"success": False, "error": "My Service integration not configured"}
    
    return await my_service.do_something(param=param)
```

#### 4. Add Health Check (Optional)

Update the `health_check` tool to include your new service:

```python
# In the health_check function (around line 73-148)
# Check My Service
if my_service:
    try:
        logger.info("Performing My Service health check...")
        result = await my_service.do_something("test")
        results["services"]["my_service"] = {
            "status": "connected" if result["success"] else "error",
            "message": (
                "Successfully connected to My Service"
                if result["success"]
                else result.get("error")
            ),
        }
    except Exception as e:
        logger.error(f"My Service health check failed: {e}")
        results["services"]["my_service"] = {"status": "error", "message": str(e)}
else:
    results["services"]["my_service"] = {
        "status": "disabled",
        "message": "My Service integration not configured (set MY_SERVICE_API_KEY)",
    }
```

#### 5. Update Dependencies (if needed)

If your new tool requires additional dependencies:

**For uv:**
```bash
uv add package-name
```

**For pip:**
```bash
pip install package-name
# Then update requirements.txt
pip freeze > requirements.txt
```

Or manually add to `pyproject.toml`:
```toml
dependencies = [
    # ... existing dependencies
    "package-name>=1.0.0",
]
```

#### 6. Update Environment Variables

Add your new service's API key to `.env.example` and document it:

```bash
# .env.example
MY_SERVICE_API_KEY=your_api_key_here
```

#### 7. Test Your Tool

```bash
# Start the MCP server with inspector
uv run mcp dev src/bird_mcp/server.py

# Or run directly
uv run python -m bird_mcp.server
```

Open `http://localhost:6274` (if using `mcp dev`) to test your tool in the MCP Inspector.

#### 8. Update Documentation

- Add your new tool to the "Available Tools" section in this README
- Update the features list at the top
- Document any new environment variables

### Running Tests

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# With coverage
pytest --cov=src/bird_mcp --cov-report=html
```

### Code Formatting

```bash
# Format code with black
black src/

# Lint code with ruff
ruff check src/

# Auto-fix linting issues
ruff check --fix src/
```

### Development with MCP Inspector

The MCP Inspector is a web-based tool for testing and debugging MCP servers:

```bash
# Start server with inspector
uv run mcp dev src/bird_mcp/server.py

# Or with Docker
docker-compose --profile dev up bird-mcp-dev
```

Then open `http://localhost:6274` in your browser. You'll need the authentication token shown in the terminal output.

## Available Tools

### Health Check (1 tool)

- **health_check**: Check the health and connectivity of all integrated services

### Todoist Tools (11 tools)

- **todoist_create_task**: Create a new task with optional description, project, due date, priority, and labels
- **todoist_get_tasks**: Retrieve tasks with optional filters (project, label)
- **todoist_complete_task**: Mark a task as completed
- **todoist_update_task**: Update task content, description, due date, priority, or labels
- **todoist_delete_task**: Permanently delete a task
- **todoist_analyze_stats**: Get comprehensive statistics about your tasks
- **todoist_get_projects**: List all your Todoist projects
- **todoist_get_labels**: Get all available Todoist labels
- **todoist_get_sections**: Get sections, optionally filtered by project
- **todoist_get_comments**: Get all comments for a task
- **todoist_add_comment**: Add a comment to a task

### Anki Tools (14 tools)

- **anki_create_deck**: Create a new deck in Anki
- **anki_get_decks**: Get all Anki decks with their IDs
- **anki_create_note**: Create a basic flashcard with front and back
- **anki_create_cloze_note**: Create a cloze deletion card (e.g., "{{c1::Paris}} is the capital of {{c2::France}}")
- **anki_get_deck_stats**: Get statistics for a specific deck (card counts, due cards, etc.)
- **anki_get_all_stats**: Get comprehensive statistics across all decks
- **anki_update_deck_config**: Update deck settings (new cards per day, reviews per day)
- **anki_find_notes**: Find notes using Anki search syntax (e.g., "deck:French tag:verb")
- **anki_suspend_cards**: Suspend cards to prevent them from appearing in reviews
- **anki_unsuspend_cards**: Unsuspend cards to allow them to appear in reviews again
- **anki_get_note_types**: Get all available note types (models) in Anki
- **anki_update_note**: Update an existing Anki note's fields and tags
- **anki_get_note_info**: Get detailed information about specific notes
- **anki_delete_notes**: Permanently delete notes from Anki

### Obsidian Tools (8 tools)

- **obsidian_create_note**: Create a new note in Obsidian vault with optional folder, tags, and frontmatter
- **obsidian_read_note**: Read a note from Obsidian vault by path
- **obsidian_update_note**: Update an existing note (replace or append content, update frontmatter)
- **obsidian_delete_note**: Delete a note from Obsidian vault
- **obsidian_search_notes**: Search notes by content, folder, or tag
- **obsidian_list_notes**: List all notes in vault or specific folder
- **obsidian_get_daily_note**: Get or create daily note for a specific date
- **obsidian_get_vault_stats**: Get statistics about the Obsidian vault (total notes, size, folder distribution)

## Troubleshooting

### Server Won't Start

1. **Check environment variables**: Ensure `TODOIST_API_TOKEN` is set
2. **Check Python version**: Requires Python 3.10+
3. **Check dependencies**: Run `uv sync` or `pip install -r requirements.txt`
4. **Check logs**: Look for error messages in stderr

### MCP Client Can't Connect

1. **Verify server is running**: Test with `python -m bird_mcp.server` directly
2. **Check MCP configuration**: Ensure the command and args are correct in your MCP settings
3. **Check environment variables**: Ensure they're set in the MCP configuration or `.env` file
4. **Check Python path**: Ensure the package is installed (`pip install -e .` or `uv pip install -e .`)

### Docker Issues

1. **Port conflicts**: Ensure ports 6274 and 6277 are available (for dev mode)
2. **Environment variables**: Ensure `.env` file exists and is properly formatted
3. **Build cache**: Try `docker-compose build --no-cache` if builds fail

### AnkiConnect Not Working

1. **Verify AnkiConnect is installed**: Check Anki → Tools → Add-ons
2. **Check Anki is running**: AnkiConnect only works when Anki is open
3. **Verify port**: Default is `http://localhost:8765`, check if different
4. **Test connection**: Use `health_check` tool to verify connectivity

## License

MIT
