# Bird MCP Server

A personal assistant MCP (Model Context Protocol) server that integrates with Todoist, Anki, and Obsidian to help you learn, organize, and stay productive. Built with Python and FastMCP, fully packaged with `uv` and Docker-compatible.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Installation & Running](#installation--running)
  - [Option 1: Using uv](#option-1-using-uv-recommended)
  - [Option 2: Using pip](#option-2-using-pip)
  - [Option 3: Using Docker](#option-3-using-docker)
- [Packaging](#packaging)
- [MCP Client Configuration](#mcp-client-configuration)
  - [Claude Desktop / Cursor](#claude-desktop--cursor-configuration)
  - [Claude Code (CLI)](#claude-code-configuration)
- [Development](#development)
- [Available Tools](#available-tools)
- [Troubleshooting](#troubleshooting)

## Quick Reference

```bash
# Quick start with uv
uv venv && source .venv/bin/activate
uv pip install -e .
cp .env.example .env  # Edit with your API tokens
python -m bird_mcp.server

# Add to Claude Code
claude mcp add --transport stdio --scope local bird-personal-assistant -- python -m bird_mcp.server

# Build Docker image
docker build -t bird-mcp .

# Run with Docker
docker run -i --rm --env-file .env bird-mcp
```

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

**Google Calendar Integration (10 tools):**
- List all available calendars
- Create, update, and delete calendar events
- Get events within time ranges (today, upcoming, custom)
- Find free time slots for scheduling
- Quick add events using natural language
- Block study time for learning workflows

**Health Check:**
- Monitor connectivity and status of all integrated services

## Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) (recommended) or pip
- Docker (optional, for containerized deployment)
- Todoist account and API token
- Anki with AnkiConnect add-on (optional, for Anki features)
- Obsidian vault (optional, for Obsidian features)
- Google Calendar with OAuth2 credentials (optional, for Google Calendar features)

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

**Google Calendar Setup (Optional):**
See the [Google Calendar Setup Guide](#google-calendar-setup) section below for detailed OAuth2 configuration instructions.

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Required
TODOIST_API_TOKEN=your_todoist_token_here

# Optional
ANKI_CONNECT_URL=http://localhost:8765
OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault
GOOGLE_CALENDAR_CREDENTIALS_PATH=/path/to/credentials.json
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

**Important for Obsidian Integration:** If you want to use Obsidian features with Docker, you'll need to mount your vault as a volume (see below).

#### Build and Run with Docker Compose

```bash
# 1. Create .env file with your configuration
cp .env.example .env

# 2. Edit .env and configure:
#    - TODOIST_API_TOKEN (required)
#    - ANKI_CONNECT_URL (optional, default: http://host.docker.internal:8765)
#    - OBSIDIAN_VAULT_PATH (optional, for Obsidian integration)

# 3. Build and start the production container
docker-compose up -d

# Or start the development container with MCP Inspector
docker-compose --profile dev up -d bird-mcp-dev

# View logs
docker-compose logs -f

# Stop the container
docker-compose down
```

#### Mounting Obsidian Vault (Required for Obsidian Integration)

If you want to use Obsidian features, you need to mount your vault into the container. Edit `docker-compose.yml`:

```yaml
services:
  bird-mcp:
    # ... existing configuration
    volumes:
      # Mount your Obsidian vault (read-write access)
      - /path/to/your/obsidian/vault:/app/vault:rw
    environment:
      - TODOIST_API_TOKEN=${TODOIST_API_TOKEN}
      - ANKI_CONNECT_URL=${ANKI_CONNECT_URL:-http://host.docker.internal:8765}
      - OBSIDIAN_VAULT_PATH=/app/vault  # Path inside container
```

Then update your `.env`:

```bash
# .env
OBSIDIAN_VAULT_PATH=/app/vault  # This matches the container path
```

**Note:** The `host.docker.internal` hostname allows the Docker container to connect to AnkiConnect running on your host machine.

#### Build and Run with Docker Directly

```bash
# Build production image
docker build -t bird-mcp .

# Run production container (basic, no Obsidian)
docker run -d --name bird-mcp --env-file .env bird-mcp

# Run with Obsidian vault mounted
docker run -d --name bird-mcp \
  --env-file .env \
  -v /path/to/your/obsidian/vault:/app/vault:rw \
  -e OBSIDIAN_VAULT_PATH=/app/vault \
  bird-mcp

# Build development image (with MCP Inspector)
docker build -f Dockerfile.dev -t bird-mcp-dev .

# Run development container with all features
docker run -d --name bird-mcp-dev \
  --env-file .env \
  -p 6274:6274 -p 6277:6277 \
  -v /path/to/your/obsidian/vault:/app/vault:rw \
  -e OBSIDIAN_VAULT_PATH=/app/vault \
  bird-mcp-dev

# Access MCP Inspector at http://localhost:6274
```

#### Using Docker with Claude Desktop

To use the Dockerized MCP server with Claude Desktop, configure it in your `claude_desktop_config.json`:

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
        "/absolute/path/to/bird/.env",
        "-v",
        "/absolute/path/to/obsidian/vault:/app/vault:rw",
        "bird-mcp"
      ]
    }
  }
}
```

**Important:** Use absolute paths for `--env-file` and volume mounts.

## Packaging

The project is properly configured for packaging with both `uv` and standard Python tools, following PEP 621 standards.

### Package Structure

The project uses a `src` layout for better packaging practices:

```
bird/
├── src/
│   └── bird_mcp/
│       ├── __init__.py                 # Package initialization with version
│       ├── server.py                   # Main MCP server with tool registrations
│       ├── todoist_tools.py            # Todoist API integration (11 tools)
│       ├── anki_tools.py               # AnkiConnect API integration (14 tools)
│       ├── obsidian_tools.py           # Obsidian vault integration (8 tools)
│       ├── google_calendar_tools.py    # Google Calendar API integration (10 tools)
│       └── utils.py                    # Error handling and retry decorators
├── pyproject.toml                      # PEP 621 package configuration
├── requirements.txt                    # Dependencies list (for pip)
├── uv.lock                             # Locked dependencies (for uv reproducibility)
├── .dockerignore                       # Files excluded from Docker builds
├── Dockerfile                          # Production Docker image (uses uv)
├── Dockerfile.dev                      # Development Docker image (with MCP Inspector)
├── docker-compose.yml                  # Multi-service Docker configuration
├── .env.example                        # Example environment variables
└── README.md                           # This file
```

### Building the Package

#### Method 1: With uv (Recommended)

`uv` is a fast Python package installer and resolver that provides better dependency management and faster builds.

```bash
# Install the package in editable mode (for development)
uv pip install -e .

# This allows you to modify source code and see changes immediately
# The package is installed but points to your source directory

# Build distribution packages
uv build

# This creates two distribution formats:
# - dist/bird_mcp-0.1.0.tar.gz        (source distribution)
# - dist/bird_mcp-0.1.0-py3-none-any.whl  (wheel - faster to install)
```

**What's in the wheel?**
- Compiled bytecode (`.pyc` files)
- All source modules from `src/bird_mcp/`
- Package metadata from `pyproject.toml`
- Dependencies list

#### Method 2: With pip and setuptools

```bash
# Install the package in editable mode
pip install -e .

# Install build tool
pip install build

# Build distribution packages
python -m build

# This creates the same dist/ files as uv build
```

### Installing from Source

#### Install from Local Directory

```bash
# For development (editable install - changes reflect immediately)
cd /path/to/bird
pip install -e .

# For production (regular install - creates a copy)
pip install /path/to/bird

# With uv
uv pip install -e /path/to/bird
```

#### Install from Git Repository

```bash
# Direct from git (requires git URL)
pip install git+https://github.com/yourusername/bird.git

# With uv
uv pip install git+https://github.com/yourusername/bird.git

# Specific branch or tag
pip install git+https://github.com/yourusername/bird.git@main
```

#### Install from Built Wheel

```bash
# After building with 'uv build' or 'python -m build'
pip install dist/bird_mcp-0.1.0-py3-none-any.whl

# With uv
uv pip install dist/bird_mcp-0.1.0-py3-none-any.whl
```

### Publishing to PyPI (Future)

When ready to publish to PyPI for public distribution:

```bash
# 1. Ensure version is updated in pyproject.toml
# 2. Build fresh distribution packages
uv build

# 3. Check the distribution
twine check dist/*

# 4. Upload to TestPyPI first (for testing)
uv publish --publish-url https://test.pypi.org/legacy/

# 5. Test installation from TestPyPI
pip install -i https://test.pypi.org/simple/ bird-mcp

# 6. If everything works, publish to real PyPI
uv publish

# Users can then install with:
# pip install bird-mcp
```

### Verifying Installation

After installing the package, verify it's working:

```bash
# Check package is installed
pip list | grep bird-mcp

# Check version
python -c "import bird_mcp; print(bird_mcp.__version__)"

# Run the MCP server
python -m bird_mcp.server

# You should see:
# INFO - Initializing Todoist integration...
# INFO - Todoist integration initialized successfully
# ...
```

### Dependency Management

The project uses multiple dependency files for different tools:

- **pyproject.toml**: Source of truth for dependencies (PEP 621)
- **requirements.txt**: Generated from pyproject.toml for pip users
- **uv.lock**: Lock file for reproducible builds with uv

#### Updating Dependencies

```bash
# With uv (recommended - updates uv.lock automatically)
uv add package-name
uv add --dev package-name  # for dev dependencies

# With pip (requires manual updates)
# 1. Edit pyproject.toml dependencies list
# 2. Reinstall
pip install -e .
# 3. Update requirements.txt
pip freeze > requirements.txt
```

#### Syncing Dependencies

```bash
# Install exact versions from uv.lock (reproducible)
uv sync --frozen

# Update all dependencies to latest compatible versions
uv sync

# Update a specific package
uv add package-name --upgrade
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

### Claude Code Configuration

To use this MCP server with Claude Code (the CLI tool), use the `claude mcp add` command:

#### Quick Setup

```bash
# Add the server to Claude Code with local scope
claude mcp add --transport stdio --scope local bird-personal-assistant -- python -m bird_mcp.server

# Or with uv
claude mcp add --transport stdio --scope local bird-personal-assistant -- uv run python -m bird_mcp.server
```

#### Verify Connection

```bash
# List all configured MCP servers
claude mcp list

# You should see:
# bird-personal-assistant: python -m bird_mcp.server - ✓ Connected
```

#### Environment Variables for Claude Code

Claude Code will use the `.env` file in your project directory. Ensure it's properly configured:

```bash
# Navigate to your project directory
cd /path/to/bird

# Create .env from example
cp .env.example .env

# Edit .env with your credentials
# Required:
TODOIST_API_TOKEN=your_token_here

# Optional:
ANKI_CONNECT_URL=http://localhost:8765
OBSIDIAN_VAULT_PATH=/path/to/your/obsidian/vault
```

**Important:** Make sure you're in the project directory when running `claude` commands, or the server won't be able to find the `.env` file.

#### Testing the Integration

Once configured, you can test the server with Claude Code:

```bash
# Start a conversation
claude

# Try a command like:
"Check the health of my MCP server"
"Create a Todoist task named 'Test from Claude Code'"
"Show me my Obsidian vault statistics"
```

#### Removing the Server

If you need to remove the server from Claude Code:

```bash
# Remove the MCP server
claude mcp remove bird-personal-assistant
```

## Development

### Project Architecture

The Bird MCP server is built using a modular architecture:

**Core Components:**

1. **server.py** - Main MCP server
   - Registers all tools via `@mcp.tool()` decorators
   - Initializes integrations with environment variables
   - Handles tool execution and error responses
   - Provides health check endpoint

2. **todoist_tools.py** - Todoist Integration
   - Uses official `todoist-api-python` library
   - Async/await pattern with `asyncio.to_thread()` for sync API calls
   - Handles ResultsPaginator nested list structures
   - 11 tools for task management and analytics

3. **anki_tools.py** - AnkiConnect Integration
   - HTTP API client for AnkiConnect (port 8765)
   - Note type validation before card creation
   - Supports basic cards, cloze deletions, and card management
   - 14 tools for flashcard operations

4. **obsidian_tools.py** - Obsidian Integration
   - Filesystem-based vault access (no API required)
   - YAML frontmatter parsing and generation
   - Daily notes integration
   - 8 tools for note management

5. **google_calendar_tools.py** - Google Calendar Integration
   - OAuth2 authentication with Google Calendar API v3
   - Automatic token refresh and persistence
   - Natural language event creation (Quick Add)
   - Free slot finding and study time blocking
   - 10 tools for calendar management

6. **utils.py** - Shared Utilities
   - Error handling decorators for consistent responses
   - Retry logic with exponential backoff
   - BaseIntegration abstract class for future integrations

**Design Patterns:**

- **Optional Integration Pattern**: Services gracefully degrade if not configured
- **Error Handling**: Consistent `{"success": bool, "error": str}` responses
- **Async/Await**: Non-blocking operations for external API calls
- **Environment-based Config**: All secrets via environment variables

### Project Structure

```
bird/
├── src/
│   └── bird_mcp/
│       ├── __init__.py                 # Package initialization with version
│       ├── server.py                   # Main MCP server (44 tools total)
│       ├── todoist_tools.py            # Todoist API integration (11 tools)
│       ├── anki_tools.py               # AnkiConnect API integration (14 tools)
│       ├── obsidian_tools.py           # Obsidian vault integration (8 tools)
│       ├── google_calendar_tools.py    # Google Calendar API integration (10 tools)
│       └── utils.py                    # Error handling and retry decorators
├── Dockerfile                          # Production Docker image (uses uv)
├── Dockerfile.dev                      # Development Docker image (uses uv)
├── docker-compose.yml                  # Docker Compose configuration
├── .dockerignore                       # Files excluded from Docker builds
├── pyproject.toml                      # Package configuration (PEP 621)
├── requirements.txt                    # Dependencies list
├── uv.lock                             # Locked dependencies (uv)
├── .env.example                        # Example environment variables
└── README.md                           # This file
```

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/bird.git
cd bird

# Create virtual environment with uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Or with Python's venv
python -m venv venv
source venv/bin/activate

# Install dependencies in editable mode
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"

# Set up environment variables
cp .env.example .env
# Edit .env with your API tokens

# Run the server
python -m bird_mcp.server
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

- **health_check**: Check the health and connectivity of all integrated services (Todoist, Anki, Obsidian, Google Calendar)

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

### Google Calendar Tools (10 tools)

- **google_calendar_list_calendars**: List all available Google Calendars with IDs, names, and access roles
- **google_calendar_create_event**: Create a new calendar event with title, time, description, location, and attendees
- **google_calendar_get_events**: Get events within a specified time range
- **google_calendar_update_event**: Update an existing calendar event (title, time, description, location)
- **google_calendar_delete_event**: Delete a calendar event
- **google_calendar_find_free_slots**: Find available time slots in the calendar for scheduling
- **google_calendar_quick_add**: Create an event using natural language (e.g., "Lunch with John tomorrow at 12pm")
- **google_calendar_get_today_events**: Get all events for today
- **google_calendar_get_upcoming_events**: Get upcoming events for the next N days
- **google_calendar_block_study_time**: Create a study block event for learning workflows (integrates with Anki/Obsidian)

## Google Calendar Setup

The Google Calendar integration requires OAuth2 authentication. Follow these steps to set it up:

### Step 1: Create a Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" at the top, then "New Project"
3. Enter a project name (e.g., "Bird MCP Calendar")
4. Click "Create"

### Step 2: Enable Google Calendar API

1. In your Google Cloud project, go to "APIs & Services" > "Library"
2. Search for "Google Calendar API"
3. Click on "Google Calendar API"
4. Click "Enable"

### Step 3: Configure OAuth Consent Screen

1. Go to "APIs & Services" > "OAuth consent screen"
2. Select "External" user type (unless you have a Google Workspace)
3. Click "Create"
4. Fill in the required fields:
   - App name: "Bird MCP Server"
   - User support email: Your email
   - Developer contact information: Your email
5. Click "Save and Continue"
6. On the "Scopes" page, click "Add or Remove Scopes"
7. Add the Google Calendar API scope:
   - Filter for "Google Calendar API"
   - Select `https://www.googleapis.com/auth/calendar`
8. Click "Update" then "Save and Continue"
9. On "Test users", add your Google account email
10. Click "Save and Continue"

### Step 4: Create OAuth2 Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "+ Create Credentials" > "OAuth client ID"
3. Select "Desktop app" as the application type
4. Enter a name (e.g., "Bird MCP Desktop")
5. Click "Create"
6. Click "Download JSON" to download your credentials file
7. Save the file as `credentials.json` in a secure location

### Step 5: Configure Environment Variables

Update your `.env` file with the path to your credentials:

```bash
# Google Calendar Integration
GOOGLE_CALENDAR_CREDENTIALS_PATH=/absolute/path/to/credentials.json

# Optional: Custom token storage location
# GOOGLE_CALENDAR_TOKEN_PATH=/path/to/token.pickle
```

**Important:** Use absolute paths, not relative paths like `~/` or `./`

### Step 6: Initial Authentication

The first time you use the Google Calendar integration, you'll need to authenticate:

1. Start the MCP server:
   ```bash
   python -m bird_mcp.server
   ```

2. A browser window will open automatically asking you to sign in to Google

3. Sign in with the Google account you added as a test user

4. Grant the requested permissions (Calendar access)

5. You'll see a success message in your browser

6. The authentication token will be saved automatically to `~/.bird_mcp/google_calendar_token.pickle`

7. Future requests will use this saved token (no browser required)

### Token Management

- **Token Location**: By default, tokens are saved to `~/.bird_mcp/google_calendar_token.pickle`
- **Token Refresh**: Tokens are automatically refreshed when they expire
- **Revoke Access**: To revoke access, delete the token file and remove the app from your [Google Account permissions](https://myaccount.google.com/permissions)

### Troubleshooting Google Calendar

**"Credentials file not found"**
- Verify `GOOGLE_CALENDAR_CREDENTIALS_PATH` points to the correct file
- Use absolute paths: `/Users/username/credentials.json` not `~/credentials.json`

**"Access blocked: This app's request is invalid"**
- Make sure you added your email as a test user in OAuth consent screen
- Verify the Google Calendar API is enabled in your project

**"Invalid grant" or "Token has been expired or revoked"**
- Delete the token file: `rm ~/.bird_mcp/google_calendar_token.pickle`
- Restart the server to re-authenticate

**Browser doesn't open during authentication**
- Check the terminal output for the authentication URL
- Copy and paste the URL into your browser manually
- Follow the authentication steps in the browser

### Security Considerations

1. **Credentials File**: Keep `credentials.json` secure - it contains your OAuth2 client secret
2. **Token File**: The token file contains access to your calendar - keep it secure
3. **Scopes**: The integration only requests calendar access, not other Google services
4. **Test Users**: In development, only accounts added as test users can authenticate
5. **Publishing**: To allow any Google account, you'll need to verify your app (not required for personal use)

### Using with Docker

When using Docker, you need to mount both the credentials and token files:

```bash
# Create directory for credentials
mkdir -p ~/.bird_mcp

# Copy credentials file
cp /path/to/credentials.json ~/.bird_mcp/

# Run with Docker, mounting the credentials directory
docker run -i --rm \
  --env-file .env \
  -v ~/.bird_mcp:/root/.bird_mcp:rw \
  -e GOOGLE_CALENDAR_CREDENTIALS_PATH=/root/.bird_mcp/credentials.json \
  -e GOOGLE_CALENDAR_TOKEN_PATH=/root/.bird_mcp/google_calendar_token.pickle \
  bird-mcp
```

**Note**: The first time you run with Docker, the OAuth flow may not work automatically. You'll need to:
1. Run the authentication on your host machine first (outside Docker)
2. Then use Docker with the saved token file

## Troubleshooting

### Server Won't Start

**Symptoms:** Server fails to start or crashes immediately

**Solutions:**

1. **Check environment variables**
   ```bash
   # Ensure .env file exists
   ls -la .env

   # Check TODOIST_API_TOKEN is set
   cat .env | grep TODOIST_API_TOKEN
   ```

2. **Check Python version**
   ```bash
   # Requires Python 3.10+
   python --version
   ```

3. **Check dependencies**
   ```bash
   # With uv
   uv sync

   # With pip
   pip install -r requirements.txt
   ```

4. **Check logs**
   ```bash
   # Run server directly to see errors
   python -m bird_mcp.server

   # Look for error messages in output
   ```

5. **Verify package installation**
   ```bash
   # Check if package is installed
   pip list | grep bird-mcp

   # Reinstall if missing
   pip install -e .
   ```

### Claude Code Issues

**Symptoms:** Claude Code can't find or connect to the MCP server

**Solutions:**

1. **Verify server is configured**
   ```bash
   # List configured servers
   claude mcp list

   # Should show: bird-personal-assistant: python -m bird_mcp.server - ✓ Connected
   ```

2. **Check you're in the project directory**
   ```bash
   # The server needs to find .env file
   pwd  # Should show /path/to/bird
   ls .env  # Should exist
   ```

3. **Test server manually**
   ```bash
   # Run server to check for errors
   python -m bird_mcp.server

   # Should see initialization logs:
   # INFO - Initializing Todoist integration...
   # INFO - Todoist integration initialized successfully
   ```

4. **Re-add the server**
   ```bash
   # Remove and re-add
   claude mcp remove bird-personal-assistant
   claude mcp add --transport stdio --scope local bird-personal-assistant -- python -m bird_mcp.server
   ```

5. **Check environment variables are accessible**
   ```bash
   # Print environment variable (should show your token)
   echo $TODOIST_API_TOKEN

   # If empty, source .env
   export $(cat .env | xargs)
   ```

### Claude Desktop / Cursor Connection Issues

**Symptoms:** Claude Desktop shows server as disconnected or tools don't appear

**Solutions:**

1. **Verify MCP configuration file location**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Check JSON syntax**
   ```bash
   # Validate JSON syntax
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | python -m json.tool
   ```

3. **Verify Python path**
   ```bash
   # Check which Python is being used
   which python

   # Use absolute path in config if needed
   /full/path/to/python -m bird_mcp.server
   ```

4. **Check environment variables in config**
   - Ensure `TODOIST_API_TOKEN` is set in the `env` section
   - Use absolute paths for `OBSIDIAN_VAULT_PATH`

5. **Restart Claude Desktop**
   - Completely quit Claude Desktop (not just close window)
   - Reopen and check server status

### MCP Client Can't Connect

1. **Verify server is running**: Test with `python -m bird_mcp.server` directly
2. **Check MCP configuration**: Ensure the command and args are correct in your MCP settings
3. **Check environment variables**: Ensure they're set in the MCP configuration or `.env` file
4. **Check Python path**: Ensure the package is installed (`pip install -e .` or `uv pip install -e .`)

### Docker Issues

**Symptoms:** Docker container won't start or crashes

**Solutions:**

1. **Port conflicts** (development mode only)
   ```bash
   # Check if ports are in use
   lsof -i :6274
   lsof -i :6277

   # Kill process using port if needed
   kill -9 <PID>
   ```

2. **Environment variables**
   ```bash
   # Ensure .env file exists
   ls -la .env

   # Check format (no quotes around values)
   cat .env
   ```

3. **Build cache issues**
   ```bash
   # Rebuild without cache
   docker-compose build --no-cache

   # Or with docker directly
   docker build --no-cache -t bird-mcp .
   ```

4. **Volume mount issues** (for Obsidian)
   ```bash
   # Check vault path exists
   ls -la /path/to/obsidian/vault

   # Ensure path is absolute in docker-compose.yml
   # Correct: /Users/username/obsidian_vault:/app/vault:rw
   # Wrong: ~/obsidian_vault:/app/vault:rw
   ```

5. **View container logs**
   ```bash
   # With docker-compose
   docker-compose logs -f bird-mcp

   # With docker
   docker logs bird-mcp
   ```

### Todoist API Issues

**Symptoms:** Todoist tools return errors or fail

**Solutions:**

1. **Verify API token**
   ```bash
   # Get new token from https://todoist.com/app/settings/integrations/developer
   # Update .env file with new token
   ```

2. **Check API rate limits**
   - Todoist has rate limits (varies by plan)
   - Wait a few minutes and try again

3. **Test token manually**
   ```bash
   # Test with curl
   curl https://api.todoist.com/rest/v2/projects \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
   ```

### AnkiConnect Issues

**Symptoms:** Anki tools fail or return connection errors

**Solutions:**

1. **Verify AnkiConnect is installed**
   ```bash
   # Open Anki → Tools → Add-ons
   # Should see "AnkiConnect" in the list
   # Code: 2055492159
   ```

2. **Check Anki is running**
   ```bash
   # Anki must be open for AnkiConnect to work
   # Start Anki application
   ```

3. **Verify port**
   ```bash
   # Test connection
   curl http://localhost:8765

   # Should return AnkiConnect API info
   ```

4. **Check firewall**
   - Some firewalls block localhost connections
   - Allow connections to port 8765

5. **Test with Docker**
   ```bash
   # Use host.docker.internal instead of localhost
   # Already configured in docker-compose.yml
   ```

6. **Use health check**
   ```bash
   # Run health check to test all services
   # In Claude Code:
   "Check the health of my MCP server"
   ```

### Obsidian Integration Issues

**Symptoms:** Obsidian tools return "vault not found" errors

**Solutions:**

1. **Verify vault path**
   ```bash
   # Check path exists
   ls -la /path/to/obsidian/vault

   # Update .env
   OBSIDIAN_VAULT_PATH=/absolute/path/to/vault
   ```

2. **Check path is absolute**
   ```bash
   # Correct: /Users/username/obsidian_vault
   # Wrong: ~/obsidian_vault
   # Wrong: ../obsidian_vault
   ```

3. **Verify permissions**
   ```bash
   # Check read/write permissions
   ls -ld /path/to/obsidian/vault

   # Should show drwxr-xr-x or similar
   ```

4. **Docker vault mounting**
   - Ensure volume is mounted in docker-compose.yml
   - Use absolute paths for host directory
   - Set `OBSIDIAN_VAULT_PATH=/app/vault` inside container

### Common Error Messages

**"ModuleNotFoundError: No module named 'bird_mcp'"**
- Solution: Install package with `pip install -e .` or `uv pip install -e .`

**"Todoist integration disabled"**
- Solution: Set `TODOIST_API_TOKEN` in `.env` file

**"AnkiConnect error: Connection refused"**
- Solution: Start Anki application

**"Vault path does not exist"**
- Solution: Check `OBSIDIAN_VAULT_PATH` is correct absolute path

**"'list' object has no attribute 'id'"**
- This was a bug in earlier versions, ensure you're on latest code

### Getting Help

If you're still experiencing issues:

1. **Check the logs**
   ```bash
   # Run with verbose output
   python -m bird_mcp.server 2>&1 | tee server.log
   ```

2. **Test with health check**
   ```bash
   # In Claude Code, ask:
   "Run a health check on the MCP server"
   ```

3. **Report issues**
   - GitHub Issues: [Create an issue](https://github.com/yourusername/bird/issues)
   - Include logs, error messages, and your setup (OS, Python version, etc.)

## License

MIT
