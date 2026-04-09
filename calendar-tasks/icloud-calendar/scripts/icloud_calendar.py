#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iCloud Calendar Tool for Windows
Supports: list calendars, view events, add events
"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

import caldav
from datetime import datetime, timedelta
from icalendar import Calendar, Event
import uuid

# iCloud CalDAV Config
# NOTE: Update these with your own credentials or use environment variables
ICLOUD_URL = "https://caldav.icloud.com/"
USERNAME = "kyq2026@icloud.com"
PASSWORD = "cjfj-tzzp-ckwf-pyex"

class iCloudCalendar:
    def __init__(self, username=None, password=None, url=None):
        self.client = None
        self.principal = None
        self.calendars = {}
        self.username = username or USERNAME
        self.password = password or PASSWORD
        self.url = url or ICLOUD_URL
        
    def connect(self):
        """Connect to iCloud CalDAV"""
        print("Connecting to iCloud CalDAV...")
        self.client = caldav.DAVClient(
            url=self.url,
            username=self.username,
            password=self.password
        )
        self.principal = self.client.principal()
        print("Connected successfully!")
        self._load_calendars()
        return True
        
    def _load_calendars(self):
        """Load all calendars"""
        cals = self.principal.calendars()
        self.calendars = {}
        for cal in cals:
            try:
                name = cal.get_display_name() or "Unnamed"
            except:
                name = str(cal.url).split('/')[-2] if cal.url else "Unnamed"
            self.calendars[name] = cal
        
    def list_calendars(self):
        """List all calendars"""
        print("\n=== Your Calendars ===")
        names = []
        for i, (name, cal) in enumerate(self.calendars.items(), 1):
            # Handle encoding issues
            safe_name = name.encode('utf-8', errors='ignore').decode('utf-8')
            print(f"{i}. {safe_name}")
            names.append(name)
        return names
    
    def list_events(self, calendar_name, days=7):
        """List events in a calendar"""
        if calendar_name not in self.calendars:
            print(f"Calendar '{calendar_name}' not found!")
            return []
            
        cal = self.calendars[calendar_name]
        now = datetime.now()
        end = now + timedelta(days=days)
        
        safe_name = calendar_name.encode('utf-8', errors='ignore').decode('utf-8')
        print(f"\n=== Events in '{safe_name}' (next {days} days) ===")
        events = cal.date_search(start=now, end=end)
        
        event_list = []
        for i, event in enumerate(events, 1):
            try:
                vevent = event.vobject_instance.vevent
                summary = str(getattr(vevent, 'summary', 'No Title'))
                dtstart = getattr(vevent, 'dtstart', None)
                
                if dtstart:
                    start_time = dtstart.value
                    if isinstance(start_time, datetime):
                        time_str = start_time.strftime("%Y-%m-%d %H:%M")
                    else:
                        time_str = str(start_time)
                else:
                    time_str = "No date"
                    
                print(f"{i}. {summary} - {time_str}")
                event_list.append({
                    'summary': summary,
                    'start': time_str,
                    'event_obj': event
                })
            except Exception as e:
                print(f"{i}. [Error reading event: {e}]")
                
        if not event_list:
            print("No events found.")
            
        return event_list
    
    def add_event(self, calendar_name, summary, start_time, end_time=None, description=""):
        """Add event to calendar"""
        if calendar_name not in self.calendars:
            print(f"Calendar '{calendar_name}' not found!")
            return False
            
        cal = self.calendars[calendar_name]
        
        # Create icalendar event
        ical = Calendar()
        ical.add('prodid', '-//iCloud Calendar//')
        ical.add('version', '2.0')
        
        event = Event()
        event.add('summary', summary)
        event.add('dtstart', start_time)
        if end_time:
            event.add('dtend', end_time)
        if description:
            event.add('description', description)
        event.add('uid', str(uuid.uuid4()))
        event.add('dtstamp', datetime.now())
        
        ical.add_component(event)
        
        # Add event
        try:
            cal.add_event(ical.to_ical())
            print(f"Added event: {summary}")
            return True
        except Exception as e:
            print(f"Failed to add event: {e}")
            return False
    
    def quick_add(self, calendar_name, summary, days_from_now=0, hour=9, duration_hours=1):
        """Quick add event (simplified)"""
        start = datetime.now() + timedelta(days=days_from_now)
        start = start.replace(hour=hour, minute=0, second=0, microsecond=0)
        end = start + timedelta(hours=duration_hours)
        return self.add_event(calendar_name, summary, start, end)


def interactive_mode():
    """Interactive mode"""
    icloud = iCloudCalendar()
    
    if not icloud.connect():
        return
    
    calendars = icloud.list_calendars()
    
    if not calendars:
        print("No calendars found!")
        return
    
    # Show events from first calendar as example
    first_cal = calendars[0]
    icloud.list_events(first_cal, days=7)
    
    print("\n\n=== iCloud Calendar Tool Ready ===")
    print("Available commands:")
    print("  icloud.list_calendars()           - List all calendars")
    print("  icloud.list_events('name', days)  - View events")
    print("  icloud.quick_add('name', 'title') - Quick add event")
    print("  icloud.add_event('name', 'title', start, end) - Add with details")
    
    return icloud


if __name__ == "__main__":
    icloud = interactive_mode()
