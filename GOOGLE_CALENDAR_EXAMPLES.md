# Google Calendar Integration - Usage Examples

This guide provides practical examples of using the Google Calendar tools in the Bird MCP server.

## Table of Contents

- [Basic Operations](#basic-operations)
- [Event Management](#event-management)
- [Time Management](#time-management)
- [Learning Workflows](#learning-workflows)
- [Advanced Usage](#advanced-usage)

## Basic Operations

### List All Calendars

Find all calendars accessible to your account:

```
"List all my Google calendars"
```

**What you'll get**:
- Primary calendar (your main Google Calendar)
- Secondary calendars you've created
- Shared calendars from others
- Calendar IDs needed for other operations

**Example response**:
```json
{
  "success": true,
  "calendars": [
    {
      "id": "primary",
      "summary": "john.doe@gmail.com",
      "primary": true,
      "access_role": "owner"
    },
    {
      "id": "family12345@group.calendar.google.com",
      "summary": "Family Calendar",
      "primary": false,
      "access_role": "owner"
    }
  ],
  "count": 2
}
```

### Get Today's Events

See what's on your calendar today:

```
"Show me my calendar events for today"
```

**Use cases**:
- Morning review of your schedule
- Quick check before meetings
- Planning your day

### Get Upcoming Events

See what's coming up in the next week:

```
"What events do I have in the next 7 days?"
```

You can customize the number of days:

```
"Show me my calendar for the next 3 days"
"What's on my calendar for the next 2 weeks?"
```

## Event Management

### Create Events

#### Simple Event

Create a basic event with start and end times:

```
"Create a calendar event called 'Team Meeting' tomorrow from 2pm to 3pm"
```

**Parameters**:
- Summary: "Team Meeting"
- Start time: Tomorrow at 14:00
- End time: Tomorrow at 15:00
- Calendar: Primary (default)

#### Event with Details

Create an event with description and location:

```
"Create a calendar event:
- Title: Client Presentation
- Date: 2025-11-20 at 10:00 AM
- Duration: 2 hours
- Location: Conference Room A
- Description: Q4 results presentation for ABC Corp"
```

#### Event with Attendees

Create a meeting with multiple attendees:

```
"Schedule a meeting called 'Project Kickoff' on Friday at 3pm for 1 hour.
Add these attendees: alice@example.com, bob@example.com, charlie@example.com"
```

### Quick Add with Natural Language

Use Google's Quick Add feature for natural language event creation:

```
"Quick add calendar event: Lunch with Sarah tomorrow at noon"
"Quick add: Team standup every weekday at 9am"
"Quick add: Dentist appointment next Tuesday at 2pm"
```

**Advantages**:
- No need to specify exact times in ISO format
- Google parses natural language ("tomorrow", "next Tuesday")
- Automatically handles recurring events

### Update Events

Modify existing events (you need the event ID from a previous query):

```
"Update event abc123xyz to start at 3pm instead of 2pm"
"Change the event title to 'Team Sync Meeting'"
"Update event description to include the Zoom link"
```

### Delete Events

Remove events you no longer need:

```
"Delete the calendar event with ID abc123xyz"
"Cancel the meeting scheduled for tomorrow at 2pm"
```

## Time Management

### Find Free Time Slots

Find available time for scheduling:

```
"Find 60-minute free slots in my calendar between 9am and 5pm tomorrow"
```

**Use cases**:
- Scheduling new meetings
- Planning focus time
- Finding time for tasks

**Example response**:
```json
{
  "success": true,
  "free_slots": [
    {
      "start": "2025-11-17T09:00:00+00:00",
      "end": "2025-11-17T10:00:00+00:00",
      "duration_minutes": 60
    },
    {
      "start": "2025-11-17T14:00:00+00:00",
      "end": "2025-11-17T16:30:00+00:00",
      "duration_minutes": 150
    }
  ],
  "count": 2,
  "duration_minutes": 60
}
```

### Block Study Time

Create focused study blocks for learning:

```
"Block 90 minutes of study time for French grammar tomorrow at 7pm"
"Schedule a 2-hour AI course study session on Saturday at 9am"
```

This creates a dedicated calendar event with:
- Title: "Study: [subject]"
- Specified duration
- Description indicating it's a study block

## Learning Workflows

The Google Calendar integration is designed to work seamlessly with your learning goals (AI, French, English).

### Daily Study Routine

Create a structured daily study schedule:

```
"Create the following study blocks for this week:
- Monday 7pm: French vocabulary (1 hour)
- Tuesday 7pm: AI fundamentals (90 minutes)
- Wednesday 7pm: English conversation practice (1 hour)
- Thursday 7pm: French grammar (1 hour)
- Friday 7pm: AI project work (2 hours)"
```

### Coordinate with Anki Reviews

Schedule study time around your Anki review schedule:

```
# First, check Anki stats
"How many Anki cards are due for review today?"

# Then schedule time for reviews
"Block 30 minutes of study time for Anki reviews at 8am tomorrow"
```

### Coordinate with Todoist Tasks

Combine calendar blocking with task management:

```
# Check tasks
"Show me my Todoist tasks for this week"

# Block time for high-priority tasks
"Block 2 hours tomorrow afternoon for the AI project task"
```

### Daily Learning Review

Use daily notes and calendar together:

```
# Morning routine
"What events do I have today?"
"Get my Obsidian daily note for today"
"Show me tasks due today from Todoist"

# Evening routine
"Block study time for tomorrow based on my Anki review schedule"
"Create a summary in my daily note of today's calendar events"
```

## Advanced Usage

### Multiple Calendars

Work with different calendars:

```
# List calendars to get IDs
"List all my Google calendars"

# Create event in specific calendar
"Create an event in my Family Calendar (ID: family123@group.calendar.google.com)
called 'Family Dinner' on Sunday at 6pm"
```

### Custom Time Ranges

Get events for specific date ranges:

```
"Show me all events from December 1st to December 15th"
"Get calendar events for next month"
```

### Timezone Handling

Specify timezones for events:

```
"Create an event with timezone America/New_York:
- Title: Conference Call
- Time: 2025-11-20T14:00:00
- Duration: 1 hour"
```

### Recurring Events

While creating complex recurring events is best done with Quick Add:

```
"Quick add: Team meeting every Monday at 10am"
"Quick add: Gym workout every Monday, Wednesday, Friday at 6am"
```

### Batch Operations

Perform multiple calendar operations together:

```
"For this week, I need to:
1. Find all 90-minute free slots
2. Block study time for French on Monday and Wednesday
3. Block study time for AI on Tuesday and Thursday
4. Check if I have any conflicts with my Todoist high-priority tasks"
```

## Integration Examples

### Complete Learning Session Setup

Coordinate across Todoist, Anki, Obsidian, and Calendar:

```
"Set up my study session for tomorrow:
1. Check how many Anki French cards are due
2. Find a 2-hour free slot in my calendar tomorrow
3. Block study time for French in that slot
4. Create a Todoist task to review today's French notes
5. Add a note in my Obsidian daily note about the planned session"
```

### Weekly Planning Workflow

```
"Help me plan my week:
1. Show me my calendar for the next 7 days
2. Show me all Todoist tasks due this week
3. Check my Anki stats for cards due
4. Find free 90-minute slots each day for study time
5. Create study blocks for:
   - French (3 sessions)
   - AI (2 sessions)
   - English practice (2 sessions)"
```

### Meeting Preparation

```
"I have a meeting tomorrow at 2pm:
1. Get the event details from my calendar
2. Create a Todoist task to prepare presentation
3. Create an Obsidian note with meeting agenda
4. Find a 30-minute prep slot before the meeting
5. Block that time as 'Meeting Prep'"
```

### Post-Study Review

```
"After my study session:
1. Update my Obsidian daily note with what I learned
2. Create Anki cards for new French vocabulary
3. Mark the study Todoist task as complete
4. Check tomorrow's calendar for next study session"
```

## Best Practices

### Use Descriptive Event Titles

Instead of: "Meeting"
Use: "Team Sync - Q4 Planning"

This makes it easier to:
- Search for events later
- Understand your schedule at a glance
- Coordinate with other tools

### Consistent Time Blocking

Create a consistent study schedule:
- Same times each day/week
- Regular duration blocks
- Specific subjects labeled clearly

### Leverage Natural Language

Use Quick Add when possible:
- Faster than specifying exact ISO times
- Handles recurring events easily
- More intuitive for complex patterns

### Regular Calendar Reviews

Daily reviews:
```
"What's on my calendar today?"
```

Weekly planning:
```
"Show me next week's calendar"
"Find free slots for study time next week"
```

Monthly overview:
```
"Show me all events in December"
```

### Coordinate with Other Tools

Always consider the full workflow:
1. Check calendar availability
2. Review Todoist tasks
3. Check Anki review schedule
4. Update Obsidian notes
5. Block appropriate time

## Troubleshooting

### Can't Find Event ID

List events first to get IDs:
```
"Show me all events today"
```

The response includes event IDs you can use for updates/deletes.

### Time Format Errors

Use ISO 8601 format for precise times:
- Correct: "2025-11-20T14:00:00"
- Incorrect: "Nov 20 2pm"

Or use Quick Add for natural language.

### Timezone Confusion

Specify timezone explicitly:
```
"Create event with timezone UTC"
"Create event with timezone America/Los_Angeles"
```

Common timezones:
- UTC
- America/New_York
- America/Los_Angeles
- Europe/London
- Europe/Paris
- Asia/Tokyo

### Free Slot Finding Not Working

Ensure you specify:
- Start time (time_min)
- End time (time_max)
- Duration in minutes

Example:
```
"Find 60-minute free slots between 2025-11-20T09:00:00 and 2025-11-20T17:00:00"
```

## Tips for Maximum Productivity

1. **Morning Calendar Review**: Start each day by checking your calendar
2. **Time Block Everything**: Schedule study time, not just meetings
3. **Use Consistent Labels**: "Study: [subject]" for all study blocks
4. **Coordinate Tools**: Check calendar before creating Todoist tasks
5. **Find Free Time First**: Before committing to tasks, check availability
6. **Update Regularly**: Keep calendar current to avoid conflicts
7. **Set Reminders**: Use calendar notifications for study sessions
8. **Review and Adjust**: Weekly review to optimize your schedule

## Example Conversations

### Planning a Study Session

**You**: "I need to study French tomorrow. Help me schedule it."

**Assistant**:
1. Checks your calendar for tomorrow
2. Finds free 90-minute slots
3. Asks your preference
4. Blocks study time in chosen slot
5. Creates related Todoist task
6. Updates Obsidian daily note

### Weekly Planning

**You**: "Plan my study schedule for next week"

**Assistant**:
1. Gets next week's calendar events
2. Finds all free time slots
3. Checks Anki review schedule
4. Reviews Todoist learning tasks
5. Proposes optimal study times
6. Creates calendar blocks
7. Confirms schedule

### Quick Schedule Check

**You**: "Am I free tomorrow afternoon?"

**Assistant**:
1. Gets tomorrow's events
2. Filters for afternoon (12pm-6pm)
3. Shows free slots
4. Suggests activities based on your learning goals

## Summary

The Google Calendar integration provides:
- Full calendar management capabilities
- Natural language event creation
- Smart time slot finding
- Study time blocking
- Seamless integration with Todoist, Anki, and Obsidian

Use it to create a structured, productive learning schedule that supports your goals in AI, French, and English.
