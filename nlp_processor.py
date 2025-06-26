import re
from datetime import datetime, timedelta
from typing import Tuple, Optional
from dateutil import parser
import pytz

class NLPProcessor:
    def __init__(self, timezone='UTC'):
        self.timezone = pytz.timezone(timezone)
        
        # Enhanced intent patterns - more comprehensive
        self.booking_intents = [
            r'\b(book|schedule|set up|arrange|plan)\b.*\b(meeting|call|appointment|session)\b',
            r'\b(want to|need to|would like to)\b.*\b(meet|talk|discuss|schedule)\b',
            r'\b(available|free)\b.*\b(time|slot)\b',
            r'\b(when can|what time)\b',
            r'\b(do you have)\b.*\b(time|availability)\b',
            r'\b(schedule)\b.*\b(meeting|call|appointment)\b',
            r'\b(I want to schedule)\b',
            r'\b(Can we book)\b',
            r'\b(What times are available)\b',
        ]
        
        # Confirmation patterns
        self.confirmation_patterns = [
            r'\b(yes|yeah|yep|ok|okay|sure|sounds good|perfect|great)\b',
            r'\b(confirm|book it|schedule it)\b',
            r'\b(that works|looks good)\b',
        ]
        
        # Rejection patterns
        self.rejection_patterns = [
            r'\b(no|nope|not available|can\'t make it)\b',
            r'\b(different time|another time|reschedule)\b',
            r'\b(cancel|not interested)\b',
        ]
        
        # Time patterns
        self.time_patterns = [
            r'\b(\d{1,2}):(\d{2})\s*(am|pm|AM|PM)\b',  # 2:30 PM
            r'\b(\d{1,2})\s*(am|pm|AM|PM)\b',          # 2 PM
            r'\b(\d{1,2})-(\d{1,2})\s*(am|pm|AM|PM)\b', # 2-4 PM
            r'\b(morning|afternoon|evening|noon)\b',     # General times
        ]
        
        # Date patterns
        self.date_patterns = [
            r'\b(today|tomorrow|yesterday)\b',
            r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday)\b',
            r'\b(next week|this week|next month|this month)\b',
            r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b',  # MM/DD/YYYY
            r'\b(\d{1,2})/(\d{1,2})\b',          # MM/DD
            r'\b(\d{1,2})-(\d{1,2})-(\d{4})\b',  # MM-DD-YYYY
        ]
        
        # Slot selection patterns
        self.slot_selection_patterns = [
            r'\b(first|1st|one|1)\b',
            r'\b(second|2nd|two|2)\b', 
            r'\b(third|3rd|three|3)\b',
        ]
    
    def extract_intent(self, text: str) -> str:
        """Extract user intent from text"""
        text_lower = text.lower().strip()
        
        # Check for booking intent first
        for pattern in self.booking_intents:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return "booking_request"
        
        # Check for confirmation
        for pattern in self.confirmation_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return "confirmation"
        
        # Check for rejection
        for pattern in self.rejection_patterns:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return "rejection"
        
        # Check for slot selection
        for i, pattern in enumerate(self.slot_selection_patterns):
            if re.search(pattern, text_lower, re.IGNORECASE):
                return f"slot_selection_{i}"
        
        return "general"
    
    def extract_datetime_info(self, text: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract date and time information from text"""
        text_lower = text.lower()
        
        # Extract date
        date_match = self._extract_date(text_lower)
        
        # Extract time
        time_match = self._extract_time(text_lower)
        
        return date_match, time_match
    
    def extract_slot_selection(self, text: str) -> Optional[int]:
        """Extract slot selection from user input"""
        text_lower = text.lower()
        
        for i, pattern in enumerate(self.slot_selection_patterns):
            if re.search(pattern, text_lower, re.IGNORECASE):
                return i
        
        return None
    
    def _extract_date(self, text: str) -> Optional[str]:
        """Extract date from text"""
        now = datetime.now(self.timezone)
        
        # Handle relative dates
        if "today" in text:
            return now.strftime("%Y-%m-%d")
        elif "tomorrow" in text:
            return (now + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "yesterday" in text:
            return (now - timedelta(days=1)).strftime("%Y-%m-%d")
        
        # Handle day names
        weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for i, day in enumerate(weekdays):
            if day in text:
                days_ahead = i - now.weekday()
                if days_ahead <= 0:  # Target day already happened this week
                    days_ahead += 7
                target_date = now + timedelta(days=days_ahead)
                return target_date.strftime("%Y-%m-%d")
        
        # Handle "next week" - default to next Monday
        if "next week" in text:
            days_until_next_monday = 7 - now.weekday()
            next_monday = now + timedelta(days=days_until_next_monday)
            return next_monday.strftime("%Y-%m-%d")
        
        # Handle "this week" - find next available weekday
        if "this week" in text:
            # If it's weekend, suggest next Monday
            if now.weekday() >= 5:  # Saturday or Sunday
                days_until_monday = 7 - now.weekday()
                next_monday = now + timedelta(days=days_until_monday)
                return next_monday.strftime("%Y-%m-%d")
            else:
                return now.strftime("%Y-%m-%d")
        
        # Try to parse explicit dates
        # MM/DD/YYYY format
        date_matches = re.findall(r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b', text)
        if date_matches:
            month, day, year = date_matches[0]
            try:
                parsed_date = datetime(int(year), int(month), int(day))
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                pass
        
        # MM/DD format (assume current year)
        date_matches = re.findall(r'\b(\d{1,2})/(\d{1,2})\b', text)
        if date_matches:
            month, day = date_matches[0]
            try:
                parsed_date = datetime(now.year, int(month), int(day))
                # If the date is in the past, assume next year
                if parsed_date < now:
                    parsed_date = datetime(now.year + 1, int(month), int(day))
                return parsed_date.strftime("%Y-%m-%d")
            except ValueError:
                pass
        
        return None
    
    def _extract_time(self, text: str) -> Optional[str]:
        """Extract time from text"""
        # Handle time ranges (take the start time)
        time_range_match = re.search(r'\b(\d{1,2})-(\d{1,2})\s*(am|pm|AM|PM)\b', text)
        if time_range_match:
            start_hour, end_hour, period = time_range_match.groups()
            return f"{start_hour}:00 {period.upper()}"
        
        # Handle specific times with minutes
        time_match = re.search(r'\b(\d{1,2}):(\d{2})\s*(am|pm|AM|PM)\b', text)
        if time_match:
            hour, minute, period = time_match.groups()
            return f"{hour}:{minute} {period.upper()}"
        
        # Handle specific times without minutes
        time_match = re.search(r'\b(\d{1,2})\s*(am|pm|AM|PM)\b', text)
        if time_match:
            hour, period = time_match.groups()
            return f"{hour}:00 {period.upper()}"
        
        # Handle general times
        if "morning" in text:
            return "9:00 AM"
        elif "afternoon" in text:
            return "2:00 PM"
        elif "evening" in text:
            return "6:00 PM"
        elif "noon" in text:
            return "12:00 PM"
        
        return None
    
    def parse_time_to_hour(self, time_str: str) -> Optional[int]:
        """Parse time string to hour (24-hour format)"""
        if not time_str:
            return None
            
        try:
            time_match = re.search(r'(\d{1,2}):?(\d{2})?\s*(am|pm|AM|PM)', time_str)
            if time_match:
                hour, minute, period = time_match.groups()
                hour = int(hour)
                if period.upper() == 'PM' and hour != 12:
                    hour += 12
                elif period.upper() == 'AM' and hour == 12:
                    hour = 0
                return hour
        except:
            pass
        return None