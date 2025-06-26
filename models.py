from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum

class ConversationState(str, Enum):
    GREETING = "greeting"
    UNDERSTANDING_REQUEST = "understanding_request"
    CHECKING_AVAILABILITY = "checking_availability"
    CONFIRMING_BOOKING = "confirming_booking"
    BOOKING_COMPLETE = "booking_complete"
    ERROR = "error"

class BookingRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    date: Optional[str] = None
    time: Optional[str] = None
    duration: Optional[int] = 60  # minutes
    attendee_email: Optional[str] = None
    
class CalendarSlot(BaseModel):
    start_time: datetime
    end_time: datetime
    available: bool = True

class AgentState(BaseModel):
    messages: List[dict] = []
    current_state: ConversationState = ConversationState.GREETING
    booking_request: BookingRequest = BookingRequest()
    suggested_slots: List[CalendarSlot] = []
    confirmed_slot: Optional[CalendarSlot] = None
    user_input: str = ""
    agent_response: str = ""
    
    class Config:
        arbitrary_types_allowed = True