# AI Chat Stack Backend

This is the Python backend for the AI Chat Stack application. It provides WebSocket support for real-time communication with the React frontend.

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs with Python
- **WebSockets**: For real-time bidirectional communication
- **Pydantic**: Data validation and settings management
- **PyGithub**: GitHub API integration
- **Uvicorn**: ASGI server for hosting the FastAPI application

## Project Structure

```
backend/
├── app/
│   ├── api/            # API routes and endpoints
│   ├── core/           # Core application functionality
│   ├── models/         # Data models
│   ├── schemas/        # Pydantic schemas for validation
│   ├── services/       # Business logic services
│   └── main.py         # FastAPI application entry point
├── tests/              # Test cases
├── .env.example        # Environment variables template
├── requirements.txt    # Python dependencies
└── run.py              # Script to run the server
```

## Getting Started

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. Clone the repository
2. Create a virtual environment
   ```
   cd backend
   python -m venv venv
   ```
3. Activate the virtual environment
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`
4. Install dependencies
   ```
   pip install -r requirements.txt
   ```
5. Create a `.env` file based on `.env.example` and fill in your API keys

### Running the Server

```bash
# Make sure the virtual environment is activated
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Run the server
python run.py
```

The server will start at http://localhost:8080 by default.

## WebSocket API

The WebSocket endpoint is available at `/ws`. The following message types are supported:

### Client → Server Messages

- `SUBMIT_CONFIG`: Submit configuration data (GitHub token, Gemini token, etc.)
- `FETCH_FILES`: Fetch file tree from a GitHub repository
- `SEND_CHAT_MESSAGE`: Send a chat message to the AI agent

### Server → Client Messages

- `CONFIG_SUCCESS`: Configuration submitted successfully
- `CONFIG_ERROR`: Error submitting configuration
- `FILE_TREE_DATA`: File tree data response
- `FILE_TREE_ERROR`: Error fetching file tree
- `NEW_CHAT_MESSAGE`: New chat message (from user or agent)
- `AGENT_TYPING`: Agent typing status

## Testing

Run tests with pytest:

```bash
pytest
```
