import os
import pickle
from datetime import datetime, timedelta
from typing import List, Optional
import pytz
from models import CalendarSlot

class CalendarService:
    """Mock-only calendar service that bypasses Google authentication"""
    
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.pickle"):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.timezone = pytz.timezone('UTC')  # Change to your timezone
        self.authenticated = False  # Always use mock mode
        print("📅 Calendar service initialized in DEMO MODE (no Google Calendar)")
        
    def authenticate(self) -> bool:
        """Skip Google authentication and use mock data only"""
        print("🔧 Using mock calendar data for demonstration")
        self.authenticated = False  # Keep as False to use mock data
        return True  # Return True so the app continues to work
    
    def get_availability(self, start_date: datetime, end_date: datetime) -> List[CalendarSlot]:
        """Always return mock availability"""
        return self._get_mock_availability(start_date, end_date)
    
    def _get_mock_availability(self, start_date: datetime, end_date: datetime) -> List[CalendarSlot]:
        """Generate realistic mock availability for demo purposes"""
        print("📊 Generating mock calendar availability...")
        slots = []
        
        # Ensure timezone awareness
        if start_date.tzinfo is None:
            start_date = self.timezone.localize(start_date)
        if end_date.tzinfo is None:
            end_date = self.timezone.localize(end_date)
        
        current = start_date.replace(hour=9, minute=0, second=0, microsecond=0)
        
        while current < end_date:
            # Skip weekends
            if current.weekday() < 5:  # Monday = 0, Friday = 4
                # Generate slots from 9 AM to 5 PM
                for hour in range(9, 17):
                    slot_start = current.replace(hour=hour)
                    slot_end = slot_start + timedelta(hours=1)
                    
                    # Simulate realistic busy periods
                    is_busy = (
                        hour in [12, 13] or  # Lunch break (12-2 PM)
                        (hour == 10 and current.day % 3 == 0) or  # Some 10 AM slots busy
                        (hour == 15 and current.day % 2 == 0) or  # Some 3 PM slots busy
                        (hour == 9 and current.weekday() == 0) or  # Monday morning meetings
                        (hour == 16 and current.weekday() == 4)    # Friday afternoon busy
                    )
                    
                    if not is_busy:
                        slots.append(CalendarSlot(
                            start_time=slot_start,
                            end_time=slot_end,
                            available=True
                        ))
            
            current += timedelta(days=1)
        
        print(f"📅 Found {len(slots)} available time slots")
        return slots
    
    def create_event(self, slot: CalendarSlot, title: str, description: str = "", attendee_email: str = "") -> bool:
        """Mock event creation"""
        print("=" * 50)
        print("🎉 MOCK BOOKING CREATED")
        print("=" * 50)
        print(f"📅 Event: {title}")
        print(f"🕐 Time: {slot.start_time.strftime('%A, %B %d at %I:%M %p')}")
        print(f"⏱️  Duration: 1 hour")
        if description:
            print(f"📝 Description: {description}")
        if attendee_email:
            print(f"👤 Attendee: {attendee_email}")
        print("📧 Note: This is a demo booking. No actual calendar event was created.")
        print("=" * 50)
        return True