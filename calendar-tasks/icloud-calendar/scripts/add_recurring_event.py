#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example: Add a recurring event to iCloud Calendar
Useful for weekly classes, meetings, etc.
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import caldav
from datetime import datetime, timedelta
from icalendar import Calendar, Event, vRecur
import uuid

# iCloud CalDAV Config
ICLOUD_URL = "https://caldav.icloud.com/"
USERNAME = "kyq2026@icloud.com"
PASSWORD = "cjfj-tzzp-ckwf-pyex"

print("Connecting to iCloud CalDAV...")
client = caldav.DAVClient(url=ICLOUD_URL, username=USERNAME, password=PASSWORD)
principal = client.principal()
print("Connected!\n")

# Get the target calendar
calendars = principal.calendars()
target_cal = None
calendar_name = "上课"  # Change this to your target calendar

for cal in calendars:
    try:
        name = cal.get_display_name() or ""
        if name == calendar_name:
            target_cal = cal
            break
    except:
        pass

if not target_cal:
    print(f"Error: '{calendar_name}' calendar not found!")
    print("Available calendars:")
    for cal in calendars:
        try:
            print(f"  - {cal.get_display_name()}")
        except:
            pass
    exit(1)

print(f"Adding recurring event to '{calendar_name}' calendar...")

# Create the recurring event
ical = Calendar()
ical.add('prodid', '-//iCloud Calendar//')
ical.add('version', '2.0')

# Example: Weekly event starting next Tuesday
# Adjust these parameters as needed
today = datetime.now()
days_until_tuesday = (1 - today.weekday()) % 7  # Tuesday is 1
if days_until_tuesday == 0:
    days_until_tuesday = 7
first_tuesday = today + timedelta(days=days_until_tuesday)

# Event details
start_dt = first_tuesday.replace(hour=8, minute=0, second=0, microsecond=0)
end_dt = first_tuesday.replace(hour=9, minute=35, second=0, microsecond=0)
event_title = "Weekly Meeting"  # Change this
event_description = "Recurring weekly event"

print(f"First occurrence: {start_dt.strftime('%Y-%m-%d %H:%M')} - {end_dt.strftime('%H:%M')}")

# Create event
event = Event()
event.add('summary', event_title)
event.add('dtstart', start_dt)
event.add('dtend', end_dt)
event.add('description', event_description)
event.add('uid', str(uuid.uuid4()))
event.add('dtstamp', datetime.now())

# Add recurrence rule: every Tuesday until end date
until_date = datetime(2026, 6, 30, 23, 59, 59)  # Adjust end date
recur = vRecur(freq='weekly', byweekday='TU', until=until_date)
event.add('rrule', recur)

ical.add_component(event)

# Add event to calendar
try:
    target_cal.add_event(ical.to_ical())
    print("\n✓ Recurring event added successfully!")
    print(f"  Title: {event_title}")
    print(f"  Schedule: Every Tuesday {start_dt.strftime('%H:%M')}-{end_dt.strftime('%H:%M')}")
    print(f"  First: {start_dt.strftime('%Y-%m-%d')}")
    print(f"  Until: {until_date.strftime('%Y-%m-%d')}")
except Exception as e:
    print(f"\n✗ Failed to add event: {e}")
    import traceback
    traceback.print_exc()
