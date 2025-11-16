"""Main MCP server for Bird personal assistant."""

import os
import sys
import logging
from typing import Any
from datetime import datetime
from pathlib import Path

from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Configure logging to stderr to avoid interfering with MCP protocol (stdout)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(stream=sys.stderr)],
)

logger = logging.getLogger(__name__)

# Handle imports for both installed package and direct script execution

# Add src directory to path if not installed as package
if str(Path(__file__).parent.parent.parent / "src") not in sys.path:
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from bird_mcp.todoist_tools import TodoistTools
from bird_mcp.anki_tools import AnkiTools
from bird_mcp.obsidian_tools import ObsidianTools
from bird_mcp.google_calendar_tools import GoogleCalendarTools

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

# Initialize Obsidian (optional)
obsidian_vault = os.getenv("OBSIDIAN_VAULT_PATH")
obsidian = None
if obsidian_vault:
    try:
        logger.info(f"Initializing Obsidian integration at {obsidian_vault}...")
        obsidian = ObsidianTools(obsidian_vault)
        logger.info("Obsidian integration initialized successfully")
    except Exception as e:
        logger.warning(f"Obsidian integration disabled: {e}")
else:
    logger.info("Obsidian integration disabled (OBSIDIAN_VAULT_PATH not set)")

# Initialize Google Calendar (optional)
gcal_credentials = os.getenv("GOOGLE_CALENDAR_CREDENTIALS_PATH")
gcal_token = os.getenv("GOOGLE_CALENDAR_TOKEN_PATH")
google_calendar = None
if gcal_credentials:
    try:
        logger.info(f"Initializing Google Calendar integration...")
        google_calendar = GoogleCalendarTools(
            credentials_path=gcal_credentials,
            token_path=gcal_token,
        )
        logger.info("Google Calendar integration initialized successfully")
    except Exception as e:
        logger.warning(f"Google Calendar integration disabled: {e}")
else:
    logger.info("Google Calendar integration disabled (GOOGLE_CALENDAR_CREDENTIALS_PATH not set)")


# Health Check Tool


