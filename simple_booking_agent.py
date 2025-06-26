from typing import Dict, Any
from datetime import datetime, timedelta
from models import AgentState, ConversationState, CalendarSlot
from calendar_service import CalendarService
from nlp_processor import NLPProcessor

class SimpleBookingAgent:
    """Simplified booking agent without LangGraph complexity"""
    
    def __init__(self, calendar_service: CalendarService):
        self.calendar_service = calendar_service
        self.nlp_processor = NLPProcessor()
    
    def process_message(self, message: str, state: AgentState) -> AgentState:
        """Process a user message and update state"""
        try:
            # Update state with user input
            state.user_input = message
            if message.strip():  # Don't add empty messages to history
                state.messages.append({"role": "user", "content": message})
            
            # Process based on current state
            if state.current_state == ConversationState.GREETING:
                state = self._handle_greeting(state)
            elif state.current_state == ConversationState.UNDERSTANDING_REQUEST:
                state = self._handle_understanding_request(state)
            elif state.current_state == ConversationState.CHECKING_AVAILABILITY:
                state = self._handle_checking_availability(state)
            elif state.current_state == ConversationState.CONFIRMING_BOOKING:
                state = self._handle_confirming_booking(state)
            else:
                # Default handling
                state = self._handle_greeting(state)
            
            # Add agent response to messages
            if state.agent_response:
                state.messages.append({
                    "role": "assistant", 
                    "content": state.agent_response
                })
            
            return state
            
        except Exception as e:
            print(f"Error processing message: {e}")
            state.agent_response = "I'm sorry, I encountered an error. Could you please try again?"
            state.current_state = ConversationState.ERROR
            state.messages.append({"role": "assistant", "content": state.agent_response})
            return state
    
    def _handle_greeting(self, state: AgentState) -> AgentState:
        """Handle greeting state"""
        if not state.user_input or not state.user_input.strip():
            # Initial greeting
            state.agent_response = "Hi! I'm your calendar booking assistant. I can help you schedule appointments and check availability. What would you like to schedule today?"
            state.current_state = ConversationState.GREETING
        else:
            # Process user's message
            intent = self.nlp_processor.extract_intent(state.user_input)
            if intent == "booking_request":
                state.agent_response = "Great! I'd be happy to help you schedule an appointment. Let me gather some details."
                state.current_state = ConversationState.UNDERSTANDING_REQUEST
                # Extract initial information
                self._extract_booking_info(state)
            else:
                state.agent_response = "I can help you book appointments and schedule meetings. Could you tell me what kind of meeting you'd like to schedule and when?"
                state.current_state = ConversationState.UNDERSTANDING_REQUEST
        
        return state
    
    def _handle_understanding_request(self, state: AgentState) -> AgentState:
        """Handle understanding request state"""
        # Extract booking information
        self._extract_booking_info(state)
        
        # Check if we have enough information
        missing_info = []
        if not state.booking_request.date:
            missing_info.append("date")
        if not state.booking_request.time:
            missing_info.append("preferred time")
        
        if missing_info:
            if len(missing_info) == 1:
                state.agent_response = f"I need to know the {missing_info[0]}. When would you like to schedule this?"
            else:
                state.agent_response = f"I need a bit more information. Could you please specify the {' and '.join(missing_info)}?"
            state.current_state = ConversationState.UNDERSTANDING_REQUEST
        else:
            # We have enough info, check availability
            state.agent_response = f"Perfect! Let me check availability for {self._format_date(state.booking_request.date)} around {state.booking_request.time}."
            state.current_state = ConversationState.CHECKING_AVAILABILITY
            # Get available slots
            self._get_available_slots(state)
        
        return state
    
    def _handle_checking_availability(self, state: AgentState) -> AgentState:
        """Handle checking availability state"""
        # Check if user is selecting a slot
        slot_selection = self.nlp_processor.extract_slot_selection(state.user_input)
        
        if slot_selection is not None and slot_selection < len(state.suggested_slots):
            # User selected a specific slot
            state.confirmed_slot = state.suggested_slots[slot_selection]
            slot_time = state.confirmed_slot.start_time.strftime('%A, %B %d at %I:%M %p')
            state.agent_response = f"Perfect! I'll book your {state.booking_request.title.lower()} for {slot_time}. Please confirm - is this correct?"
            state.current_state = ConversationState.CONFIRMING_BOOKING
        elif not state.suggested_slots:
            # No slots available, get them
            self._get_available_slots(state)
        else:
            # Show available slots
            slots_text = "\n".join([
                f"{i+1}. {slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}"
                for i, slot in enumerate(state.suggested_slots)
            ])
            
            formatted_date = self._format_date(state.booking_request.date)
            state.agent_response = f"Here are some available time slots for {formatted_date}:\n\n{slots_text}\n\nWhich slot works best for you? Just type 1, 2, or 3."
            state.current_state = ConversationState.CHECKING_AVAILABILITY
        
        return state
    
    def _handle_confirming_booking(self, state: AgentState) -> AgentState:
        """Handle confirming booking state"""
        intent = self.nlp_processor.extract_intent(state.user_input)
        
        if intent == "confirmation":
            # Complete the booking
            if state.confirmed_slot:
                title = state.booking_request.title or "Scheduled Meeting"
                success = self.calendar_service.create_event(
                    state.confirmed_slot,
                    title,
                    state.booking_request.description or "",
                    state.booking_request.attendee_email or ""
                )
                
                if success:
                    slot_time = state.confirmed_slot.start_time.strftime('%A, %B %d at %I:%M %p')
                    state.agent_response = f"🎉 Your {title.lower()} has been successfully booked for {slot_time}!"
                    if self.calendar_service.authenticated:
                        state.agent_response += " You should receive a calendar invitation shortly."
                    state.agent_response += "\n\nIs there anything else I can help you with?"
                    state.current_state = ConversationState.BOOKING_COMPLETE
                else:
                    state.agent_response = "I encountered an issue while booking your appointment. Please try again or contact support."
                    state.current_state = ConversationState.ERROR
            else:
                state.agent_response = "Something went wrong with the booking. Let's start over."
                state.current_state = ConversationState.GREETING
        
        elif intent == "rejection":
            # User wants to modify
            state.agent_response = "No problem! Would you like to see different time slots or schedule for a different date?"
            state.current_state = ConversationState.UNDERSTANDING_REQUEST
            state.confirmed_slot = None
        
        else:
            # Ask for clear confirmation
            state.agent_response = "Please type 'yes' to confirm the booking or 'no' to choose a different time."
            state.current_state = ConversationState.CONFIRMING_BOOKING
        
        return state
    
    def _extract_booking_info(self, state: AgentState):
        """Extract booking information from user input"""
        date_info, time_info = self.nlp_processor.extract_datetime_info(state.user_input)
        
        # Update booking request with new information
        if date_info and not state.booking_request.date:
            state.booking_request.date = date_info
        if time_info and not state.booking_request.time:
            state.booking_request.time = time_info
        
        # Extract meeting type/title if not set
        if not state.booking_request.title:
            text_lower = state.user_input.lower()
            if "call" in text_lower:
                state.booking_request.title = "Phone Call"
            elif "meeting" in text_lower:
                state.booking_request.title = "Meeting"
            elif "discussion" in text_lower or "discuss" in text_lower:
                state.booking_request.title = "Discussion"
            else:
                state.booking_request.title = "Appointment"
    
    def _get_available_slots(self, state: AgentState):
        """Get available calendar slots"""
        try:
            if not state.booking_request.date:
                return
            
            # Parse the requested date
            requested_date = datetime.strptime(state.booking_request.date, "%Y-%m-%d")
            start_date = requested_date.replace(hour=0, minute=0, second=0)
            end_date = requested_date.replace(hour=23, minute=59, second=59)
            
            # Get available slots from calendar service
            available_slots = self.calendar_service.get_availability(start_date, end_date)
            
            if available_slots:
                # Filter slots based on requested time if provided
                if state.booking_request.time:
                    preferred_slots = self._filter_preferred_slots(available_slots, state.booking_request.time)
                    state.suggested_slots = preferred_slots[:3]  # Show top 3 suggestions
                else:
                    state.suggested_slots = available_slots[:3]
            else:
                state.suggested_slots = []
                
        except Exception as e:
            print(f"Error getting available slots: {e}")
            state.suggested_slots = []
    
    def _filter_preferred_slots(self, slots: list[CalendarSlot], preferred_time: str) -> list[CalendarSlot]:
        """Filter slots based on preferred time"""
        preferred_hour = self.nlp_processor.parse_time_to_hour(preferred_time)
        if preferred_hour is None:
            return slots
        
        # Sort by proximity to preferred time
        def time_distance(slot):
            return abs(slot.start_time.hour - preferred_hour)
        
        return sorted(slots, key=time_distance)
    
    def _format_date(self, date_str: str) -> str:
        """Format date string for display"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime('%A, %B %d')
        except:
            return date_str