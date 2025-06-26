from langgraph.graph import StateGraph, END
from typing import Dict, Any
from datetime import datetime, timedelta
from models import AgentState, ConversationState, CalendarSlot
from calendar_service import CalendarService
from nlp_processor import NLPProcessor

class BookingAgent:
    def __init__(self, calendar_service: CalendarService):
        self.calendar_service = calendar_service
        self.nlp_processor = NLPProcessor()
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the conversation flow graph using LangGraph"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("greeting", self._greeting_node)
        workflow.add_node("understand_request", self._understand_request_node)
        workflow.add_node("check_availability", self._check_availability_node)
        workflow.add_node("confirm_booking", self._confirm_booking_node)
        workflow.add_node("complete_booking", self._complete_booking_node)
        workflow.add_node("handle_error", self._handle_error_node)
        
        # Set entry point
        workflow.set_entry_point("greeting")
        
        # Add conditional edges with routing logic
        workflow.add_conditional_edges(
            "greeting",
            self._route_from_greeting,
            {
                "understand": "understand_request",
                "end": END
            }
        )
        
        workflow.add_conditional_edges(
            "understand_request", 
            self._route_from_understanding,
            {
                "check_availability": "check_availability",
                "need_more_info": "understand_request",
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "check_availability",
            self._route_from_availability,
            {
                "confirm": "confirm_booking",
                "no_slots": "understand_request", 
                "error": "handle_error"
            }
        )
        
        workflow.add_conditional_edges(
            "confirm_booking",
            self._route_from_confirmation,
            {
                "complete": "complete_booking",
                "modify": "understand_request",
                "error": "handle_error"
            }
        )
        
        workflow.add_edge("complete_booking", END)
        workflow.add_edge("handle_error", END)
        
        return workflow.compile()
    
    def _greeting_node(self, state: AgentState) -> Dict[str, Any]:
        """Handle initial greeting and intent detection"""
        if not state.messages and not state.user_input:
            # Initial greeting when agent starts
            response = "Hi! I'm your calendar booking assistant. I can help you schedule appointments and check availability. What would you like to schedule today?"
            state.agent_response = response
            state.current_state = ConversationState.GREETING
        else:
            # Process user's message
            intent = self.nlp_processor.extract_intent(state.user_input)
            if intent == "booking_request":
                response = "Great! I'd be happy to help you schedule an appointment. Let me gather some details."
                state.current_state = ConversationState.UNDERSTANDING_REQUEST
            else:
                response = "I can help you book appointments and schedule meetings. Could you tell me what kind of meeting you'd like to schedule and when?"
                state.current_state = ConversationState.UNDERSTANDING_REQUEST
            state.agent_response = response
        
        return state
    
    def _understand_request_node(self, state: AgentState) -> Dict[str, Any]:
        """Extract booking details from user input"""
        try:
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
            
            # Check if we have enough information to proceed
            missing_info = []
            if not state.booking_request.date:
                missing_info.append("date")
            if not state.booking_request.time:
                missing_info.append("preferred time")
            
            if missing_info:
                if len(missing_info) == 1:
                    response = f"I need to know the {missing_info[0]}. When would you like to schedule this?"
                else:
                    response = f"I need a bit more information. Could you please specify the {' and '.join(missing_info)}?"
                state.agent_response = response
                state.current_state = ConversationState.UNDERSTANDING_REQUEST
            else:
                # We have enough info, move to availability check
                response = f"Perfect! Let me check availability for {self._format_date(state.booking_request.date)} around {state.booking_request.time}."
                state.agent_response = response
                state.current_state = ConversationState.CHECKING_AVAILABILITY
                
        except Exception as e:
            print(f"Error in understand_request_node: {e}")
            state.current_state = ConversationState.ERROR
        
        return state
    
    def _check_availability_node(self, state: AgentState) -> Dict[str, Any]:
        """Check calendar availability and suggest slots"""
        try:
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
                
                if state.suggested_slots:
                    slots_text = "\n".join([
                        f"{i+1}. {slot.start_time.strftime('%I:%M %p')} - {slot.end_time.strftime('%I:%M %p')}"
                        for i, slot in enumerate(state.suggested_slots)
                    ])
                    
                    formatted_date = self._format_date(state.booking_request.date)
                    response = f"Here are some available time slots for {formatted_date}:\n\n{slots_text}\n\nWhich slot works best for you? Just type 1, 2, or 3."
                    state.current_state = ConversationState.CHECKING_AVAILABILITY
                else:
                    response = f"I don't have any available slots that match your preferred time on {self._format_date(state.booking_request.date)}. Would you like to try a different time or date?"
                    state.current_state = ConversationState.UNDERSTANDING_REQUEST
            else:
                response = f"I don't have any available slots on {self._format_date(state.booking_request.date)}. Would you like to try a different date?"
                state.current_state = ConversationState.UNDERSTANDING_REQUEST
            
            state.agent_response = response
            
        except Exception as e:
            print(f"Error in check_availability_node: {e}")
            state.agent_response = "I encountered an error while checking availability. Could you please try again?"
            state.current_state = ConversationState.ERROR
        
        return state
    
    def _confirm_booking_node(self, state: AgentState) -> Dict[str, Any]:
        """Handle booking confirmation"""
        try:
            user_input = state.user_input.lower()
            
            # Check if user selected a slot by number
            slot_selection = self.nlp_processor.extract_slot_selection(state.user_input)
            
            if slot_selection is not None and slot_selection < len(state.suggested_slots):
                # User selected a specific slot
                state.confirmed_slot = state.suggested_slots[slot_selection]
                slot_time = state.confirmed_slot.start_time.strftime('%A, %B %d at %I:%M %p')
                response = f"Perfect! I'll book your {state.booking_request.title.lower()} for {slot_time}. Please confirm - is this correct?"
                state.current_state = ConversationState.CONFIRMING_BOOKING
            else:
                # Check for general confirmation/rejection intent
                intent = self.nlp_processor.extract_intent(state.user_input)
                
                if intent == "confirmation" and state.confirmed_slot:
                    # User confirmed the booking
                    response = "Excellent! Let me complete your booking now."
                    state.current_state = ConversationState.BOOKING_COMPLETE
                elif intent == "rejection":
                    # User rejected or wants to modify
                    response = "No problem! Would you like to see different time slots or schedule for a different date?"
                    state.current_state = ConversationState.UNDERSTANDING_REQUEST
                    # Reset the confirmed slot
                    state.confirmed_slot = None
                else:
                    # User input not clear
                    if state.suggested_slots:
                        response = "Please select a time slot by typing 1, 2, or 3, or let me know if you'd like different options."
                    else:
                        response = "I'm not sure what you'd like to do. Could you please clarify?"
                    state.current_state = ConversationState.CHECKING_AVAILABILITY
            
            state.agent_response = response
            
        except Exception as e:
            print(f"Error in confirm_booking_node: {e}")
            state.current_state = ConversationState.ERROR
        
        return state
    
    def _complete_booking_node(self, state: AgentState) -> Dict[str, Any]:
        """Complete the booking process"""
        try:
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
                    response = f"🎉 Your {title.lower()} has been successfully booked for {slot_time}!"
                    if self.calendar_service.authenticated:
                        response += " You should receive a calendar invitation shortly."
                    response += "\n\nIs there anything else I can help you with?"
                    state.current_state = ConversationState.BOOKING_COMPLETE
                else:
                    response = "I encountered an issue while booking your appointment. Please try again or contact support."
                    state.current_state = ConversationState.ERROR
            else:
                response = "Something went wrong with the booking. Let's start over."
                state.current_state = ConversationState.ERROR
            
            state.agent_response = response
            
        except Exception as e:
            print(f"Error in complete_booking_node: {e}")
            state.agent_response = "I encountered an error while completing your booking. Please try again."
            state.current_state = ConversationState.ERROR
        
        return state
    
    def _handle_error_node(self, state: AgentState) -> Dict[str, Any]:
        """Handle errors gracefully"""
        response = "I apologize, but I encountered an issue. Let's start fresh - how can I help you schedule an appointment?"
        state.agent_response = response
        state.current_state = ConversationState.GREETING
        # Reset state
        state.booking_request = state.booking_request.__class__()
        state.suggested_slots = []
        state.confirmed_slot = None
        return state
    
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
    
    # Routing functions for LangGraph
    def _route_from_greeting(self, state: AgentState) -> str:
        """Route from greeting based on state"""
        if state.current_state == ConversationState.UNDERSTANDING_REQUEST:
            return "understand"
        return "end"
    
    def _route_from_understanding(self, state: AgentState) -> str:
        """Route from understanding based on state"""
        if state.current_state == ConversationState.CHECKING_AVAILABILITY:
            return "check_availability"
        elif state.current_state == ConversationState.ERROR:
            return "error"
        return "need_more_info"
    
    def _route_from_availability(self, state: AgentState) -> str:
        """Route from availability check based on state"""
        if state.suggested_slots and state.current_state == ConversationState.CHECKING_AVAILABILITY:
            return "confirm"
        elif state.current_state == ConversationState.ERROR:
            return "error"
        return "no_slots"
    
    def _route_from_confirmation(self, state: AgentState) -> str:
        """Route from confirmation based on state"""
        if state.current_state == ConversationState.BOOKING_COMPLETE:
            return "complete"
        elif state.current_state == ConversationState.UNDERSTANDING_REQUEST:
            return "modify"
        return "error"
    
    def process_message(self, message: str, state: AgentState) -> AgentState:
        """Process a user message and update state"""
        try:
            # Update state with user input
            state.user_input = message
            if message.strip():  # Don't add empty messages
                state.messages.append({"role": "user", "content": message})
            
            # Run the graph
            result = self.graph.invoke(state)
            
            # The result should be the updated state
            if isinstance(result, AgentState):
                # Add agent response to messages
                if result.agent_response:
                    result.messages.append({
                        "role": "assistant", 
                        "content": result.agent_response
                    })
                return result
            else:
                # Fallback - return modified state
                if state.agent_response:
                    state.messages.append({
                        "role": "assistant", 
                        "content": state.agent_response
                    })
                return state
            
        except Exception as e:
            print(f"Error processing message: {e}")
            # Fallback error handling
            state.agent_response = "I'm sorry, I encountered an error. Could you please try again?"
            state.current_state = ConversationState.ERROR
            state.messages.append({"role": "assistant", "content": state.agent_response})
            return state