@mcp.tool()
async def health_check() -> dict[str, Any]:
    """Check the health and connectivity of all integrated services.

    Returns status for Todoist, Anki, and future integrations.
    """
    results = {"timestamp": datetime.now().isoformat(), "services": {}}

    # Check Todoist
    try:
        logger.info("Performing Todoist health check...")
        projects = await todoist.get_projects()
        results["services"]["todoist"] = {
            "status": "connected" if projects["success"] else "error",
            "message": (
                "Successfully connected to Todoist"
                if projects["success"]
                else projects.get("error")
            ),
            "project_count": projects.get("count", 0) if projects["success"] else None,
        }
    except Exception as e:
        logger.error(f"Todoist health check failed: {e}")
        results["services"]["todoist"] = {"status": "error", "message": str(e)}

    # Check Anki
    try:
        logger.info("Performing Anki health check...")
        decks = await anki.get_decks()
        results["services"]["anki"] = {
            "status": "connected" if decks["success"] else "disconnected",
            "message": (
                "Successfully connected to AnkiConnect" if decks["success"] else decks.get("error")
            ),
            "deck_count": decks.get("count", 0) if decks["success"] else None,
        }
    except Exception as e:
        logger.error(f"Anki health check failed: {e}")
        results["services"]["anki"] = {"status": "error", "message": str(e)}

    # Check Obsidian
    if obsidian:
        try:
            logger.info("Performing Obsidian health check...")
            stats = await obsidian.get_vault_stats()
            results["services"]["obsidian"] = {
                "status": "connected" if stats["success"] else "error",
                "message": (
                    "Successfully connected to Obsidian vault"
                    if stats["success"]
                    else stats.get("error")
                ),
                "note_count": stats["stats"].get("total_notes", 0) if stats["success"] else None,
            }
        except Exception as e:
            logger.error(f"Obsidian health check failed: {e}")
            results["services"]["obsidian"] = {"status": "error", "message": str(e)}
    else:
        results["services"]["obsidian"] = {
            "status": "disabled",
            "message": "Obsidian integration not configured (set OBSIDIAN_VAULT_PATH)",
        }

    # Check Google Calendar
    if google_calendar:
        try:
            logger.info("Performing Google Calendar health check...")
            calendars = await google_calendar.list_calendars()
            results["services"]["google_calendar"] = {
                "status": "connected" if calendars["success"] else "error",
                "message": (
                    "Successfully connected to Google Calendar"
                    if calendars["success"]
                    else calendars.get("error")
                ),
                "calendar_count": calendars.get("count", 0) if calendars["success"] else None,
            }
        except Exception as e:
            logger.error(f"Google Calendar health check failed: {e}")
            results["services"]["google_calendar"] = {"status": "error", "message": str(e)}
    else:
        results["services"]["google_calendar"] = {
            "status": "disabled",
            "message": "Google Calendar integration not configured (set GOOGLE_CALENDAR_CREDENTIALS_PATH)",
        }

    # Overall status
    all_statuses = [
        svc["status"] for svc in results["services"].values() if svc["status"] != "disabled"
    ]
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
    labels: list[str] = [],
) -> dict[str, Any]:
    """Create a new task in Todoist.

    Args:
        content: Task title/content
        description: Task description (optional)
        project_id: Project ID to add task to (optional)
        due_string: Due date in natural language (e.g., 'tomorrow', 'next Monday')
        priority: Priority level (1-4, where 4 is highest)
        labels: List of label names (default: empty list)
    """
    logger.info(f"Creating task with content='{content}', labels={labels}")
    return await todoist.create_task(
        content=content,
        description=description,
        project_id=project_id,
        due_string=due_string,
        priority=priority,
        labels=labels if labels else None,
    )


