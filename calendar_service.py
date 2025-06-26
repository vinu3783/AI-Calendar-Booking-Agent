import os
import pickle
from datetime import datetime, timedelta
from typing import List, Optional
import pytz
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from models import CalendarSlot

class CalendarService:
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.pickle"):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.timezone = pytz.timezone('UTC')  # Change to your timezone
        self.authenticated = False
        
    def authenticate(self) -> bool:
        """Authenticate with Google Calendar API"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Error refreshing credentials: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_file):
                    print(f"Credentials file {self.credentials_file} not found.")
                    print("Running in mock mode - using fake calendar data.")
                    return False
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    print(f"Error during OAuth flow: {e}")
                    print("Running in mock mode - using fake calendar data.")
                    return False
            
            # Save credentials for next run
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        try:
            self.service = build('calendar', 'v3', credentials=creds)
            # Test the connection
            self.service.calendarList().list().execute()
            self.authenticated = True
            print("Successfully authenticated with Google Calendar!")
            return True
        except Exception as e:
            print(f"Error building calendar service: {e}")
            print("Running in mock mode - using fake calendar data.")
            return False
    
    def get_availability(self, start_date: datetime, end_date: datetime) -> List[CalendarSlot]:
        """Get available time slots between start_date and end_date"""
        if not self.authenticated:
            return self._get_mock_availability(start_date, end_date)
        
        try:
            # Convert to timezone-aware if needed
            if start_date.tzinfo is None:
                start_date = self.timezone.localize(start_date)
            if end_date.tzinfo is None:
                end_date = self.timezone.localize(end_date)
            
            # Get busy periods
            body = {
                "timeMin": start_date.isoformat(),
                "timeMax": end_date.isoformat(),
                "items": [{"id": "primary"}]
            }
            
            freebusy_result = self.service.freebusy().query(body=body).execute()
            busy_periods = freebusy_result.get('calendars', {}).get('primary', {}).get('busy', [])
            
            # Generate available slots
            available_slots = self._generate_available_slots(start_date, end_date, busy_periods)
            return available_slots
            
        except HttpError as error:
            print(f'Calendar API error: {error}')
            return self._get_mock_availability(start_date, end_date)
    
    def _get_mock_availability(self, start_date: datetime, end_date: datetime) -> List[CalendarSlot]:
        """Generate mock availability for demo purposes"""
        print("Using mock calendar data")
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
                    
                    # Simulate some busy periods (lunch time and random busy slots)
                    is_busy = (
                        hour in [12, 13] or  # Lunch break
                        (hour == 10 and current.day % 3 == 0) or  # Some 10 AM slots busy
                        (hour == 15 and current.day % 2 == 0)     # Some 3 PM slots busy
                    )
                    
                    if not is_busy:
                        slots.append(CalendarSlot(
                            start_time=slot_start,
                            end_time=slot_end,
                            available=True
                        ))
            
            current += timedelta(days=1)
        
        return slots
    
    def _generate_available_slots(self, start_date: datetime, end_date: datetime, busy_periods: List[dict]) -> List[CalendarSlot]:
        """Generate available slots excluding busy periods"""
        slots = []
        current = start_date.replace(hour=9, minute=0, second=0, microsecond=0)
        
        while current < end_date:
            if current.weekday() < 5:  # Weekdays only
                for hour in range(9, 17):  # 9 AM to 5 PM
                    slot_start = current.replace(hour=hour)
                    slot_end = slot_start + timedelta(hours=1)
                    
                    # Check if slot conflicts with busy periods
                    is_available = not self._is_time_busy(slot_start, slot_end, busy_periods)
                    
                    if is_available:
                        slots.append(CalendarSlot(
                            start_time=slot_start,
                            end_time=slot_end,
                            available=True
                        ))
            
            current += timedelta(days=1)
        
        return slots
    
    def _is_time_busy(self, start_time: datetime, end_time: datetime, busy_periods: List[dict]) -> bool:
        """Check if a time slot conflicts with busy periods"""
        for busy in busy_periods:
            try:
                busy_start = datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                busy_end = datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                
                # Check for overlap
                if start_time < busy_end and end_time > busy_start:
                    return True
            except (ValueError, KeyError) as e:
                print(f"Error parsing busy period: {e}")
                continue
        
        return False
    
    def create_event(self, slot: CalendarSlot, title: str, description: str = "", attendee_email: str = "") -> bool:
        """Create a calendar event"""
        if not self.authenticated:
            print(f"MOCK BOOKING: {title}")
            print(f"Time: {slot.start_time.strftime('%A, %B %d at %I:%M %p')}")
            if description:
                print(f"Description: {description}")
            if attendee_email:
                print(f"Attendee: {attendee_email}")
            return True
        
        try:
            event = {
                'summary': title,
                'description': description,
                'start': {
                    'dateTime': slot.start_time.isoformat(),
                    'timeZone': str(self.timezone),
                },
                'end': {
                    'dateTime': slot.end_time.isoformat(),
                    'timeZone': str(self.timezone),
                },
            }
            
            if attendee_email:
                event['attendees'] = [{'email': attendee_email}]
            
            result = self.service.events().insert(calendarId='primary', body=event).execute()
            print(f"Event created: {result.get('htmlLink')}")
            return True
            
        except HttpError as error:
            print(f'Error creating event: {error}')
            return False