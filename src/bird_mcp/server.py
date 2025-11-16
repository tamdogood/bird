"""Main MCP server for Bird personal assistant."""

import os
import logging
from typing import Any
from datetime import datetime

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

logger = logging.getLogger(__name__)

# Handle imports for both installed package and direct script execution
import sys
from pathlib import Path

# Add src directory to path if not installed as package
if str(Path(__file__).parent.parent.parent / "src") not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from bird_mcp.todoist_tools import TodoistTools
from bird_mcp.anki_tools import AnkiTools

# Load environment variables
load_dotenv()

logger.info("Bird MCP Server starting...")

# Initialize FastMCP server
mcp = FastMCP("Bird Personal Assistant")

# Initialize integrations
todoist_token = os.getenv("TODOIST_API_TOKEN")
if not todoist_token:
    logger.error("TODOIST_API_TOKEN environment variable is required")
    raise ValueError("TODOIST_API_TOKEN environment variable is required")

logger.info("Initializing Todoist integration...")
todoist = TodoistTools(todoist_token)
logger.info("Todoist integration initialized successfully")

# Initialize Anki (optional - will work even if AnkiConnect is not running)
anki_url = os.getenv("ANKI_CONNECT_URL", "http://localhost:8765")
logger.info(f"Initializing Anki integration at {anki_url}...")
anki = AnkiTools(anki_url)
logger.info("Anki integration initialized (connection will be tested on first use)")


# Health Check Tool

@mcp.tool()
async def health_check() -> dict[str, Any]:
    """Check the health and connectivity of all integrated services.

    Returns status for Todoist, Anki, and future integrations.
    """
    results = {
        "timestamp": datetime.now().isoformat(),
        "services": {}
    }

    # Check Todoist
    try:
        logger.info("Performing Todoist health check...")
        projects = await todoist.get_projects()
        results["services"]["todoist"] = {
            "status": "connected" if projects["success"] else "error",
            "message": "Successfully connected to Todoist" if projects["success"] else projects.get("error"),
            "project_count": projects.get("count", 0) if projects["success"] else None
        }
    except Exception as e:
        logger.error(f"Todoist health check failed: {e}")
        results["services"]["todoist"] = {
            "status": "error",
            "message": str(e)
        }

    # Check Anki
    try:
        logger.info("Performing Anki health check...")
        decks = await anki.get_decks()
        results["services"]["anki"] = {
            "status": "connected" if decks["success"] else "disconnected",
            "message": "Successfully connected to AnkiConnect" if decks["success"] else decks.get("error"),
            "deck_count": decks.get("count", 0) if decks["success"] else None
        }
    except Exception as e:
        logger.error(f"Anki health check failed: {e}")
        results["services"]["anki"] = {
            "status": "error",
            "message": str(e)
        }

    # Overall status
    all_statuses = [svc["status"] for svc in results["services"].values()]
    if all(status == "connected" for status in all_statuses):
        results["overall_status"] = "healthy"
    elif any(status == "connected" for status in all_statuses):
        results["overall_status"] = "degraded"
    else:
        results["overall_status"] = "unhealthy"

    logger.info(f"Health check complete: {results['overall_status']}")
    return results


# Todoist Tools

@mcp.tool()
async def todoist_create_task(
    content: str,
    description: str | None = None,
    project_id: str | None = None,
    due_string: str | None = None,
    priority: int = 1,
    labels: list[str] | None = None,
) -> dict[str, Any]:
    """Create a new task in Todoist.

    Args:
        content: Task title/content
        description: Task description (optional)
        project_id: Project ID to add task to (optional)
        due_string: Due date in natural language (e.g., 'tomorrow', 'next Monday')
        priority: Priority level (1-4, where 4 is highest)
        labels: List of label names
    """
    return await todoist.create_task(
        content=content,
        description=description,
        project_id=project_id,
        due_string=due_string,
        priority=priority,
        labels=labels,
    )


@mcp.tool()
async def todoist_get_tasks(
    project_id: str | None = None,
    label: str | None = None,
    filter_string: str | None = None,
) -> dict[str, Any]:
    """Retrieve tasks from Todoist with optional filters.

    Args:
        project_id: Filter by project ID
        label: Filter by label name
        filter_string: Todoist filter string (e.g., 'today', 'overdue', 'p1')
    """
    return await todoist.get_tasks(
        project_id=project_id,
        label=label,
        filter_string=filter_string,
    )


@mcp.tool()
async def todoist_complete_task(task_id: str) -> dict[str, Any]:
    """Mark a task as completed.

    Args:
        task_id: ID of the task to complete
    """
    return await todoist.complete_task(task_id=task_id)


