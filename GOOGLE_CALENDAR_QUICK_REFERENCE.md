# Google Calendar - Quick Reference Card

Quick reference for Google Calendar integration in Bird MCP server.

## Setup (One-Time)

```bash
# 1. Install dependencies
pip install -e .

# 2. Set environment variable in .env
GOOGLE_CALENDAR_CREDENTIALS_PATH=/path/to/credentials.json

# 3. Run server (browser opens for OAuth)
python -m bird_mcp.server

# 4. Sign in to Google and grant permissions
# Token saved to ~/.bird_mcp/google_calendar_token.pickle
```

For detailed setup: See `GOOGLE_CALENDAR_SETUP.md`

## 10 Available Tools

| Tool | Purpose | Example |
|------|---------|---------|
| `google_calendar_list_calendars` | List all calendars | "List my calendars" |
| `google_calendar_create_event` | Create new event | "Create event tomorrow 2pm-3pm" |
| `google_calendar_get_events` | Get events in time range | "Show events this week" |
| `google_calendar_update_event` | Modify existing event | "Update event to 3pm" |
| `google_calendar_delete_event` | Delete event | "Delete event abc123" |
| `google_calendar_find_free_slots` | Find available time | "Find 1-hour slots tomorrow" |
| `google_calendar_quick_add` | Natural language event | "Quick add: Lunch at noon" |
| `google_calendar_get_today_events` | Today's schedule | "What's on my calendar today?" |
| `google_calendar_get_upcoming_events` | Next N days | "Show next 7 days" |
| `google_calendar_block_study_time` | Create study block | "Block French study 7pm 90min" |

## Common Commands

### Daily Workflow
```
"What's on my calendar today?"
"Find free time this afternoon"
"Block 1 hour for study at 7pm"
```

### Event Creation
```
"Create calendar event 'Team Meeting' tomorrow 2-3pm"
"Quick add: Dentist appointment Friday at 2pm"
"Block study time for AI tomorrow at 8am for 2 hours"
```

### Planning
```
"Show my calendar for next week"
"Find 90-minute free slots between 9am-5pm tomorrow"
"Get upcoming events for the next 14 days"
```

### Integration
```
"Check my calendar and Todoist tasks for conflicts"
"Block study time based on my Anki review schedule"
"Add today's events to my Obsidian daily note"
```

## Time Format

### ISO 8601 (Precise)
```
"2025-11-20T14:00:00"  # 2pm on Nov 20, 2025
"2025-12-01T09:30:00"  # 9:30am on Dec 1, 2025
```

### Natural Language (Quick Add)
```
"tomorrow at 2pm"
"next Monday at 9am"
"December 1st at noon"
"every weekday at 10am"
```

## Calendar IDs

- `"primary"` - Your main Google Calendar (default)
- Custom IDs from: `google_calendar_list_calendars`

## Common Parameters

### Create Event
- **summary** (required): Event title
- **start_time** (required): ISO format or natural language
- **end_time** (required): ISO format or natural language
- **description** (optional): Event details
- **location** (optional): Where it happens
- **attendees** (optional): List of email addresses
- **calendar_id** (optional): Default "primary"
- **timezone** (optional): Default "UTC"

### Find Free Slots
- **time_min** (required): Start of search range
- **time_max** (required): End of search range
- **duration_minutes** (optional): Minimum slot size, default 60
- **calendar_id** (optional): Default "primary"

### Get Events
- **time_min** (optional): Start time, default now
- **time_max** (optional): End time
- **max_results** (optional): Limit results, default 10
- **calendar_id** (optional): Default "primary"

## Response Format

All tools return:
```json
{
  "success": true/false,
  "data": {...},
  "error": "..." (if success=false)
}
```

### Event Object
```json
{
  "id": "abc123xyz",
  "summary": "Team Meeting",
  "start": "2025-11-20T14:00:00+00:00",
  "end": "2025-11-20T15:00:00+00:00",
  "description": "Q4 planning",
  "location": "Conference Room A",
  "html_link": "https://calendar.google.com/...",
  "status": "confirmed"
}
```

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| "Google Calendar integration not configured" | No credentials | Set GOOGLE_CALENDAR_CREDENTIALS_PATH |
| "Credentials file not found" | Wrong path | Use absolute path |
| "HTTP error: Not Found" | Invalid event ID | List events to get correct ID |
| "Access blocked" | Not a test user | Add email in OAuth consent screen |
| "Token expired" | Token revoked | Delete token file, re-authenticate |

