# AI Chat Stack Template

A comprehensive template for building AI chat applications with React frontend and Python backend, featuring real-time WebSocket communication.

## ⚡ Quick Start

```bash
# Clone this template
git clone https://github.com/yourusername/ai-chat-stack.git my-ai-app
cd my-ai-app

# Start with Docker (recommended)
docker compose up

# Access the application
# Frontend: http://localhost:80
# Backend API: http://localhost:8080
```

## Overview

This project provides a complete scaffolding for building AI-powered chat applications. It consists of:

- **React Frontend**: Modern UI with WebSocket communication
- **Python FastAPI Backend**: Real-time messaging with WebSocket support
- **Docker Configuration**: For both development and production environments

## 🚀 Getting Started

### Running Locally (Without Docker)

**Frontend Prerequisites:**
- Node.js 16+
- npm or yarn

**Backend Prerequisites:**
- Python 3.9+
- pip

#### Frontend Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create a `.env.local` file with your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

#### Backend Setup

1. Create a Python virtual environment:
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate     # On Windows
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file from the template:
   ```bash
   cp .env.example .env
   # Edit the .env file with your API keys
   ```

4. Run the server:
   ```bash
   python run.py
   ```

### Using Docker

For development and deployment with Docker, see [DOCKER_README.md](DOCKER_README.md).

## 📋 Customizing This Template

### 1. Replace the AI Service Implementation

The current AI service in `backend/app/services/ai_service.py` is a placeholder. Implement your own AI integration:

```python
async def process_message(self, message: str, context: Dict[str, Any]) -> str:
    """
    Replace this with your actual AI model integration:
    - Gemini API
    - OpenAI API
    - Local LLM
    - Custom AI solution
    """
    # Example integration with Gemini API:
    from google.generativeai import GenerativeModel
    import google.generativeai as genai
    
    genai.configure(api_key=self.api_key)
    model = GenerativeModel('gemini-pro')
    response = await model.generate_content_async(message)
    
    return response.text
```

### 2. Extend the Message Types

Add custom message types to enhance the communication between frontend and backend:

1. Update the schemas in `backend/app/schemas/ws_schemas.py`
2. Update the types in `types.ts` in the frontend
3. Add handlers in `backend/app/core/ws_manager.py`
4. Update the frontend components to handle the new message types

Example of adding a new message type:

```typescript
// In types.ts
export type ClientToServerMessage =
  | { type: 'SUBMIT_CONFIG'; payload: ConfigData }
  | { type: 'FETCH_FILES'; payload: { repo: string; branch: string; githubToken: string } }
  | { type: 'SEND_CHAT_MESSAGE'; payload: { text: string } }
  | { type: 'CUSTOM_ACTION'; payload: { actionType: string; data: any } }; // New message type
```

### 3. Add Authentication

Implement user authentication:

1. Backend: Add JWT authentication middleware to FastAPI
2. Frontend: Add login/registration forms and token management
3. WebSocket: Modify connections to include authentication tokens

### 4. Customize UI Components

The React components in the `components/` directory can be styled and customized:

- Update styling with your brand colors
- Add new UI elements for specific features
- Modify the chat interface layout

### 5. Add Database Persistence

Replace the in-memory database with a persistent solution:

1. Add a database (PostgreSQL, MongoDB, etc.)
2. Update the models in `backend/app/models/`
3. Add database connection and ORM (SQLAlchemy, Beanie, etc.)
4. Implement repository pattern for data access

### 6. Add Features

Common features to consider:

- Message history persistence
- User preferences
- File uploads and attachments
- Markdown/rich text support
- Code highlighting
- Multi-user support
- Chat rooms/channels

## 🧩 Project Structure

### Frontend

```
├── components/            # React components
│   ├── common/            # Reusable UI components
│   └── icons/             # SVG icons
├── App.tsx                # Main application component
├── constants.ts           # Configuration constants
├── types.ts               # TypeScript type definitions
├── index.tsx              # Application entry point
└── vite.config.ts         # Vite configuration
```

### Backend

```
backend/
├── app/
│   ├── api/               # API routes and endpoints
│   ├── core/              # Core application functionality
│   ├── models/            # Data models
│   ├── schemas/           # Pydantic schemas
│   ├── services/          # Business logic services
│   └── main.py            # FastAPI application entry point
├── tests/                 # Test cases
└── run.py                 # Server entry point
```

## 📡 WebSocket Communication Protocol

The frontend and backend communicate via a simple JSON-based WebSocket protocol:

### Client → Server Messages

- `SUBMIT_CONFIG`: Send configuration data (API keys, repository info)
- `FETCH_FILES`: Request file tree from GitHub repository
- `SEND_CHAT_MESSAGE`: Send a chat message to the AI

### Server → Client Messages

- `CONFIG_SUCCESS`: Configuration accepted
- `CONFIG_ERROR`: Configuration error
- `FILE_TREE_DATA`: File tree response
- `FILE_TREE_ERROR`: File tree error
- `NEW_CHAT_MESSAGE`: New chat message (from user or AI)
- `AGENT_TYPING`: AI typing indicator

## 📚 Additional Documentation

- [Backend API Documentation](backend/README.md)
- [Docker Configuration](DOCKER_README.md)

## 📝 License

MIT License - Feel free to use this template for your own projects!

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## ✨ Acknowledgements

This template was created to simplify the process of building AI chat applications with a modern tech stack.