@mcp.tool()
async def todoist_update_task(
    task_id: str,
    content: str | None = None,
    description: str | None = None,
    due_string: str | None = None,
    priority: int | None = None,
    labels: list[str] | None = None,
) -> dict[str, Any]:
    """Update an existing task.

    Args:
        task_id: ID of the task to update
        content: New task content
        description: New task description
        due_string: New due date in natural language
        priority: New priority level (1-4)
        labels: New labels list
    """
    return await todoist.update_task(
        task_id=task_id,
        content=content,
        description=description,
        due_string=due_string,
        priority=priority,
        labels=labels,
    )


@mcp.tool()
async def todoist_analyze_stats() -> dict[str, Any]:
    """Analyze Todoist tasks and provide comprehensive statistics.

    Returns statistics including priority distribution, project breakdown,
    label usage, and due date analysis.
    """
    return await todoist.analyze_stats()


@mcp.tool()
async def todoist_get_projects() -> dict[str, Any]:
    """Get all Todoist projects."""
    return await todoist.get_projects()


# Anki Tools

@mcp.tool()
async def anki_create_deck(deck_name: str) -> dict[str, Any]:
    """Create a new deck in Anki.

    Args:
        deck_name: Name of the deck to create
    """
    return await anki.create_deck(deck_name=deck_name)


@mcp.tool()
async def anki_get_decks() -> dict[str, Any]:
    """Get all Anki decks."""
    return await anki.get_decks()


@mcp.tool()
async def anki_create_note(
    deck_name: str,
    front: str,
    back: str,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Create a basic flashcard note in Anki with front and back.

    Args:
        deck_name: Name of the deck to add the note to
        front: Front of the card (question/prompt)
        back: Back of the card (answer)
        tags: List of tags to add to the note
    """
    return await anki.create_note(
        deck_name=deck_name,
        front=front,
        back=back,
        tags=tags,
    )


@mcp.tool()
async def anki_create_cloze_note(
    deck_name: str,
    text: str,
    extra: str | None = None,
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Create a cloze deletion flashcard in Anki.

    Use cloze format like: '{{c1::Paris}} is the capital of {{c2::France}}'

    Args:
        deck_name: Name of the deck to add the note to
        text: Text with cloze deletions (use {{c1::text}} format)
        extra: Additional information field (optional)
        tags: List of tags to add to the note
    """
    return await anki.create_cloze_note(
        deck_name=deck_name,
        text=text,
        extra=extra,
        tags=tags,
    )


@mcp.tool()
async def anki_get_deck_stats(deck_name: str) -> dict[str, Any]:
    """Get statistics for a specific Anki deck.

    Returns card counts, review information, and other deck statistics.

    Args:
        deck_name: Name of the deck to get statistics for
    """
    return await anki.get_deck_stats(deck_name=deck_name)


@mcp.tool()
async def anki_get_all_stats() -> dict[str, Any]:
    """Get comprehensive statistics across all Anki decks.

    Returns total cards, new cards, cards due, and per-deck breakdowns.
    """
    return await anki.get_all_stats()


@mcp.tool()
async def anki_update_deck_config(
    deck_name: str,
    new_cards_per_day: int | None = None,
    reviews_per_day: int | None = None,
) -> dict[str, Any]:
    """Update deck configuration settings like daily card limits.

    Args:
        deck_name: Name of the deck to update
        new_cards_per_day: Maximum new cards per day
        reviews_per_day: Maximum reviews per day
    """
    return await anki.update_deck_config(
        deck_name=deck_name,
        new_cards_per_day=new_cards_per_day,
        reviews_per_day=reviews_per_day,
    )


@mcp.tool()
async def anki_find_notes(query: str) -> dict[str, Any]:
    """Find notes using Anki's search syntax.

    Examples: 'deck:French tag:verb', 'is:due'

    Args:
        query: Anki search query
    """
    return await anki.find_notes(query=query)


@mcp.tool()
async def anki_suspend_cards(card_ids: list[int]) -> dict[str, Any]:
    """Suspend cards to prevent them from appearing in reviews.

    Args:
        card_ids: List of card IDs to suspend
    """
    return await anki.suspend_cards(card_ids=card_ids)


@mcp.tool()
async def anki_unsuspend_cards(card_ids: list[int]) -> dict[str, Any]:
    """Unsuspend cards to allow them to appear in reviews again.

    Args:
        card_ids: List of card IDs to unsuspend
    """
    return await anki.unsuspend_cards(card_ids=card_ids)


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
