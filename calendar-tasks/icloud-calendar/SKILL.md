---
name: icloud-calendar
description: iCloud Calendar management tool for adding, viewing, and managing calendar events via CalDAV protocol. Use when the user needs to interact with their Apple iCloud calendar, such as adding events, viewing upcoming events, checking deadlines, or managing calendar data. Triggers on phrases like "add to my calendar", "check my calendar", "icloud calendar", "apple calendar", "calendar event", or any calendar-related requests involving iCloud/Apple.
---

# iCloud Calendar

## Overview

Manage your Apple iCloud Calendar through CalDAV protocol. This skill enables adding events, viewing calendar contents, and managing deadlines directly from your iCloud account.

## Prerequisites

- iCloud account with app-specific password configured
- CalDAV access enabled for the account

## Configuration

The tool uses these default settings (stored in scripts/icloud_calendar.py):
- **URL**: `https://caldav.icloud.com/`
- **Username**: Your Apple ID (e.g., `kyq2026@icloud.com`)
- **Password**: App-specific password (not your regular iCloud password)

To generate an app-specific password:
1. Go to appleid.apple.com
2. Sign in and go to "App-Specific Passwords"
3. Generate a new password for CalDAV access

## Quick Start

### Adding an Event

```python
from icloud_calendar import iCloudCalendar
from datetime import datetime

icloud = iCloudCalendar()
icloud.connect()

# Add a simple event
start = datetime(2026, 4, 16, 22, 0)  # April 16, 2026 at 10:00 PM
end = datetime(2026, 4, 16, 22, 30)
icloud.add_event('ddl', 'Event Title', start, end, 'Event description')
```

### Viewing Events

```python
# List all calendars
calendars = icloud.list_calendars()

# View events in a specific calendar (next 7 days)
events = icloud.list_events('ddl', days=7)
```

## Available Calendars

Common calendar names in iCloud:
- `ddl` - Deadlines and due dates
- `上课` - Classes and courses
- `作业` - Assignments
- `体育` - Sports/exercise
- `社工` - Social work/volunteering
- `娱乐` - Entertainment
- `提醒 ⚠️` - Reminders (note: may have read issues via CalDAV)

## Core Capabilities

### 1. Connect to iCloud

Use `iCloudCalendar.connect()` to establish connection.

### 2. List Calendars

`iCloudCalendar.list_calendars()` returns all available calendar names.

### 3. Add Events

**Simple event:**
```python
icloud.add_event(calendar_name, summary, start_time, end_time, description)
```

**Quick add with defaults:**
```python
icloud.quick_add(calendar_name, summary, days_from_now=0, hour=9, duration_hours=1)
```

### 4. View Events

```python
icloud.list_events(calendar_name, days=7)
```

### 5. Add Recurring Events

For repeating events (like weekly classes), see the example in scripts/add_recurring_event.py

## Scripts

### icloud_calendar.py
Main Python module providing the `iCloudCalendar` class with methods:
- `connect()` - Connect to iCloud CalDAV
- `list_calendars()` - List all calendars
- `add_event()` - Add a single event
- `quick_add()` - Quick add with simplified parameters
- `list_events()` - View events in a date range

### add_recurring_event.py
Example script showing how to add weekly recurring events (e.g., classes).

## Known Limitations

1. **Reminders/Tasks**: iCloud Reminders cannot be accessed via CalDAV (returns 500 error). Use Apple Reminders app or other methods.
2. **Encoding**: On Windows, console output may require UTF-8 encoding fix (handled automatically in the script).
3. **Read-only Calendars**: Some calendars (like subscribed calendars) may be read-only.

## Error Handling

Common issues and solutions:
- **Connection failed**: Check username and app-specific password
- **Calendar not found**: Verify calendar name (case-sensitive in some cases)
- **Authentication error**: Generate a new app-specific password

## Security Notes

- App-specific passwords are stored in the script file
- Consider using environment variables for credentials in production
- Never commit credentials to version control
