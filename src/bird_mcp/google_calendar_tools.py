"""Google Calendar integration tools for the Bird MCP server."""

import os
import pickle
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleCalendarTools:
    """Tools for interacting with Google Calendar API."""

    # OAuth2 scopes required for calendar operations
    SCOPES = ["https://www.googleapis.com/auth/calendar"]

    def __init__(
        self,
        credentials_path: str,
        token_path: Optional[str] = None,
    ):
        """
        Initialize Google Calendar tools.

        Args:
            credentials_path: Path to OAuth2 credentials JSON file
            token_path: Path to store/load OAuth2 token (default: ~/.bird_mcp/token.pickle)
        """
        self.credentials_path = credentials_path
        self.token_path = token_path or str(
            Path.home() / ".bird_mcp" / "google_calendar_token.pickle"
        )
        self.service = None
        self._initialize_service()

    def _initialize_service(self) -> None:
        """Initialize Google Calendar API service with OAuth2 authentication."""
        creds = None

        # Load existing token if available
        if os.path.exists(self.token_path):
            with open(self.token_path, "rb") as token:
                creds = pickle.load(token)

        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                # Refresh expired token
                creds.refresh(Request())
            else:
                # Run OAuth2 flow for new token
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file not found at {self.credentials_path}. "
                        "Please download OAuth2 credentials from Google Cloud Console."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, self.SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save the token for future use
            os.makedirs(os.path.dirname(self.token_path), exist_ok=True)
            with open(self.token_path, "wb") as token:
                pickle.dump(creds, token)

        # Build the Calendar API service
        self.service = build("calendar", "v3", credentials=creds)

    async def list_calendars(self) -> dict[str, Any]:
        """
        List all calendars available to the user.

        Returns:
            Dictionary with success status and list of calendars
        """
        try:
            calendar_list = self.service.calendarList().list().execute()
            calendars = [
                {
                    "id": cal["id"],
                    "summary": cal["summary"],
                    "primary": cal.get("primary", False),
                    "access_role": cal.get("accessRole"),
                    "background_color": cal.get("backgroundColor"),
                    "foreground_color": cal.get("foregroundColor"),
                }
                for cal in calendar_list.get("items", [])
            ]
            return {
                "success": True,
                "calendars": calendars,
                "count": len(calendars),
            }
        except HttpError as e:
            return {"success": False, "error": f"HTTP error: {e.reason}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def create_event(
        self,
        summary: str,
        start_time: str,
        end_time: str,
        calendar_id: str = "primary",
        description: Optional[str] = None,
        location: Optional[str] = None,
        attendees: Optional[list[str]] = None,
        timezone: str = "UTC",
    ) -> dict[str, Any]:
        """
        Create a new calendar event.

        Args:
            summary: Event title
            start_time: Start time in ISO format (e.g., "2025-11-16T10:00:00")
            end_time: End time in ISO format
            calendar_id: Calendar ID (default: "primary")
            description: Event description
            location: Event location
            attendees: List of attendee email addresses
            timezone: Timezone for the event (default: "UTC")

        Returns:
            Dictionary with success status and created event details
        """
        try:
            event = {
                "summary": summary,
                "start": {
                    "dateTime": start_time,
                    "timeZone": timezone,
                },
                "end": {
                    "dateTime": end_time,
                    "timeZone": timezone,
                },
            }

            if description:
                event["description"] = description
            if location:
                event["location"] = location
            if attendees:
                event["attendees"] = [{"email": email} for email in attendees]

            created_event = (
                self.service.events()
                .insert(calendarId=calendar_id, body=event)
                .execute()
            )

            return {
                "success": True,
                "event": {
                    "id": created_event["id"],
                    "summary": created_event["summary"],
                    "start": created_event["start"].get("dateTime"),
                    "end": created_event["end"].get("dateTime"),
                    "html_link": created_event.get("htmlLink"),
                    "status": created_event.get("status"),
                },
                "message": f"Event '{summary}' created successfully",
            }
        except HttpError as e:
            return {"success": False, "error": f"HTTP error: {e.reason}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_events(
        self,
        time_min: Optional[str] = None,
        time_max: Optional[str] = None,
        calendar_id: str = "primary",
        max_results: int = 10,
        single_events: bool = True,
    ) -> dict[str, Any]:
        """
        Get events within a specified time range.

        Args:
            time_min: Start of time range in ISO format (default: now)
            time_max: End of time range in ISO format
            calendar_id: Calendar ID (default: "primary")
            max_results: Maximum number of events to return (default: 10)
            single_events: Expand recurring events (default: True)

        Returns:
            Dictionary with success status and list of events
        """
        try:
            # Default to current time if not specified
            if not time_min:
                time_min = datetime.utcnow().isoformat() + "Z"

            events_result = (
                self.service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=time_min,
                    timeMax=time_max,
                    maxResults=max_results,
                    singleEvents=single_events,
                    orderBy="startTime" if single_events else None,
                )
                .execute()
            )

            events = [
                {
                    "id": event["id"],
                    "summary": event.get("summary", "No title"),
                    "start": event["start"].get("dateTime", event["start"].get("date")),
                    "end": event["end"].get("dateTime", event["end"].get("date")),
                    "description": event.get("description"),
                    "location": event.get("location"),
                    "status": event.get("status"),
                    "html_link": event.get("htmlLink"),
                }
                for event in events_result.get("items", [])
            ]

            return {
                "success": True,
                "events": events,
                "count": len(events),
            }
        except HttpError as e:
            return {"success": False, "error": f"HTTP error: {e.reason}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def update_event(
        self,
        event_id: str,
        calendar_id: str = "primary",
        summary: Optional[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        description: Optional[str] = None,
        location: Optional[str] = None,
        timezone: str = "UTC",
    ) -> dict[str, Any]:
        """
        Update an existing calendar event.

        Args:
            event_id: Event ID to update
            calendar_id: Calendar ID (default: "primary")
            summary: New event title
            start_time: New start time in ISO format
            end_time: New end time in ISO format
            description: New description
            location: New location
            timezone: Timezone for the event (default: "UTC")

        Returns:
            Dictionary with success status and updated event details
        """
        try:
            # Get existing event
            event = (
                self.service.events()
                .get(calendarId=calendar_id, eventId=event_id)
                .execute()
            )

            # Update fields
            if summary:
                event["summary"] = summary
            if start_time:
                event["start"] = {"dateTime": start_time, "timeZone": timezone}
            if end_time:
                event["end"] = {"dateTime": end_time, "timeZone": timezone}
            if description is not None:
                event["description"] = description
            if location is not None:
                event["location"] = location

            updated_event = (
                self.service.events()
                .update(calendarId=calendar_id, eventId=event_id, body=event)
                .execute()
            )

            return {
                "success": True,
                "event": {
                    "id": updated_event["id"],
                    "summary": updated_event["summary"],
                    "start": updated_event["start"].get("dateTime"),
                    "end": updated_event["end"].get("dateTime"),
                    "html_link": updated_event.get("htmlLink"),
                },
                "message": f"Event updated successfully",
            }
        except HttpError as e:
            return {"success": False, "error": f"HTTP error: {e.reason}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def delete_event(
        self,
        event_id: str,
        calendar_id: str = "primary",
    ) -> dict[str, Any]:
        """
        Delete a calendar event.

        Args:
            event_id: Event ID to delete
            calendar_id: Calendar ID (default: "primary")

        Returns:
            Dictionary with success status
        """
        try:
            self.service.events().delete(
                calendarId=calendar_id, eventId=event_id
            ).execute()
            return {
                "success": True,
                "message": f"Event {event_id} deleted successfully",
            }
        except HttpError as e:
            return {"success": False, "error": f"HTTP error: {e.reason}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def find_free_slots(
        self,
        time_min: str,
        time_max: str,
        duration_minutes: int = 60,
        calendar_id: str = "primary",
    ) -> dict[str, Any]:
        """
        Find available time slots in the calendar.

        Args:
            time_min: Start of time range in ISO format
            time_max: End of time range in ISO format
            duration_minutes: Desired duration in minutes (default: 60)
            calendar_id: Calendar ID (default: "primary")

        Returns:
            Dictionary with success status and list of free time slots
        """
        try:
            # Get all events in the time range
            events_result = await self.get_events(
                time_min=time_min,
                time_max=time_max,
                calendar_id=calendar_id,
                max_results=100,
            )

            if not events_result["success"]:
                return events_result

            events = events_result["events"]

            # Parse time boundaries
            start_dt = datetime.fromisoformat(time_min.replace("Z", "+00:00"))
            end_dt = datetime.fromisoformat(time_max.replace("Z", "+00:00"))

            # Create list of busy periods
            busy_periods = []
            for event in events:
                event_start = datetime.fromisoformat(
                    event["start"].replace("Z", "+00:00")
                )
                event_end = datetime.fromisoformat(event["end"].replace("Z", "+00:00"))
                busy_periods.append((event_start, event_end))

            # Sort busy periods by start time
            busy_periods.sort()

            # Find free slots
            free_slots = []
            current_time = start_dt

            for busy_start, busy_end in busy_periods:
                # Check if there's a gap before this busy period
                if current_time < busy_start:
                    gap_duration = (busy_start - current_time).total_seconds() / 60
                    if gap_duration >= duration_minutes:
                        free_slots.append(
                            {
                                "start": current_time.isoformat(),
                                "end": busy_start.isoformat(),
                                "duration_minutes": int(gap_duration),
                            }
                        )
                current_time = max(current_time, busy_end)

            # Check for free time after the last event
            if current_time < end_dt:
                gap_duration = (end_dt - current_time).total_seconds() / 60
                if gap_duration >= duration_minutes:
                    free_slots.append(
                        {
                            "start": current_time.isoformat(),
                            "end": end_dt.isoformat(),
                            "duration_minutes": int(gap_duration),
                        }
                    )

            return {
                "success": True,
                "free_slots": free_slots,
                "count": len(free_slots),
                "duration_minutes": duration_minutes,
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def quick_add(
        self,
        text: str,
        calendar_id: str = "primary",
    ) -> dict[str, Any]:
        """
        Create an event using natural language (Google's Quick Add feature).

        Args:
            text: Natural language event description (e.g., "Lunch with John tomorrow at 12pm")
            calendar_id: Calendar ID (default: "primary")

        Returns:
            Dictionary with success status and created event details
        """
        try:
            event = (
                self.service.events()
                .quickAdd(calendarId=calendar_id, text=text)
                .execute()
            )

            return {
                "success": True,
                "event": {
                    "id": event["id"],
                    "summary": event.get("summary"),
                    "start": event["start"].get("dateTime", event["start"].get("date")),
                    "end": event["end"].get("dateTime", event["end"].get("date")),
                    "html_link": event.get("htmlLink"),
                },
                "message": f"Event created from text: '{text}'",
            }
        except HttpError as e:
            return {"success": False, "error": f"HTTP error: {e.reason}"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_today_events(
        self,
        calendar_id: str = "primary",
    ) -> dict[str, Any]:
        """
        Get all events for today.

        Args:
            calendar_id: Calendar ID (default: "primary")

        Returns:
            Dictionary with success status and list of today's events
        """
        try:
            # Get today's date range
            now = datetime.utcnow()
            today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
            today_end = today_start + timedelta(days=1)

            time_min = today_start.isoformat() + "Z"
            time_max = today_end.isoformat() + "Z"

            return await self.get_events(
                time_min=time_min,
                time_max=time_max,
                calendar_id=calendar_id,
                max_results=50,
            )
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_upcoming_events(
        self,
        days: int = 7,
        calendar_id: str = "primary",
        max_results: int = 20,
    ) -> dict[str, Any]:
        """
        Get upcoming events for the next N days.

        Args:
            days: Number of days to look ahead (default: 7)
            calendar_id: Calendar ID (default: "primary")
            max_results: Maximum number of events to return (default: 20)

        Returns:
            Dictionary with success status and list of upcoming events
        """
        try:
            now = datetime.utcnow()
            future = now + timedelta(days=days)

            time_min = now.isoformat() + "Z"
            time_max = future.isoformat() + "Z"

            return await self.get_events(
                time_min=time_min,
                time_max=time_max,
                calendar_id=calendar_id,
                max_results=max_results,
            )
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def block_study_time(
        self,
        subject: str,
        start_time: str,
        duration_minutes: int = 60,
        calendar_id: str = "primary",
        timezone: str = "UTC",
    ) -> dict[str, Any]:
        """
        Create a study block event for learning workflows.

        Args:
            subject: Study subject (e.g., "French Grammar", "AI Course")
            start_time: Start time in ISO format
            duration_minutes: Duration in minutes (default: 60)
            calendar_id: Calendar ID (default: "primary")
            timezone: Timezone for the event (default: "UTC")

        Returns:
            Dictionary with success status and created event details
        """
        try:
            # Calculate end time
            start_dt = datetime.fromisoformat(start_time.replace("Z", ""))
            end_dt = start_dt + timedelta(minutes=duration_minutes)

            # Create study block event
            summary = f"Study: {subject}"
            description = f"Focused study session for {subject}\nDuration: {duration_minutes} minutes"

            return await self.create_event(
                summary=summary,
                start_time=start_dt.isoformat(),
                end_time=end_dt.isoformat(),
                calendar_id=calendar_id,
                description=description,
                timezone=timezone,
            )
        except Exception as e:
            return {"success": False, "error": str(e)}
