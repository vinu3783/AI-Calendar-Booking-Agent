from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from typing import Dict, Optional
import logging
from calendar_service import CalendarService
from booking_agent import BookingAgent
from models import AgentState
from simple_booking_agent import SimpleBookingAgent  # Instead of BookingAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
calendar_service = CalendarService()
calendar_service.authenticate()

# Initialize FastAPI app
app = FastAPI(
    title="Calendar Booking Agent API",
    description="AI-powered calendar booking assistant",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session storage (use Redis/Database in production)
sessions: Dict[str, AgentState] = {}

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    state: str

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat messages from the frontend"""
    try:
        # Get or create session
        session_id = request.session_id or str(uuid.uuid4())
        
        # Initialize session if it doesn't exist
        if session_id not in sessions:
            sessions[session_id] = AgentState()
            # Create agent and initialize with greeting
            agent = BookingAgent(calendar_service)
            sessions[session_id] = agent.process_message("", sessions[session_id])
            logger.info(f"Created new session: {session_id}")
        
        # Process the user message
        agent = BookingAgent(calendar_service)
        sessions[session_id] = agent.process_message(request.message, sessions[session_id])
        
        logger.info(f"Processed message for session {session_id}: {request.message}")
        
        return ChatResponse(
            response=sessions[session_id].agent_response,
            session_id=session_id,
            state=sessions[session_id].current_state.value
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/session/{session_id}")
async def get_session(session_id: str):
    """Get session information"""
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = sessions[session_id]
    return {
        "session_id": session_id,
        "state": session.current_state.value,
        "messages": session.messages,
        "booking_request": session.booking_request.dict() if session.booking_request else None
    }

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    if session_id in sessions:
        del sessions[session_id]
        logger.info(f"Deleted session: {session_id}")
        return {"message": "Session deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Session not found")

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "calendar_authenticated": calendar_service.authenticated,
        "active_sessions": len(sessions)
    }

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "Calendar Booking Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Optional: Clean up old sessions periodically
from datetime import datetime, timedelta
import asyncio

async def cleanup_old_sessions():
    """Clean up sessions older than 1 hour"""
    while True:
        try:
            current_time = datetime.now()
            sessions_to_remove = []
            
            for session_id, session in sessions.items():
                # Simple cleanup based on session creation (you might want to track last activity)
                # For now, we'll keep this simple
                if len(sessions) > 100:  # Only cleanup if we have too many sessions
                    sessions_to_remove.append(session_id)
            
            # Remove oldest sessions
            for session_id in sessions_to_remove[:50]:  # Remove up to 50 old sessions
                if session_id in sessions:
                    del sessions[session_id]
                    logger.info(f"Cleaned up old session: {session_id}")
            
        except Exception as e:
            logger.error(f"Error in session cleanup: {e}")
        
        # Wait 1 hour before next cleanup
        await asyncio.sleep(3600)

# Start cleanup task when the app starts
@app.on_event("startup")
async def startup_event():
    """Start background tasks"""
    logger.info("Starting Calendar Booking Agent API")
    # asyncio.create_task(cleanup_old_sessions())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )