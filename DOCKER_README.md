# AI Chat Stack - Dockerized

This repository contains a React frontend and a Python FastAPI backend that communicate through WebSockets. Both applications are containerized using Docker for easy deployment and development.

## Architecture

- **Frontend**: React application with WebSocket communication
- **Backend**: FastAPI Python application with WebSocket support
- **Communication**: WebSockets for real-time bidirectional messaging

## Prerequisites

- [Docker](https://www.docker.com/get-started) 
- [Docker Compose](https://docs.docker.com/compose/install/)

## Development Setup

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ai-chat-stack
   ```

2. Set up environment variables:
   ```bash
   cp backend/.env.example backend/.env
   # Edit the .env file to include your API keys
   ```

3. Start the development environment:
   ```bash
   docker compose up
   ```

4. Access the application:
   - Frontend: http://localhost:80
   - Backend API: http://localhost:8080

## Production Deployment

For production deployment, use the production Docker Compose file:

```bash
docker compose -f docker-compose.prod.yml up -d
```

This configuration:
- Doesn't mount volumes (uses code copied into the container)
- Adds restart policies
- Uses environment variables from .env files

## Configuration

### Environment Variables

Backend environment variables should be set in `backend/.env`:

```
# GitHub API
GITHUB_ACCESS_TOKEN=your_github_token_here

# Gemini API
GEMINI_API_KEY=your_gemini_api_key_here

# Server Configuration
PORT=8080
HOST=0.0.0.0
```

## Project Structure

```
├── backend/               # Python FastAPI backend
│   ├── app/               # Application code
│   ├── tests/             # Test files
│   ├── requirements.txt   # Python dependencies
│   └── Dockerfile         # Backend Docker configuration
│
├── components/            # React components
├── public/                # Static assets
│
├── Dockerfile             # Frontend Docker configuration
├── nginx.conf             # Nginx configuration for the frontend
├── docker-compose.yml     # Development Docker Compose config
└── docker-compose.prod.yml # Production Docker Compose config
```

## Development vs Production

- **Development**: Uses volume mounts for hot-reloading changes
- **Production**: Builds optimized containers with no volumes

## Troubleshooting

- **WebSocket Connection Issues**: Make sure the WebSocket URL in `constants.ts` is correctly set for your environment.
- **Container Errors**: Check logs with `docker compose logs -f [service_name]`
