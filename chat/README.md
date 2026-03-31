# Chat Interfaces (`chat/`)

User interface components for interacting with the MCP Gateway through conversational interfaces.

## Purpose

The chat module provides user-friendly interfaces for interacting with the MCP Gateway's AI orchestration capabilities, supporting various chat platforms and interaction patterns.

## Directory Structure

```
chat/
├── streamlit_chat_ui.py  # Streamlit-based web chat interface
└── brain_chat.py         # Teams bot integration
```

## Core Components

### `streamlit_chat_ui.py` - Web Chat Interface
**Purpose**: Streamlit-based web application for chat interaction

**Features**:
- **Real-time Chat**: Conversational interface with the Brain Server
- **Tool Discovery**: Dynamic display of available tools
- **Execution Tracking**: Real-time display of plan execution
- **Result Formatting**: Structured display of tool outputs
- **Error Handling**: User-friendly error messages

**Architecture**:
```
User Input → Streamlit UI → Brain Server → MCP Gateway → External APIs → Results Display
```

**Key Functions**:

```python
# Main chat interface
def main():
    # Chat history management
    # User input handling
    # Brain server communication
    # Result formatting and display

# Brain server interaction
async def get_execution_plan(user_request: str):
    # Generate execution plan
    # Display plan steps
    # Handle plan errors

async def execute_plan(plan: dict):
    # Execute plan steps
    # Display real-time results
    # Handle execution errors
```

**UI Components**:
- **Chat History**: Scrollable conversation history
- **Input Field**: User text input with send button
- **Plan Display**: Structured display of execution plans
- **Results Panel**: Formatted display of tool outputs
- **Status Indicators**: Loading and error states

### `brain_chat.py` - Teams Bot Integration
**Purpose**: Microsoft Teams bot for enterprise chat integration

**Features**:
- **Teams Integration**: Native Microsoft Teams bot interface
- **Adaptive Cards**: Rich interactive cards for tool outputs
- **Authentication**: Enterprise authentication integration
- **Channel Support**: Works in Teams channels and direct messages
- **Formatting**: Optimized for Teams display format

**Architecture**:
```
Teams User → Teams Bot → Brain Server → MCP Gateway → External APIs → Teams Response
```

**Key Components**:

```python
# Bot message handling
async def on_message_activity(turn_context):
    # Process user message
    # Generate execution plan
    # Execute plan
    # Format Teams response

# Response formatting
def format_teams_response(results):
    # Create adaptive cards
    # Format tool outputs
    # Handle errors gracefully
```

## Configuration

### Streamlit Configuration

**Environment Variables**:
```bash
# Brain Server Configuration
BRAIN_SERVER_URL=http://localhost:8000

# Streamlit Configuration
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

**Configuration File** (`config.toml`):
```toml
[server]
port = 8501
address = "0.0.0.0"

[theme]
base = "light"
primaryColor = "#FF6B6B"
backgroundColor = "#FFFFFF"
```

### Teams Bot Configuration

**Bot Configuration**:
```bash
# Microsoft Teams Bot
TEAMS_BOT_ID=your-bot-id
TEAMS_BOT_PASSWORD=your-bot-password

# Brain Server
BRAIN_SERVER_URL=http://localhost:8000

# App Registration
MICROSOFT_APP_ID=your-app-id
MICROSOFT_APP_PASSWORD=your-app-password
```

## User Experience

### Streamlit Chat Flow

1. **Initial Load**:
   - Display welcome message
   - Show available tools
   - Load chat history (if any)

2. **User Input**:
   - User types natural language request
   - Input validation and formatting
   - Send to Brain Server

3. **Plan Generation**:
   - Display "Generating plan..." status
   - Show generated execution plan
   - User can approve or modify plan

4. **Execution**:
   - Real-time execution status
   - Step-by-step progress updates
   - Error handling and retry options

5. **Results Display**:
   - Formatted tool outputs
   - Interactive elements (links, buttons)
   - Option to ask follow-up questions

### Teams Bot Flow

1. **Message Reception**:
   - Bot receives user message in Teams
   - Parse and validate input
   - Acknowledge receipt

2. **Processing**:
   - Send to Brain Server
   - Generate execution plan
   - Execute plan steps

3. **Response**:
   - Format response for Teams
   - Create adaptive cards for rich display
   - Send structured response

## API Integration

### Brain Server Communication

**Plan Generation**:
```python
async def get_execution_plan(user_request: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BRAIN_SERVER_URL}/plan",
            json={"user_request": user_request}
        ) as response:
            return await response.json()
```

**Plan Execution**:
```python
async def execute_plan(plan: dict):
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{BRAIN_SERVER_URL}/execute",
            json={"plan": plan}
        ) as response:
            return await response.json()
```

## Response Formatting

### Streamlit Formatting

**Tool Output Display**:
```python
def display_tool_output(tool_name: str, output: dict):
    st.subheader(f"🔧 {tool_name}")
    
    if isinstance(output, dict):
        for key, value in output.items():
            if isinstance(value, dict):
                with st.expander(f"📋 {key}"):
                    st.json(value)
            else:
                st.write(f"**{key}**: {value}")
    else:
        st.write(output)
```

**Error Display**:
```python
def display_error(error: dict):
    st.error(f"❌ Error: {error.get('message', 'Unknown error')}")
    if 'details' in error:
        with st.expander("Error Details"):
            st.code(error['details'])
