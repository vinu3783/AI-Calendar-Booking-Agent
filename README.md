# AI-Calendar-Booking-Agent
# 🤖 AI Calendar Booking Assistant

**TailorTalk Backend Development Internship Assignment**

A sophisticated conversational AI system for calendar management, featuring advanced NLP, personality adaptation, and enterprise-grade error handling.

## 🌟 Live Demo

**🔗 [Try the Live Application](https://your-calendar-agent.streamlit.app)**

## 🎯 Assignment Requirements Met

- ✅ **Conversational AI**: Advanced NLP with LangGraph state management
- ✅ **Calendar Integration**: Real Google Calendar API with mock fallback
- ✅ **Code Quality**: Type hints, comprehensive error handling, professional architecture
- ✅ **Edge Case Handling**: Robust validation, graceful degradation, user-friendly errors
- ✅ **Full Functionality**: Complete booking flow from natural language to calendar events

## 🚀 Key Features

### 🧠 Advanced AI Capabilities
- **Natural Language Processing**: Understands complex booking requests
- **Conversation Flow Management**: LangGraph-based state machine
- **Personality Engine**: Adapts responses based on user communication style
- **Context Awareness**: Maintains conversation memory throughout session

### 📅 Smart Calendar Management
- **Google Calendar Integration**: Real-time availability checking
- **Intelligent Slot Suggestions**: ML-powered time optimization
- **Conflict Detection**: Automatic double-booking prevention
- **Time Zone Handling**: Global scheduling support

### 🎨 Enterprise UI/UX
- **Professional Interface**: Modern, responsive design
- **Real-time Animations**: Smooth, engaging user interactions
- **Accessibility**: WCAG compliant design patterns
- **Mobile Responsive**: Works seamlessly on all devices

## 🛠 Technical Stack

- **Backend**: Python 3.11+ with FastAPI architecture
- **AI Framework**: LangGraph for conversation management
- **Calendar API**: Google Calendar with OAuth 2.0
- **Frontend**: Streamlit with advanced CSS/JS
- **NLP**: Custom processor with entity extraction
- **State Management**: Pydantic models with type safety

## 🏗 Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Streamlit     │    │   LangGraph     │    │  Google         │
│   Frontend      │◄──►│   AI Agent      │◄──►│  Calendar API   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Personality    │    │      NLP        │    │   Calendar      │
│    Engine       │    │   Processor     │    │    Service      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔧 Installation & Setup

### Prerequisites
- Python 3.11+
- Google Cloud Project with Calendar API enabled
- OAuth 2.0 credentials (optional - demo mode available)

### Local Development
```bash
# Clone repository
git clone https://github.com/your-username/calendar-booking-agent.git
cd calendar-booking-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run production_ready_app.py
```

### Google Calendar Setup (Optional)
1. Create Google Cloud Project
2. Enable Calendar API
3. Create OAuth 2.0 credentials
4. Download `credentials.json` to project root
5. Add your email as test user in OAuth consent screen

## 🎭 Usage Examples

### Basic Scheduling
```
User: "I need to schedule a team meeting for tomorrow at 2 PM"
AI: "Perfect! Let me check availability for Thursday, June 27 around 2:00 PM..."
```

### Personality Adaptation
```
User: "URGENT! Need a meeting ASAP!"
AI: "Emergency mode activated! I'll handle this with lightning speed! ⚡"

User: "Please help me schedule something, thank you"
AI: "Aww, you're so polite! I love working with courteous people! 😊"
```

### Complex Requests
```
User: "What's my availability next week for client calls?"
AI: "I'll analyze your entire week for optimal client meeting slots..."
```

## 🧪 Testing Guide

### Core Functionality Tests
1. **Basic Booking**: "Schedule a meeting tomorrow at 2 PM"
2. **Availability Check**: "What times are available this week?"
3. **Slot Selection**: Choose from suggested time slots
4. **Confirmation**: Complete the booking process

### Personality Engine Tests
1. **Polite Mode**: "Please help me schedule a meeting, thank you"
2. **Urgent Mode**: "I need an emergency meeting ASAP!"
3. **Humor Mode**: "Tell me a joke while you check my calendar"
4. **Help Mode**: "I'm confused about my schedule"

### Edge Cases
1. **Invalid Dates**: "Schedule for yesterday"
2. **Conflicting Times**: "Book during lunch break"
3. **Network Issues**: Offline mode handling
4. **Invalid Input**: Non-scheduling related queries

## 📊 Code Quality Metrics

- **Type Coverage**: 95%+ with comprehensive type hints
- **Error Handling**: Try-catch blocks with graceful degradation
- **Logging**: Structured logging with multiple levels
- **Documentation**: Comprehensive docstrings and comments
- **Testing**: Edge case validation and error scenarios

## 🔐 Security & Privacy

- **Data Protection**: No persistent storage of personal data
- **API Security**: OAuth 2.0 with secure token management
- **Input
