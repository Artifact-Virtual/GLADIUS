# Artifact Virtual Chat Server

A production-ready, real-time chat application built with TypeScript, Express.js, and Socket.IO. This enterprise-grade chat server provides secure, scalable real-time communication with comprehensive API endpoints and monitoring capabilities.

## Features

- Real-time communication using Socket.IO
- Multi-user support with join/leave notifications
- Modern web client with a full-featured UI for testing
- Production-ready: TypeScript compilation, error handling, graceful shutdown
- RESTful API endpoints for monitoring and management
- In-memory chat history persistence and retrieval
- Room support for multi-room functionality
- Optimized for high-throughput messaging
- Security features: CORS configuration and input validation

## Architecture

### Core Components

- Express.js server for RESTful API and static file serving
- Socket.IO integration for real-time WebSocket communication
- TypeScript for type-safe development and compilation
- In-memory storage for fast message history and user management
- Graceful shutdown with proper cleanup and resource management

### Project Structure

```text
chat-app/
├── src/
│   ├── server.ts           # Main server application
│   └── app.ts              # Express app configuration (legacy)
├── dist/                   # Compiled JavaScript output
├── public/
│   └── index.html          # Enhanced web client with test interface
├── config/                 # Configuration files
├── tests/                  # Test files
├── .env                    # Environment variables
├── .env.example            # Environment template
├── package.json            # Dependencies and scripts
├── tsconfig.json           # TypeScript configuration
└── README.md               # This file
```

## Quick Start

### Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- TypeScript compiler

### Installation

1. Navigate to the project directory:

    ```bash
    cd W:\artifactvirtual\workshop\templates\chat-app
    ```

2. Install dependencies:

    ```bash
    npm install
    ```

3. Set up environment variables:

    ```bash
    # Copy the example environment file
    cp .env.example .env
   
   # Edit .env with your configurationn
   PORT=60000
   NODE_ENV=developmentt
   CORS_ORIGIN=http://localhost:60000
   ````

4. **Build the TypeScript project**:

   ```bashh
   npm run buildd
    # or
    npx tsc
    ```

5. Start the server:

    ```bash
    # Production mode
    node dist/server.js

    # Development mode (if ts-node is available)
    npm run dev
    ```

6. Access the application:
    Open your browser and navigate to `http://localhost:6000`

## API Endpoints

### Public Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serves the web client interface |
| GET | `/test` | Server health test endpoint |
| GET | `/api/health` | Comprehensive health check |
| GET | `/api/users` | List connected users |
| GET | `/api/messages` | Retrieve chat history |

### WebSocket Events

#### Client → Server

| Event | Payload | Description |
|-------|---------|-------------|
| `join` | `{ username: string }` | User joins the chat |
| `message` | `{ username: string, message: string, timestamp?: string }` | Send a message |
| `join-room` | `roomId: string` | Join a specific room |
| `send-message` | `{ room: string, message: string, user: string }` | Send room message |
| `typing` | `{ username: string, isTyping: boolean }` | Typing indicator |

#### Server → Client

| Event | Payload | Description |
|-------|---------|-------------|
| `message` | `ChatMessage` | Broadcast message to all users |
| `user_joined` | `{ username: string }` | User joined notification |
| `user_left` | `{ username: string }` | User left notification |
| `user_count` | `{ count: number }` | Current user count |
| `chat_history` | `ChatMessage[]` | Historical messages |
| `user_typing` | `{ username: string, isTyping: boolean }` | Typing indicator |

## Testing

### Web Client Features

The web client includes comprehensive testing capabilities:

- Connection management: connect/disconnect with custom username
- Real-time messaging: send and receive messages instantly
- Test functions:
  - Server connection test
  - Random test message generation
  - Multiple message simulation
  - Message history clearing
- Visual indicators: connection status and message timestamps
- Keyboard shortcuts: Enter key support for quick messaging

### Testing Multi-user Chat

1. Open multiple browser tabs to `http://localhost:6000`
2. Connect with different usernames in each tab
3. Send messages to test real-time broadcasting
4. Use test functions to simulate high-frequency messaging

### API Testing

```bash
# Test server health
curl http://localhost:6000/api/health

# Get connected users
curl http://localhost:6000/api/users

# Get chat history
curl http://localhost:6000/api/messages?limit=10
```

## Monitoring

### Server Logs

The server provides comprehensive logging:

- Connection events (user join/leave)
- Message broadcasting
- Room management
- Error tracking
- Graceful shutdown events

### Real-time Metrics

- Active user count
- Message throughput
- Connection status
- Room participation
- Error rates

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PORT` | `6000` | Server port |
| `NODE_ENV` | `development` | Environment mode |
| `CORS_ORIGIN` | `http://localhost:6000` | CORS allowed origins |

### TypeScript Configuration

The project uses strict TypeScript configuration for maximum type safety:

- ES2020 target
- CommonJS modules
- Strict type checking
- Source maps enabled
- Declaration files generated

## Production Deployment

### Build Process

```bash
# Clean build
rm -rf dist/
npm run build

# Verify build
ls -la dist/

# Test production build
node dist/server.js
```

### Production Considerations

- Process management: use PM2 or similar
- Load balancing: configure sticky sessions for Socket.IO
- Database: implement persistent storage for production
- Caching: add Redis for session management
- Monitoring: integrate with APM tools
- Security: implement authentication and rate limiting

## Security

- CORS configuration for controlled cross-origin access
- Input validation for message content
- Secure error responses
- Prepared for rate limiting implementation
- Secure socket session handling

## Recent Updates

### v1.0.0 (Current)

- Port migration from 3000 to 6000
- Production build with TypeScript compilation
- Enhanced client with comprehensive test interface
- RESTful monitoring endpoints
- Robust error management
- Complete README overhaul

## Contributing

This is part of the Artifact Virtual ecosystem. Contributions should follow enterprise standards:

1. Type safety: all code must be properly typed
2. Error handling: comprehensive error management
3. Documentation: code documentation and README updates
4. Testing: include appropriate tests
5. Performance: consider scalability and performance

## License

Part of the Artifact Virtual project. See main project license for details.

## Related Projects

- Artifact Virtual Core: main orchestration system
- Research Lab: advanced analysis capabilities
- Enterprise Suite: business management tools

---

**Status**: ✅ Production Ready | **Port**: 6000 | **Protocol**: HTTP/WebSocket | **Build**: TypeScript