```

### Teams Formatting

**Adaptive Cards**:
```python
def create_adaptive_card(tool_results: list):
    card = {
        "type": "AdaptiveCard",
        "version": "1.2",
        "body": []
    }
    
    for result in tool_results:
        card["body"].append({
            "type": "TextBlock",
            "text": f"**{result['tool']}**",
            "weight": "bolder"
        })
        
        if isinstance(result['output'], dict):
            card["body"].append({
                "type": "RichTextBlock",
                "text": format_dict_for_teams(result['output'])
            })
    
    return card
```

## Security Considerations

### Input Validation

```python
def validate_user_input(user_input: str) -> bool:
    """Validate user input for security"""
    # Length limits
    if len(user_input) > 1000:
        return False
    
    # Content filtering
    forbidden_patterns = [
        r'<script.*?>.*?</script>',
        r'javascript:',
        r'data:text/html'
    ]
    
    for pattern in forbidden_patterns:
        if re.search(pattern, user_input, re.IGNORECASE):
            return False
    
    return True
```

### Output Sanitization

```python
def sanitize_output(output: Any) -> Any:
    """Sanitize output for display"""
    if isinstance(output, dict):
        return {k: sanitize_output(v) for k, v in output.items()}
    elif isinstance(output, list):
        return [sanitize_output(item) for item in output]
    elif isinstance(output, str):
        # Remove HTML tags
        return re.sub(r'<[^>]+>', '', output)
    else:
        return output
```

## Performance Optimization

### Caching

```python
@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_available_tools():
    """Cache available tools to reduce API calls"""
    # Implementation
    pass
```

### Async Operations

```python
async def process_user_request(user_input: str):
    """Process user request with async operations"""
    # Plan generation
    plan_task = get_execution_plan(user_input)
    plan = await plan_task
    
    # Execution
    if plan:
        execution_task = execute_plan(plan)
        results = await execution_task
    
    return results
```

## Error Handling

### User-Friendly Messages

```python
def format_user_error(error: Exception) -> str:
    """Format technical errors for user consumption"""
    error_messages = {
        "ConnectionError": "I'm having trouble connecting to my services. Please try again in a moment.",
        "TimeoutError": "The request took too long. Please try again.",
        "ValidationError": "I didn't understand that request. Could you rephrase it?",
        "AuthenticationError": "I'm having trouble with my credentials. Please contact support."
    }
    
    error_type = type(error).__name__
    return error_messages.get(error_type, "Something went wrong. Please try again.")
```

### Retry Logic

```python
async def retry_with_backoff(func, max_retries=3):
    """Retry function with exponential backoff"""
    for attempt in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            wait_time = 2 ** attempt
            await asyncio.sleep(wait_time)
```

## Deployment

### Streamlit Deployment

**Dockerfile**:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8501

CMD ["streamlit", "run", "chat/streamlit_chat_ui.py", "--server.port=8501"]
```

**Docker Compose**:
```yaml
version: '3.8'
services:
  chat-ui:
    build: .
    ports:
      - "8501:8501"
    environment:
      - BRAIN_SERVER_URL=http://brain-server:8000
    depends_on:
      - brain-server
```

### Teams Bot Deployment

**Azure Bot Service**:
- Deploy to Azure Bot Service
- Configure Microsoft Teams channel
- Set up authentication
- Configure messaging endpoint

## Monitoring

### Usage Analytics

```python
def log_chat_interaction(user_input: str, response: dict, session_id: str):
    """Log chat interactions for analytics"""
    log_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "session_id": session_id,
        "user_input_length": len(user_input),
        "response_type": type(response).__name__,
        "tools_used": [r.get("tool") for r in response.get("results", [])]
    }
    
    # Send to analytics service
    logger.info("Chat interaction", extra=log_data)
```

### Performance Metrics

```python
def track_response_time(start_time: float, operation: str):
    """Track response times for monitoring"""
    duration = time.time() - start_time
    
    metrics = {
        "operation": operation,
        "duration": duration,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    # Send to monitoring service
    if duration > 5.0:  # Alert on slow responses
        logger.warning(f"Slow response: {operation} took {duration:.2f}s")
```

## Dependencies

### Streamlit Dependencies
```bash
streamlit>=1.28.0
aiohttp>=3.8.0
plotly>=5.15.0  # For advanced visualizations
```

### Teams Bot Dependencies
```bash
botbuilder-core>=4.14.0
botbuilder-integration-aiohttp>=4.14.0
python-dotenv>=1.0.0
```

## Future Enhancements

### Planned Features

1. **Multi-language Support**: Internationalization for global users
2. **Voice Input**: Speech-to-text integration
3. **File Upload**: Support for file attachments
4. **Custom Themes**: User-customizable interface themes
5. **Mobile Optimization**: Responsive design for mobile devices
6. **Analytics Dashboard**: Usage analytics and insights
7. **Plugin System**: Extensible plugin architecture

### Integration Opportunities

1. **Slack Bot**: Expand to Slack workspace
2. **Discord Bot**: Gaming community integration
3. **Web Widget**: Embeddable chat widget
4. **Email Integration**: Email-to-chat functionality
5. **Calendar Integration**: Schedule and manage meetings