@mcp.tool()
async def todoist_get_tasks(
    project_id: str | None = None,
    label: str | None = None,
) -> dict[str, Any]:
    """Retrieve tasks from Todoist with optional filters.

    Args:
        project_id: Filter by project ID
        label: Filter by label name

    Note: Advanced filtering via filter strings was removed in todoist-api-python v3.x
    """
    return await todoist.get_tasks(
        project_id=project_id,
        label=label,
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
    labels: list[str] = [],
) -> dict[str, Any]:
    """Update an existing task.

    Args:
        task_id: ID of the task to update
        content: New task content
        description: New task description
        due_string: New due date in natural language
        priority: New priority level (1-4)
        labels: New labels list (empty list means no change)
    """
    logger.info(f"Updating task {task_id} with labels={labels}")
    return await todoist.update_task(
        task_id=task_id,
        content=content,
        description=description,
        due_string=due_string,
        priority=priority,
        labels=labels if labels else None,
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


@mcp.tool()
async def todoist_delete_task(task_id: str) -> dict[str, Any]:
    """Permanently delete a task.

    Args:
        task_id: ID of the task to delete
    """
    return await todoist.delete_task(task_id=task_id)


@mcp.tool()
async def todoist_get_comments(task_id: str) -> dict[str, Any]:
    """Get all comments for a task.

    Args:
        task_id: ID of the task
    """
    return await todoist.get_comments(task_id=task_id)


@mcp.tool()
async def todoist_add_comment(task_id: str, content: str) -> dict[str, Any]:
    """Add a comment to a task.

    Args:
        task_id: ID of the task
        content: Comment text
    """
    return await todoist.add_comment(task_id=task_id, content=content)


@mcp.tool()
async def todoist_get_labels() -> dict[str, Any]:
    """Get all available Todoist labels."""
    return await todoist.get_labels()


@mcp.tool()
async def todoist_get_sections(project_id: str | None = None) -> dict[str, Any]:
    """Get sections, optionally filtered by project.

    Args:
        project_id: Project ID to filter sections (optional)
    """
    return await todoist.get_sections(project_id=project_id)


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


@mcp.tool()
async def anki_get_note_types() -> dict[str, Any]:
    """Get all available note types (models) in Anki.

    Returns list of note type names like "Basic", "Cloze", etc.
    """
    return await anki.get_note_types()


@mcp.tool()
async def anki_update_note(
    note_id: int,
    fields: dict[str, str],
    tags: list[str] | None = None,
) -> dict[str, Any]:
    """Update an existing Anki note's fields and tags.

    Args:
        note_id: ID of the note to update
        fields: Dictionary of field names to new values (e.g., {"Front": "new question", "Back": "new answer"})
        tags: New tags to replace existing tags (optional)
    """
    return await anki.update_note(note_id=note_id, fields=fields, tags=tags)


@mcp.tool()
async def anki_get_note_info(note_ids: list[int]) -> dict[str, Any]:
    """Get detailed information about specific notes.

    Args:
        note_ids: List of note IDs to retrieve information for
    """
    return await anki.get_note_info(note_ids=note_ids)


@mcp.tool()
async def anki_delete_notes(note_ids: list[int]) -> dict[str, Any]:
    """Permanently delete notes from Anki.

    Args:
        note_ids: List of note IDs to delete
    """
    return await anki.delete_notes(note_ids=note_ids)


# Obsidian Tools


@mcp.tool()
async def obsidian_create_note(
    title: str,
    content: str,
    folder: str = "",
    tags: list[str] | None = None,
    frontmatter: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a new note in Obsidian vault.

    Args:
        title: Note title (becomes filename)
        content: Note content in markdown
        folder: Subfolder path (e.g., "6 - main notes")
        tags: List of tags
        frontmatter: Additional YAML frontmatter fields
    """
    if not obsidian:
        return {"success": False, "error": "Obsidian integration not configured"}
    return await obsidian.create_note(title, content, folder, tags, frontmatter)


@mcp.tool()
async def obsidian_read_note(note_path: str) -> dict[str, Any]:
    """Read a note from Obsidian vault.

    Args:
        note_path: Relative path from vault root (e.g., "6 - main notes/My Note.md")
    """
    if not obsidian:
        return {"success": False, "error": "Obsidian integration not configured"}
    return await obsidian.read_note(note_path)


@mcp.tool()
async def obsidian_update_note(
    note_path: str,
    content: str | None = None,
    frontmatter: dict[str, Any] | None = None,
    append: bool = False,
) -> dict[str, Any]:
    """Update an existing note in Obsidian vault.

    Args:
        note_path: Relative path to note
        content: New content (or content to append if append=True)
        frontmatter: New/updated frontmatter fields
        append: If True, append content instead of replacing
    """
    if not obsidian:
        return {"success": False, "error": "Obsidian integration not configured"}
    return await obsidian.update_note(note_path, content, frontmatter, append)


@mcp.tool()
async def obsidian_delete_note(note_path: str) -> dict[str, Any]:
    """Delete a note from Obsidian vault.

    Args:
        note_path: Relative path to note
    """
    if not obsidian:
        return {"success": False, "error": "Obsidian integration not configured"}
    return await obsidian.delete_note(note_path)


@mcp.tool()
async def obsidian_search_notes(
    query: str,
    folder: str | None = None,
    tag: str | None = None,
) -> dict[str, Any]:
    """Search notes in Obsidian vault.

    Args:
        query: Text to search for in note content
        folder: Limit search to specific folder
        tag: Filter by tag
    """
    if not obsidian:
        return {"success": False, "error": "Obsidian integration not configured"}
    return await obsidian.search_notes(query, folder, tag)


@mcp.tool()
async def obsidian_list_notes(
    folder: str = "",
    recursive: bool = True,
) -> dict[str, Any]:
    """List all notes in Obsidian vault or specific folder.

    Args:
        folder: Folder to list (empty = root)
        recursive: Include subfolders
    """
    if not obsidian:
        return {"success": False, "error": "Obsidian integration not configured"}
    return await obsidian.list_notes(folder, recursive)


@mcp.tool()
async def obsidian_get_daily_note(date: str | None = None) -> dict[str, Any]:
    """Get or create daily note for a specific date.

    Args:
        date: Date in YYYY-MM-DD format (default: today)
    """
    if not obsidian:
        return {"success": False, "error": "Obsidian integration not configured"}
    return await obsidian.get_daily_note(date)


@mcp.tool()
async def obsidian_get_vault_stats() -> dict[str, Any]:
    """Get statistics about the Obsidian vault.

    Returns total notes, size, and folder distribution.
    """
    if not obsidian:
        return {"success": False, "error": "Obsidian integration not configured"}
    return await obsidian.get_vault_stats()


# Google Calendar Tools


@mcp.tool()
async def google_calendar_list_calendars() -> dict[str, Any]:
    """List all available Google Calendars.

    Returns list of calendars with their IDs, names, and access roles.
    """
    if not google_calendar:
        return {"success": False, "error": "Google Calendar integration not configured"}
    return await google_calendar.list_calendars()


@mcp.tool()
async def google_calendar_create_event(
    summary: str,
    start_time: str,
    end_time: str,
    calendar_id: str = "primary",
    description: str | None = None,
    location: str | None = None,
    attendees: list[str] | None = None,
    timezone: str = "UTC",
) -> dict[str, Any]:
    """Create a new calendar event.

    Args:
        summary: Event title
        start_time: Start time in ISO format (e.g., "2025-11-16T10:00:00")
        end_time: End time in ISO format (e.g., "2025-11-16T11:00:00")
        calendar_id: Calendar ID (default: "primary" for main calendar)
        description: Event description (optional)
        location: Event location (optional)
        attendees: List of attendee email addresses (optional)
        timezone: Timezone for the event (default: "UTC")
    """
    if not google_calendar:
        return {"success": False, "error": "Google Calendar integration not configured"}
    return await google_calendar.create_event(
        summary=summary,
        start_time=start_time,
        end_time=end_time,
        calendar_id=calendar_id,
        description=description,
        location=location,
        attendees=attendees,
        timezone=timezone,
    )


@mcp.tool()
async def google_calendar_get_events(
    time_min: str | None = None,
    time_max: str | None = None,
    calendar_id: str = "primary",
    max_results: int = 10,
) -> dict[str, Any]:
    """Get events within a specified time range.

    Args:
        time_min: Start of time range in ISO format (default: now)
        time_max: End of time range in ISO format (optional)
        calendar_id: Calendar ID (default: "primary")
        max_results: Maximum number of events to return (default: 10)
    """
    if not google_calendar:
        return {"success": False, "error": "Google Calendar integration not configured"}
    return await google_calendar.get_events(
        time_min=time_min,
        time_max=time_max,
        calendar_id=calendar_id,
        max_results=max_results,
    )


@mcp.tool()
async def google_calendar_update_event(
    event_id: str,
    calendar_id: str = "primary",
    summary: str | None = None,
    start_time: str | None = None,
    end_time: str | None = None,
    description: str | None = None,
    location: str | None = None,
    timezone: str = "UTC",
) -> dict[str, Any]:
    """Update an existing calendar event.

    Args:
        event_id: Event ID to update
        calendar_id: Calendar ID (default: "primary")
        summary: New event title (optional)
        start_time: New start time in ISO format (optional)
        end_time: New end time in ISO format (optional)
        description: New description (optional)
        location: New location (optional)
        timezone: Timezone for the event (default: "UTC")
    """
    if not google_calendar:
        return {"success": False, "error": "Google Calendar integration not configured"}
    return await google_calendar.update_event(
        event_id=event_id,
        calendar_id=calendar_id,
        summary=summary,
        start_time=start_time,
        end_time=end_time,
        description=description,
        location=location,
        timezone=timezone,
    )


@mcp.tool()
async def google_calendar_delete_event(
    event_id: str,
    calendar_id: str = "primary",
) -> dict[str, Any]:
    """Delete a calendar event.

    Args:
        event_id: Event ID to delete
        calendar_id: Calendar ID (default: "primary")
    """
    if not google_calendar:
        return {"success": False, "error": "Google Calendar integration not configured"}
    return await google_calendar.delete_event(
        event_id=event_id,
        calendar_id=calendar_id,
    )


@mcp.tool()
async def google_calendar_find_free_slots(
    time_min: str,
    time_max: str,
    duration_minutes: int = 60,
    calendar_id: str = "primary",
) -> dict[str, Any]:
    """Find available time slots in the calendar.

    Args:
        time_min: Start of time range in ISO format
        time_max: End of time range in ISO format
        duration_minutes: Desired duration in minutes (default: 60)
        calendar_id: Calendar ID (default: "primary")
    """
    if not google_calendar:
        return {"success": False, "error": "Google Calendar integration not configured"}
    return await google_calendar.find_free_slots(
        time_min=time_min,
        time_max=time_max,
        duration_minutes=duration_minutes,
        calendar_id=calendar_id,
    )


@mcp.tool()
async def google_calendar_quick_add(
    text: str,
    calendar_id: str = "primary",
) -> dict[str, Any]:
    """Create an event using natural language.

    Uses Google's Quick Add feature to parse natural language and create events.

    Args:
        text: Natural language event description (e.g., "Lunch with John tomorrow at 12pm")
        calendar_id: Calendar ID (default: "primary")
    """
    if not google_calendar:
        return {"success": False, "error": "Google Calendar integration not configured"}
    return await google_calendar.quick_add(
        text=text,
        calendar_id=calendar_id,
    )


@mcp.tool()
async def google_calendar_get_today_events(
    calendar_id: str = "primary",
) -> dict[str, Any]:
    """Get all events for today.

    Args:
        calendar_id: Calendar ID (default: "primary")
    """
    if not google_calendar:
        return {"success": False, "error": "Google Calendar integration not configured"}
    return await google_calendar.get_today_events(calendar_id=calendar_id)


@mcp.tool()
async def google_calendar_get_upcoming_events(
    days: int = 7,
    calendar_id: str = "primary",
    max_results: int = 20,
) -> dict[str, Any]:
    """Get upcoming events for the next N days.

    Args:
        days: Number of days to look ahead (default: 7)
        calendar_id: Calendar ID (default: "primary")
        max_results: Maximum number of events to return (default: 20)
    """
    if not google_calendar:
        return {"success": False, "error": "Google Calendar integration not configured"}
    return await google_calendar.get_upcoming_events(
        days=days,
        calendar_id=calendar_id,
        max_results=max_results,
    )


@mcp.tool()
async def google_calendar_block_study_time(
    subject: str,
    start_time: str,
    duration_minutes: int = 60,
    calendar_id: str = "primary",
    timezone: str = "UTC",
) -> dict[str, Any]:
    """Create a study block event for learning workflows.

    Designed to integrate with learning workflows - creates focused study time blocks.

    Args:
        subject: Study subject (e.g., "French Grammar", "AI Course")
        start_time: Start time in ISO format
        duration_minutes: Duration in minutes (default: 60)
        calendar_id: Calendar ID (default: "primary")
        timezone: Timezone for the event (default: "UTC")
    """
    if not google_calendar:
        return {"success": False, "error": "Google Calendar integration not configured"}
    return await google_calendar.block_study_time(
        subject=subject,
        start_time=start_time,
        duration_minutes=duration_minutes,
        calendar_id=calendar_id,
        timezone=timezone,
    )


def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
