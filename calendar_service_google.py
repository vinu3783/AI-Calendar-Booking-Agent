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
    # Only request calendar scope - this is allowed for unverified apps
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    
    def __init__(self, credentials_file: str = "credentials.json", token_file: str = "token.pickle"):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.service = None
        self.timezone = pytz.timezone('America/New_York')  # Change to your timezone
        self.authenticated = False
        
    def authenticate(self) -> bool:
        """Authenticate with Google Calendar API for development"""
        creds = None
        
        # Load existing token
        if os.path.exists(self.token_file):
            try:
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
                print("📄 Loaded existing credentials")
            except Exception as e:
                print(f"⚠️ Error loading token: {e}")
                creds = None
        
        # If no valid credentials, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    print("🔄 Refreshing expired credentials...")
                    creds.refresh(Request())
                    print("✅ Credentials refreshed successfully")
                except Exception as e:
                    print(f"❌ Error refreshing credentials: {e}")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_file):
                    print(f"❌ Credentials file {self.credentials_file} not found.")
                    print("📝 Please download credentials.json from Google Cloud Console")
                    print("🔄 Falling back to mock mode...")
                    return self._use_mock_mode()
                
                try:
                    print("🚀 Starting OAuth flow...")
                    print("📖 Note: You may see a warning about unverified app - this is normal for development")
                    print("🔒 Click 'Advanced' → 'Go to Calendar Booking Agent (unsafe)' to continue")
                    
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.credentials_file, self.SCOPES)
                    
                    # Run the flow with specific parameters for development
                    creds = flow.run_local_server(
                        port=8080,
                        access_type='offline',
                        include_granted_scopes='true'
                    )
                    print("✅ OAuth flow completed successfully")
                    
                except Exception as e:
                    print(f"❌ Error during OAuth flow: {e}")
                    print("🔄 Falling back to mock mode...")
                    return self._use_mock_mode()
            
            # Save credentials for next run
            try:
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
                print("💾 Credentials saved successfully")
            except Exception as e:
                print(f"⚠️ Warning: Could not save credentials: {e}")
        
        # Build the service
        try:
            print("🔨 Building Google Calendar service...")
            self.service = build('calendar', 'v3', credentials=creds)
            
            # Test the connection
            print("🧪 Testing connection...")
            calendar_list = self.service.calendarList().list(maxResults=1).execute()
            
            self.authenticated = True
            print("🎉 Successfully connected to Google Calendar!")
            print(f"📅 Calendar access confirmed for: {creds.token}")
            return True
            
        except HttpError as error:
            print(f"❌ Google Calendar API error: {error}")
            if "403" in str(error):
                print("🔒 Access denied - this might be due to app verification status")
                print("💡 For development, make sure your email is added as a test user")
            print("🔄 Falling back to mock mode...")
            return self._use_mock_mode()
        except Exception as e:
            print(f"❌ Error building calendar service: {e}")
            print("🔄 Falling back to mock mode...")
            return self._use_mock_mode()
    
    def _use_mock_mode(self) -> bool:
        """Fallback to mock mode if Google Calendar fails"""
        print("📊 Using mock calendar data for demonstration")
        self.authenticated = False
        self.service = None
        return True
    
    def get_availability(self, start_date: datetime, end_date: datetime) -> List[CalendarSlot]:
        """Get available time slots between start_date and end_date"""
        if not self.authenticated or not self.service:
            print("📅 Using mock availability data")
            return self._get_mock_availability(start_date, end_date)
        
        try:
            print(f"🔍 Checking Google Calendar availability from {start_date} to {end_date}")
            
            # Convert to timezone-aware if needed
            if start_date.tzinfo is None:
                start_date = self.timezone.localize(start_date)
            if end_date.tzinfo is None:
                end_date = self.timezone.localize(end_date)
            
            # Get busy periods from Google Calendar
            body = {
                "timeMin": start_date.isoformat(),
                "timeMax": end_date.isoformat(),
                "items": [{"id": "primary"}]
            }
            
            freebusy_result = self.service.freebusy().query(body=body).execute()
            busy_periods = freebusy_result.get('calendars', {}).get('primary', {}).get('busy', [])
            
            print(f"📊 Found {len(busy_periods)} busy periods in Google Calendar")
            
            # Generate available slots
            available_slots = self._generate_available_slots(start_date, end_date, busy_periods)
            print(f"✅ Generated {len(available_slots)} available slots from Google Calendar")
            return available_slots
            
        except HttpError as error:
            print(f'❌ Google Calendar API error: {error}')
            print("🔄 Falling back to mock data...")
            return self._get_mock_availability(start_date, end_date)
        except Exception as e:
            print(f'❌ Unexpected error: {e}')
            print("🔄 Falling back to mock data...")
            return self._get_mock_availability(start_date, end_date)
    
    def _get_mock_availability(self, start_date: datetime, end_date: datetime) -> List[CalendarSlot]:
        """Generate mock availability for demo purposes"""
        print("🎭 Generating mock calendar data...")
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
                    
                    # Simulate some busy periods
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
        
        print(f"📅 Generated {len(slots)} mock available slots")
        return slots
    
    def _generate_available_slots(self, start_date: datetime, end_date: datetime, busy_periods: List[dict]) -> List[CalendarSlot]:
        """Generate available slots excluding busy periods from Google Calendar"""
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
                print(f"⚠️ Error parsing busy period: {e}")
                continue
        
        return False
    
    def create_event(self, slot: CalendarSlot, title: str, description: str = "", attendee_email: str = "") -> bool:
        """Create a calendar event"""
        if not self.authenticated or not self.service:
            print("🎭 Creating mock booking (Google Calendar not connected)")
            print(f"📅 MOCK BOOKING: {title}")
            print(f"🕐 Time: {slot.start_time.strftime('%A, %B %d at %I:%M %p')}")
            if description:
                print(f"📝 Description: {description}")
            if attendee_email:
                print(f"👤 Attendee: {attendee_email}")
            return True
        
        try:
            print(f"📅 Creating Google Calendar event: {title}")
            
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
                event['sendUpdates'] = 'all'  # Send invitations
            
            result = self.service.events().insert(calendarId='primary', body=event).execute()
            
            print(f"✅ Event created successfully!")
            print(f"🔗 Event link: {result.get('htmlLink', 'N/A')}")
            print(f"📧 Event ID: {result.get('id', 'N/A')}")
            
            return True
            
        except HttpError as error:
            print(f'❌ Error creating Google Calendar event: {error}')
            return False
        except Exception as e:
            print(f'❌ Unexpected error creating event: {e}')
            return False