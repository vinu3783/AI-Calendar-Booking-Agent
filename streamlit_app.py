import streamlit as st
import requests
import json
from datetime import datetime
import time
import uuid
import random

# Configure the page
st.set_page_config(
    page_title="Calendar Booking Assistant - Enhanced",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for beautiful styling with animations
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 15px;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
        animation: headerPulse 3s ease-in-out infinite;
    }
    
    @keyframes headerPulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.02); }
    }
    
    .chat-container {
        max-height: 500px;
        overflow-y: auto;
        padding: 1.5rem;
        border: 2px solid #e1e5e9;
        border-radius: 15px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        margin-bottom: 1rem;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px 20px;
        border-radius: 20px 20px 5px 20px;
        margin: 10px 0;
        margin-left: 15%;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        animation: slideInRight 0.5s ease-out;
        position: relative;
    }
    
    .user-message::before {
        content: "👤";
        position: absolute;
        left: -35px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.3em;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        color: #333;
        padding: 15px 20px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 0;
        margin-right: 15%;
        border-left: 4px solid #ff6b6b;
        box-shadow: 0 4px 12px rgba(252, 182, 159, 0.4);
        animation: slideInLeft 0.5s ease-out;
        position: relative;
    }
    
    .assistant-message::before {
        content: "🤖";
        position: absolute;
        right: -35px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.3em;
    }
    
    .joke-message {
        background: linear-gradient(135deg, #a8e6cf 0%, #88d8a3 100%);
        color: #2d3436;
        padding: 15px 20px;
        border-radius: 20px 20px 20px 5px;
        margin: 10px 0;
        margin-right: 15%;
        border-left: 4px solid #00b894;
        box-shadow: 0 4px 12px rgba(168, 230, 207, 0.4);
        animation: bounceIn 0.8s ease-out;
        position: relative;
    }
    
    .joke-message::before {
        content: "😄";
        position: absolute;
        right: -35px;
        top: 50%;
        transform: translateY(-50%);
        font-size: 1.3em;
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-50px); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes bounceIn {
        0% { opacity: 0; transform: scale(0.3); }
        50% { opacity: 1; transform: scale(1.05); }
        70% { transform: scale(0.9); }
        100% { opacity: 1; transform: scale(1); }
    }
    
    .feature-item {
        display: flex;
        align-items: center;
        padding: 8px 12px;
        margin: 4px 0;
        border-radius: 8px;
        transition: all 0.3s ease;
        border-left: 3px solid transparent;
    }
    
    .feature-item:hover {
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 50%);
        border-left: 3px solid #2196f3;
        transform: translateX(5px);
    }
    
    .feature-icon {
        margin-right: 12px;
        font-size: 1.2em;
        min-width: 25px;
    }
    
    .status-indicator {
        font-size: 0.9em;
        color: #6c757d;
        font-style: italic;
        text-align: center;
        margin: 15px 0;
        padding: 8px 15px;
        background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
        border-radius: 20px;
        border: 1px solid #90caf9;
        animation: fadeInUp 0.5s ease-out;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .success-message {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        font-weight: bold;
        animation: celebrationBounce 0.8s ease-out;
    }
    
    @keyframes celebrationBounce {
        0%, 20%, 50%, 80%, 100% { transform: translateY(0); }
        40% { transform: translateY(-15px); }
        60% { transform: translateY(-7px); }
    }
    
    .sidebar-section {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 15px;
        border-radius: 12px;
        margin: 15px 0;
        border-left: 4px solid #007bff;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .quick-action-enhanced {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .quick-action-enhanced:hover {
        transform: translateY(-3px) scale(1.02);
        box-shadow: 0 8px 20px rgba(116, 185, 255, 0.4);
    }
    
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #ddd;
        padding: 12px 20px;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #fd79a8 0%, #e84393 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(232, 67, 147, 0.4);
    }
    
    .connection-status {
        padding: 10px;
        border-radius: 8px;
        text-align: center;
        margin: 10px 0;
        font-weight: bold;
    }
    
    .connected {
        background: linear-gradient(135deg, #00b894 0%, #00cec9 100%);
        color: white;
        animation: connectedGlow 2s ease-in-out infinite alternate;
    }
    
    .demo-mode {
        background: linear-gradient(135deg, #fdcb6e 0%, #e17055 100%);
        color: white;
    }
    
    @keyframes connectedGlow {
        from { box-shadow: 0 0 5px rgba(0, 184, 148, 0.5); }
        to { box-shadow: 0 0 20px rgba(0, 184, 148, 0.8); }
    }
</style>
""", unsafe_allow_html=True)

# Initialize enhanced session state
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'session_id' not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if 'agent_state' not in st.session_state:
    st.session_state.agent_state = None
if 'api_status' not in st.session_state:
    st.session_state.api_status = "Unknown"
if 'joke_count' not in st.session_state:
    st.session_state.joke_count = 0
if 'personality_mode' not in st.session_state:
    st.session_state.personality_mode = True
if 'connection_status' not in st.session_state:
    st.session_state.connection_status = "demo"

# Fun collections for personality
CALENDAR_JOKES = [
    "Why don't calendars ever get stressed? Because they take everything one day at a time! 📅😄",
    "I told my calendar a joke about time... it was about time! ⏰😂",
    "Why did the meeting go to therapy? It had scheduling issues! 🤪",
    "What do you call a meeting that starts on time? A miracle! ✨",
    "Why don't computers ever double-book? They have perfect memory... unlike humans! 🤖😉",
    "I'm like a Swiss watch, but funnier and better at booking meetings! ⌚😄",
    "Time flies when you're having fun... but meetings make it crawl! 🐌",
    "Why did the calendar break up with the clock? Too much pressure about timing! 💔⏱️",
    "What's a calendar's favorite type of music? Time signatures! 🎵",
    "Why don't calendars ever win at poker? They always show their dates! 🃏📅"
]

ENCOURAGING_RESPONSES = [
    "Great choice! Let me work my scheduling magic! ✨",
    "Excellent! I'm on it faster than you can say 'double-booked'! 🚀",
    "Perfect! Time to make some calendar magic happen! 🎩✨",
    "Awesome! Let me check my crystal ball... I mean, your calendar! 🔮",
    "Fantastic! I'll find you a slot faster than a time traveler! ⚡",
    "Brilliant! Let me consult the scheduling gods! 🙏✨",
    "Wonderful! Time to play calendar Tetris! 🎮",
    "Superb! I'll make this happen smoother than butter on warm toast! 🧈",
    "Amazing! Watch me work my time-bending powers! 🌟",
    "Outstanding! I'm about to make your calendar dreams come true! 💫"
]

LOADING_MESSAGES = [
    "🤔 Let me think about this...",
    "🔍 Searching through the space-time continuum...",
    "⚡ Working my scheduling magic...",
    "🎩 Pulling the perfect time slot out of my hat...",
    "🚀 Launching availability rockets...",
    "🧠 Consulting my AI brain...",
    "✨ Sprinkling some calendar dust...",
    "🎯 Targeting the perfect time slot...",
    "🔮 Reading the calendar crystal ball...",
    "🎪 Performing scheduling acrobatics..."
]

def get_random_joke():
    """Get a random calendar-related joke"""
    return random.choice(CALENDAR_JOKES)

def get_encouraging_response():
    """Get a random encouraging response"""
    return random.choice(ENCOURAGING_RESPONSES)

def get_loading_message():
    """Get a random loading message"""
    return random.choice(LOADING_MESSAGES)

def detect_message_personality(message):
    """Detect personality cues in user message"""
    message_lower = message.lower()
    
    if any(word in message_lower for word in ["please", "thank you", "thanks", "grateful"]):
        return "polite"
    elif any(word in message_lower for word in ["urgent", "asap", "emergency", "quickly", "fast"]):
        return "urgent"
    elif any(word in message_lower for word in ["joke", "funny", "laugh", "humor", "fun"]):
        return "humor"
    elif any(word in message_lower for word in ["help", "confused", "lost", "stuck"]):
        return "helpful"
    else:
        return "normal"

# Direct agent integration (no API needed)
from simple_booking_agent import SimpleBookingAgent
from calendar_service import CalendarService
from models import AgentState

@st.cache_resource
def get_booking_agent():
    """Initialize and cache the booking agent"""
    calendar_service = CalendarService()
    auth_result = calendar_service.authenticate()
    
    # Set connection status
    if hasattr(calendar_service, 'authenticated') and calendar_service.authenticated:
        st.session_state.connection_status = "connected"
    else:
        st.session_state.connection_status = "demo"
    
    return SimpleBookingAgent(calendar_service)

def process_message_direct(message: str):
    """Process message directly with the agent - Enhanced with personality"""
    try:
        agent = get_booking_agent()
        
        # Initialize agent state if not exists
        if st.session_state.agent_state is None:
            st.session_state.agent_state = AgentState()
        
        # Detect personality and add appropriate response prefix
        personality = detect_message_personality(message)
        personality_prefix = ""
        
        if st.session_state.personality_mode and message.strip():
            if personality == "polite":
                personality_prefix = "Aww, you're so polite! I love working with nice people! 😊\n\n"
            elif personality == "urgent":
                personality_prefix = "Don't worry! I'm on it like a superhero on coffee! ☕🦸‍♂️\n\n"
            elif personality == "humor":
                joke = get_random_joke()
                personality_prefix = f"{joke}\n\nNow, back to business! "
                st.session_state.joke_count += 1
            elif personality == "helpful":
                personality_prefix = "No worries! I'm here to help and make this super easy for you! 🤗\n\n"
        
        # Process message
        st.session_state.agent_state = agent.process_message(message, st.session_state.agent_state)
        
        # Get base response
        base_response = st.session_state.agent_state.agent_response
        
        # Add encouraging responses for certain states
        if st.session_state.agent_state.current_state.value == "checking_availability":
            encouraging = get_encouraging_response()
            base_response = f"{encouraging}\n\n{base_response}"
        
        # Combine personality prefix with response
        final_response = personality_prefix + base_response if personality_prefix else base_response
        
        return {
            "response": final_response,
            "state": st.session_state.agent_state.current_state.value,
            "personality": personality,
            "booking_info": {
                "date": st.session_state.agent_state.booking_request.date,
                "time": st.session_state.agent_state.booking_request.time,
                "title": st.session_state.agent_state.booking_request.title
            }
        }
    except Exception as e:
        st.error(f"Error processing message: {e}")
        return {
            "response": "Oops! I had a little hiccup there. But don't worry, I'm resilient! Try again? 🤖💫",
            "state": "error",
            "personality": "error",
            "booking_info": {}
        }

# Enhanced App header
st.markdown('''
<div class="main-header">
    <h1>📅 Calendar Booking Assistant</h1>
    <p style="font-size: 1.2em; margin: 0;">Your AI-powered scheduling companion with personality!</p>
    <p style="font-size: 0.9em; margin-top: 10px; opacity: 0.9;">Making meetings fun, one booking at a time! ✨</p>
</div>
''', unsafe_allow_html=True)

# Enhanced sidebar with all features visible
with st.sidebar:
    # Connection status
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("## 📊 Connection Status")
    
    if st.session_state.connection_status == "connected":
        st.markdown('<div class="connection-status connected">✅ Google Calendar Connected<br>Real events will be created!</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="connection-status demo-mode">🎭 Demo Mode Active<br>Using mock calendar data</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced features showcase
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("## 🎯 Smart Features")
    
    features = [
        ("🧠", "Natural language understanding"),
        ("📊", "Real-time availability checking"),
        ("🎯", "Smart time suggestions"),
        ("🔗", "Google Calendar integration"),
        ("💾", "Conversation memory"),
        ("⚡", "Fast response times"),
        ("😄", "Personality & humor"),
        ("🎨", "Beautiful animations"),
        ("🔐", "Secure & private"),
        ("🌟", "Always learning")
    ]
    
    for icon, feature in features:
        st.markdown(f'''
        <div class="feature-item">
            <span class="feature-icon">{icon}</span>
            <span>{feature}</span>
        </div>
        ''', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # How it works
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("## ℹ️ How it works")
    st.markdown("""
    **Simple 4-step process:**
    1. 💬 **Tell me what you need**: "I need a meeting tomorrow afternoon"
    2. 🔍 **I check availability**: Finding open slots in your calendar
    3. ⏰ **Pick your time**: Choose from suggested available times
    4. ✅ **I book it**: Calendar event created automatically
    """)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Enhanced example phrases
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("## 💡 Try these fun phrases")
    example_phrases = [
        "Book a call for Friday at 2 PM",
        "Do you have time next Tuesday morning?", 
        "Schedule a meeting for tomorrow afternoon",
        "What's available this week?",
        "Tell me a joke while you check my calendar",
        "I need an urgent meeting ASAP!",
        "Thank you for being so helpful!",
        "I'm confused about my schedule"
    ]
    
    for phrase in example_phrases:
        st.markdown(f"- *\"{phrase}\"*")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Current booking info
    if st.session_state.agent_state and st.session_state.agent_state.booking_request:
        booking = st.session_state.agent_state.booking_request
        if booking.date or booking.time or booking.title:
            st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
            st.markdown("## 📋 Current Booking")
            if booking.title:
                st.markdown(f"**📝 Type:** {booking.title}")
            if booking.date:
                st.markdown(f"**📅 Date:** {booking.date}")
            if booking.time:
                st.markdown(f"**🕐 Time:** {booking.time}")
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Fun statistics
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("## 📈 Fun Stats")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("💬 Messages", len(st.session_state.messages))
        st.metric("😄 Jokes", st.session_state.joke_count)
    
    with col2:
        if st.session_state.agent_state:
            current_state = st.session_state.agent_state.current_state.value.replace("_", " ").title()
            st.metric("🤖 State", current_state)
        
        connection_emoji = "🔗" if st.session_state.connection_status == "connected" else "🎭"
        st.metric("📡 Mode", f"{connection_emoji} {st.session_state.connection_status.title()}")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Control buttons
    st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.markdown("## 🎮 Controls")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔄 New Chat", type="secondary", use_container_width=True):
            st.session_state.messages = []
            st.session_state.agent_state = None
            st.session_state.session_id = str(uuid.uuid4())
            st.rerun()
    
    with col2:
        if st.button("😄 Random Joke", type="primary", use_container_width=True):
            joke = get_random_joke()
            st.session_state.messages.append({"role": "user", "content": "Tell me a joke!"})
            st.session_state.messages.append({"role": "assistant", "content": joke, "type": "joke"})
            st.session_state.joke_count += 1
            st.rerun()
    
    # Personality toggle
    personality_enabled = st.toggle("🎭 Personality Mode", value=st.session_state.personality_mode)
    st.session_state.personality_mode = personality_enabled
    
    if personality_enabled:
        st.caption("✨ I'll respond with humor and personality!")
    else:
        st.caption("🤖 I'll stick to business-only responses.")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Main chat interface
st.markdown("## 💬 Chat with your enhanced booking assistant")

# Display chat history
chat_container = st.container()
with chat_container:
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    if not st.session_state.messages:
        # Enhanced initial greeting
        calendar_status = "real Google Calendar" if st.session_state.connection_status == "connected" else "demo mode"
        greeting_joke = get_random_joke()
        
        st.markdown(
            f'''<div class="assistant-message">
            👋 Hey there! I'm your calendar booking assistant connected to {calendar_status}! 
            <br><br>
            I'm not just any ordinary bot - I've got personality, jokes, and serious scheduling skills! Here's what I can do:
            <br><br>
            📅 Schedule meetings and appointments<br>
            ⏰ Check your calendar availability<br>
            🔍 Find the perfect time slots<br>
            📝 Create actual calendar events<br>
            😄 Keep you entertained while I work<br>
            💡 Remember our entire conversation<br>
            🎭 Respond with personality based on your tone
            <br><br>
            Here's a little joke to get us started:<br>
            <em>{greeting_joke}</em>
            <br><br>
            Try saying something like "I need a meeting tomorrow" or ask me to tell you another joke! Let's make scheduling fun! 🎉
            </div>''',
            unsafe_allow_html=True
        )
        
        # Initialize the agent with greeting
        response = process_message_direct("")
        if response and response["response"]:
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response["response"]
            })
    
    # Display conversation history with enhanced styling
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(
                f'<div class="user-message">{message["content"]}</div>',
                unsafe_allow_html=True
            )
        else:
            # Check if it's a joke message
            message_class = "joke-message" if message.get("type") == "joke" else "assistant-message"
            formatted_content = message["content"].replace('\n', '<br>')
            st.markdown(
                f'<div class="{message_class}">{formatted_content}</div>',
                unsafe_allow_html=True
            )
    
    st.markdown('</div>', unsafe_allow_html=True)

# Enhanced message input
st.markdown("### 💬 Type your message:")
with st.form("chat_form", clear_on_submit=True):
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "Message:",
            placeholder="Try: 'Schedule a meeting tomorrow' or 'Tell me a joke!' 😄",
            label_visibility="collapsed"
        )
    
    with col2:
        submit_button = st.form_submit_button("Send 🚀", type="primary", use_container_width=True)

# Handle user input with enhanced personality
if submit_button and user_input:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    # Show enhanced loading with random messages
    loading_msg = get_loading_message()
    with st.spinner(loading_msg):
        # Process message with agent
        response = process_message_direct(user_input)
        
        if response:
            # Determine message type for styling
            message_type = "joke" if response.get("personality") == "humor" else "normal"
            
            # Add assistant response to chat history
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response["response"],
                "type": message_type
            })
            
            # Enhanced status indicator
            state_display = response["state"].replace("_", " ").title()
            personality_indicator = ""
            if response.get("personality") and response["personality"] != "normal":
                personality_indicator = f" | 🎭 {response['personality'].title()} mode detected"
            
            st.markdown(
                f'<div class="status-indicator">💭 Status: {state_display}{personality_indicator}</div>', 
                unsafe_allow_html=True
            )
            
            # Enhanced success celebration
            if response["state"] == "booking_complete":
                booking_type = "Google Calendar event" if st.session_state.connection_status == "connected" else "demo booking"
                st.markdown(
                    f'<div class="success-message">🎉 Woohoo! Your {booking_type} is ready! 🎊<br>Time to celebrate! 🥳</div>',
                    unsafe_allow_html=True
                )
                st.balloons()
                time.sleep(1)
                # Additional celebration message
                celebration_joke = "Why did the calendar throw a party? Because it finally got a date! 🎉📅"
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": celebration_joke,
                    "type": "joke"
                })
                st.session_state.joke_count += 1
            
            # Rerun to update the chat display
            st.rerun()

# Enhanced quick action buttons
st.markdown("### 🚀 Quick Actions")
col1, col2, col3, col4 = st.columns(4)

quick_actions = [
    ("📅 Tomorrow 2PM", "Schedule a meeting tomorrow at 2 PM"),
    ("🕐 This Week?", "What times are available this week?"),
    ("📞 Urgent Call", "I need an urgent call ASAP please!"),
    ("😄 Surprise Me!", "Tell me a joke and then help me schedule something fun!")
]

for i, (button_text, message) in enumerate(quick_actions):
    with [col1, col2, col3, col4][i]:
        if st.button(button_text, key=f"quick_{i}", use_container_width=True):
            # Add message to chat
            st.session_state.messages.append({"role": "user", "content": message})
            
            loading_msg = get_loading_message()
            with st.spinner(loading_msg):
                response = process_message_direct(message)
                if response:
                    message_type = "joke" if response.get("personality") == "humor" else "normal"
                    st.session_state.messages.append({
                        "role": "assistant", 
                        "content": response["response"],
                        "type": message_type
                    })
                    st.rerun()

# Enhanced tips and help section
with st.expander("📚 Tips for better interactions"):
    st.markdown("""
    **🎯 Be specific about timing:**
    - ✅ "Friday at 2 PM" instead of ❌ "sometime Friday"
    - ✅ "Between 9-11 AM" instead of ❌ "morning"
    
    **📝 Mention the type of meeting:**
    - "Schedule a client call"
    - "Book a team meeting" 
    - "Set up a job interview"
    
    **🎭 Try different personalities:**
    - Be polite: "Please help me schedule a meeting"
    - Be urgent: "I need a meeting ASAP!"
    - Ask for humor: "Tell me a joke while you work"
    - Show gratitude: "Thank you for being so helpful!"
    
    **🔄 Don't worry about mistakes:**
    - You can always say "actually, let's try a different time"
    - I'll remember our conversation context
    
    **⚡ Use natural language:**
    - Just talk normally - I understand casual conversation!
    - "Hey, can we meet next Tuesday?" works perfectly
    """)

# Interactive demo section with personality
with st.expander("🎮 Interactive Demo - Try Different Personalities!"):
    st.markdown("""
    **🎯 Want to see my personality in action? Try these:**
    """)
    
    demo_col1, demo_col2 = st.columns(2)
    
    with demo_col1:
        st.markdown("**😄 Fun & Humorous:**")
        if st.button("🎪 Tell me a joke and schedule something", key="demo_humor", use_container_width=True):
            demo_message = "Tell me a joke while you help me schedule a fun team meeting for tomorrow!"
            st.session_state.messages.append({"role": "user", "content": demo_message})
            response = process_message_direct(demo_message)
            if response:
                message_type = "joke" if response.get("personality") == "humor" else "normal"
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response["response"],
                    "type": message_type
                })
                st.rerun()
        
        st.markdown("**🙏 Polite & Grateful:**")
        if st.button("🤝 Please help me kindly", key="demo_polite", use_container_width=True):
            demo_message = "Please help me schedule a meeting. Thank you so much for being helpful!"
            st.session_state.messages.append({"role": "user", "content": demo_message})
            response = process_message_direct(demo_message)
            if response:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response["response"]
                })
                st.rerun()
    
    with demo_col2:
        st.markdown("**⚡ Urgent & Fast:**")
        if st.button("🚨 I need help ASAP!", key="demo_urgent", use_container_width=True):
            demo_message = "I need an urgent meeting scheduled ASAP! It's an emergency!"
            st.session_state.messages.append({"role": "user", "content": demo_message})
            response = process_message_direct(demo_message)
            if response:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response["response"]
                })
                st.rerun()
        
        st.markdown("**🤗 Confused & Need Help:**")
        if st.button("😵 I'm confused about scheduling", key="demo_help", use_container_width=True):
            demo_message = "I'm really confused about my schedule and need help figuring this out"
            st.session_state.messages.append({"role": "user", "content": demo_message})
            response = process_message_direct(demo_message)
            if response:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response["response"]
                })
                st.rerun()

# Enhanced demo conversations
with st.expander("🧪 Full Booking Flow Demos"):
    demo_conversations = [
        {
            "title": "📅 Basic Meeting Booking",
            "description": "Simple meeting scheduling",
            "steps": [
                "I want to schedule a meeting for tomorrow at 2 PM",
                "1",  # Select first slot
                "yes"  # Confirm booking
            ]
        },
        {
            "title": "😄 Fun Booking with Jokes",
            "description": "Scheduling with humor",
            "steps": [
                "Tell me a joke while you check what times are available this Friday",
                "2",  # Select second slot
                "Thank you so much! Yes, book it!"  # Polite confirmation
            ]
        },
        {
            "title": "🚨 Urgent Call Setup",
            "description": "Emergency meeting scheduling",
            "steps": [
                "I need an urgent call scheduled ASAP for tomorrow morning!",
                "1",
                "Perfect! Yes!"
            ]
        }
    ]
    
    for demo in demo_conversations:
        st.markdown(f"**{demo['title']}**")
        st.caption(demo['description'])
        for i, step in enumerate(demo['steps'], 1):
            st.code(f'Step {i}: {step}')
        st.markdown("---")

# Enhanced statistics and info
if st.session_state.agent_state:
    st.markdown("### 📊 Session Statistics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💬 Messages", len(st.session_state.messages), delta=None)
    
    with col2:
        current_state = st.session_state.agent_state.current_state.value.replace("_", " ").title()
        st.metric("🤖 Current State", current_state)
    
    with col3:
        if st.session_state.agent_state.confirmed_slot:
            st.metric("✅ Booking Status", "Confirmed", delta="Ready!")
        elif st.session_state.agent_state.suggested_slots:
            slot_count = len(st.session_state.agent_state.suggested_slots)
            st.metric("📋 Available Slots", slot_count, delta=f"{slot_count} options")
        else:
            st.metric("📋 Available Slots", "0", delta="Checking...")
    
    with col4:
        st.metric("😄 Jokes Shared", st.session_state.joke_count, delta="Keep 'em coming!")

# Fun interaction prompts
st.markdown("### 🎭 Try These Fun Interactions")

fun_col1, fun_col2, fun_col3 = st.columns(3)

with fun_col1:
    st.markdown("**🎪 Comedy Corner**")
    if st.button("🎭 Ask for a random joke", use_container_width=True):
        messages_to_add = [
            {"role": "user", "content": "Tell me your funniest calendar joke!"},
            {"role": "assistant", "content": get_random_joke(), "type": "joke"}
        ]
        st.session_state.messages.extend(messages_to_add)
        st.session_state.joke_count += 1
        st.rerun()

with fun_col2:
    st.markdown("**⚡ Speed Round**")
    if st.button("🚀 Quick meeting request", use_container_width=True):
        speed_message = "Quick! I need a 15-minute slot tomorrow morning ASAP!"
        st.session_state.messages.append({"role": "user", "content": speed_message})
        response = process_message_direct(speed_message)
        if response:
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response["response"]
            })
            st.rerun()

with fun_col3:
    st.markdown("**🎁 Surprise Me**")
    if st.button("✨ Surprise interaction", use_container_width=True):
        surprise_messages = [
            "Surprise me with something fun while you check my calendar!",
            "Tell me a joke and then find the weirdest available time slot",
            "What's the most creative way you can help me schedule a meeting?",
            "Entertain me while you work your scheduling magic!"
        ]
        surprise_message = random.choice(surprise_messages)
        st.session_state.messages.append({"role": "user", "content": surprise_message})
        response = process_message_direct(surprise_message)
        if response:
            message_type = "joke" if response.get("personality") == "humor" else "normal"
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response["response"],
                "type": message_type
            })
            st.rerun()

# Enhanced footer with dynamic stats
st.markdown("---")

# Get current stats for footer
total_messages = len(st.session_state.messages)
joke_count = st.session_state.joke_count
connection_status = st.session_state.connection_status
personality_status = "ON" if st.session_state.personality_mode else "OFF"

st.markdown(
    f"""
    <div style='text-align: center; color: #666; font-size: 0.9em; padding: 25px; 
                background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                border-radius: 15px; border: 1px solid #dee2e6;'>
        
        <div style='margin-bottom: 15px;'>
            🤖 <strong>Enhanced Calendar Booking Assistant</strong> - Where AI meets personality! 🎭
        </div>
        
        <div style='margin-bottom: 15px; font-size: 0.85em;'>
            <em>Built with ❤️ using Streamlit, Python AI, and Google Calendar API</em>
        </div>
        
        <div style='display: flex; justify-content: center; gap: 30px; margin: 15px 0; flex-wrap: wrap;'>
            <div><strong>📊 Session:</strong> {total_messages} messages</div>
            <div><strong>😄 Humor:</strong> {joke_count} jokes shared</div>
            <div><strong>🔗 Connection:</strong> {connection_status.title()}</div>
            <div><strong>🎭 Personality:</strong> {personality_status}</div>
        </div>
        
        <div style='margin-top: 15px; padding-top: 15px; border-top: 1px solid #dee2e6; font-size: 0.8em;'>
            <div><strong>🔒 Privacy:</strong> Your calendar data is processed locally and not stored.</div>
            <div><strong>✨ Fun Fact:</strong> I love compliments, jokes, and helping you stay organized!</div>
            <div><strong>💡 Pro Tip:</strong> Try different tones in your messages - I adapt my personality to match yours!</div>
        </div>
        
    </div>
    """, 
    unsafe_allow_html=True
)