## Timezones

Common timezone strings:
- `"UTC"` - Coordinated Universal Time
- `"America/New_York"` - Eastern Time
- `"America/Los_Angeles"` - Pacific Time
- `"Europe/London"` - British Time
- `"Europe/Paris"` - Central European Time
- `"Asia/Tokyo"` - Japan Time

Full list: [IANA Time Zone Database](https://en.wikipedia.org/wiki/List_of_tz_database_time_zones)

## Authentication

### Token Location
Default: `~/.bird_mcp/google_calendar_token.pickle`

### Re-authenticate
```bash
# Delete token
rm ~/.bird_mcp/google_calendar_token.pickle

# Restart server (browser opens)
python -m bird_mcp.server
```

### Revoke Access
1. Delete token file
2. Go to [Google Account Permissions](https://myaccount.google.com/permissions)
3. Remove "Bird MCP Server"

## Integration Examples

### With Todoist
```
"Create Todoist task and calendar event for meeting tomorrow at 2pm"
"Show Todoist tasks and block calendar time for high-priority ones"
```

### With Anki
```
"Check Anki stats and block study time for reviews"
"Block 30 minutes daily for Anki based on cards due"
```

### With Obsidian
```
"Get today's events and add to my Obsidian daily note"
"Create calendar blocks based on my Obsidian weekly plan"
```

### Complete Workflow
```
"Plan my study week:
1. Show calendar for next 7 days
2. Check Todoist tasks due this week
3. Check Anki review schedule
4. Find free 90-minute slots
5. Block study time for French (3x) and AI (2x)"
```

## Best Practices

1. Use descriptive event titles: "Team Sync - Q4 Planning" not "Meeting"
2. Block study time consistently (same times daily/weekly)
3. Check calendar before creating Todoist tasks
4. Use Quick Add for faster event creation
5. Review calendar daily and weekly
6. Coordinate with other tools (Todoist, Anki, Obsidian)
7. Set appropriate event durations
8. Add locations and descriptions for context

## Health Check

```
"Check the health of my MCP server"
```

Should show:
```json
{
  "services": {
    "google_calendar": {
      "status": "connected",
      "message": "Successfully connected to Google Calendar",
      "calendar_count": 2
    }
  }
}
```

## Tool Count Summary

- **Health Check**: 1 tool
- **Todoist**: 11 tools
- **Anki**: 14 tools
- **Obsidian**: 8 tools
- **Google Calendar**: 10 tools
- **Total**: 44 tools

## Documentation Files

- `GOOGLE_CALENDAR_SETUP.md` - Detailed OAuth2 setup guide
- `GOOGLE_CALENDAR_EXAMPLES.md` - Comprehensive usage examples
- `GOOGLE_CALENDAR_IMPLEMENTATION_SUMMARY.md` - Technical details
- `GOOGLE_CALENDAR_QUICK_REFERENCE.md` - This file
- `README.md` - Main project documentation

## Support

For issues:
1. Check `GOOGLE_CALENDAR_SETUP.md` troubleshooting section
2. Review `GOOGLE_CALENDAR_EXAMPLES.md` for usage examples
3. Run health check to verify connection
4. Check server logs: `python -m bird_mcp.server`
5. Verify environment variables in `.env`

## Quick Tips

- Event IDs are returned when you create or list events
- Natural language works best with Quick Add
- Free slot finding requires ISO format times
- Token refreshes automatically (no action needed)
- Use "primary" as calendar_id for main calendar
- Study blocks are formatted as "Study: [subject]"
- Timezones default to UTC (specify if different)
- Quick Add handles recurring events well

## File Locations

- **Credentials**: Set in `GOOGLE_CALENDAR_CREDENTIALS_PATH`
- **Token**: `~/.bird_mcp/google_calendar_token.pickle` (or custom path)
- **Source**: `/src/bird_mcp/google_calendar_tools.py`
- **Server**: `/src/bird_mcp/server.py`

---

**Quick Start**: Set credentials path → Run server → Authenticate → Use tools

**Most Common**: `google_calendar_get_today_events`, `google_calendar_quick_add`, `google_calendar_block_study_time`

**Learning Focus**: Use `google_calendar_block_study_time` with Anki and Todoist for optimal study scheduling
