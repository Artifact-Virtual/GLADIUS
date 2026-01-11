# Enterprise Automation Dashboard

## Overview

Production-ready web dashboard for the Enterprise Automation Suite providing real-time monitoring, content management, analytics, and configuration.

## Architecture

### Backend (Flask + SocketIO)
- **REST API** for all operations
- **WebSocket** support for real-time updates
- **JWT authentication** for security
- **CORS enabled** for frontend integration

### Frontend (React + Ant Design)
- **Modern React 18** with hooks
- **Ant Design** component library
- **Vite** for fast development
- **React Router** for navigation
- **Axios** for API calls
- **Socket.IO** for real-time updates

## Features

### 1. Real-Time Monitoring
- System status (running/stopped)
- Active integrations (ERP + Social Media)
- Recent activity feed
- Live notifications via WebSocket

### 2. Content Calendar
- Visual scheduling interface
- Multi-platform view
- Drag-and-drop scheduling (planned)
- Bulk operations

### 3. Analytics Dashboard
- Engagement metrics
- Growth trends
- Platform comparisons
- Custom reports

### 4. Configuration UI
- Platform enable/disable
- Credential management
- Automation rules
- User settings

### 5. Manual Controls
- Emergency stop
- Manual post creation
- Schedule overrides
- Testing tools

## Setup

### Backend Setup

```bash
cd automata/dashboard/backend

# Install dependencies
pip install flask flask-cors flask-socketio flask-jwt-extended

# Run server
python app.py
```

Server will start on `http://localhost:5000`

### Frontend Setup

```bash
cd automata/dashboard/frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

Development server will start on `http://localhost:3000`

## API Endpoints

### Authentication
- `POST /api/auth/login` - Login and get JWT token
- `GET /api/auth/verify` - Verify token

### System Status
- `GET /api/status` - Get current system status
- `POST /api/status/start` - Start automation system
- `POST /api/status/stop` - Stop automation system

### Configuration
- `GET /api/config` - Get configuration
- `PUT /api/config` - Update configuration
- `GET /api/config/platforms` - Get enabled platforms

### Social Media
- `GET /api/social/posts` - Get scheduled posts
- `POST /api/social/post` - Create/schedule post
- `DELETE /api/social/post/<id>` - Cancel post

### Analytics
- `GET /api/analytics` - Get system analytics
- `GET /api/analytics/social/<platform>` - Platform-specific analytics

### ERP
- `POST /api/erp/sync` - Trigger ERP synchronization

## WebSocket Events

### Client -> Server
- `connect` - Establish connection
- `subscribe_status` - Subscribe to status updates

### Server -> Client
- `connected` - Connection established
- `status_update` - Real-time status changes
- `notification` - System notifications

## Configuration

### Backend Configuration

Edit `~/.automata/config.json`:

```json
{
  "dashboard": {
    "host": "0.0.0.0",
    "port": 5000,
    "secret_key": "your-secret-key",
    "enable_auth": true,
    "admin_username": "admin",
    "admin_password": "secure-password"
  }
}
```

### Frontend Configuration

Create `.env` file in frontend directory:

```
VITE_API_URL=http://localhost:5000/api
```

## Security

- **JWT Authentication** with token expiration
- **CORS** properly configured
- **Password hashing** (implement in production)
- **HTTPS** recommended for production
- **Rate limiting** (implement in production)

## Extensibility

### Adding New Dashboard Pages

1. Create page component in `src/pages/`
2. Add route in `src/App.jsx`
3. Add navigation item in `Dashboard.jsx`

### Adding New API Endpoints

1. Add endpoint handler in `backend/app.py`
2. Add API method in `frontend/src/utils/api.js`
3. Use in components

### Adding Real-Time Features

1. Define WebSocket event in backend
2. Subscribe to event in frontend
3. Handle updates in UI

## Deployment

### Production Build

```bash
# Backend
pip install -r requirements.txt
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app

# Frontend
npm run build
# Serve dist/ folder with nginx or similar
```

### Docker Deployment (Planned)

```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "5000:5000"
  frontend:
    build: ./frontend
    ports:
      - "3000:80"
```

## Development Roadmap

### Phase 1 (Current)
- [x] Backend API structure
- [x] Authentication system
- [x] Basic REST endpoints
- [ ] Frontend app structure
- [ ] Login page
- [ ] Dashboard layout

### Phase 2
- [ ] Overview dashboard
- [ ] Content calendar
- [ ] Analytics charts
- [ ] Configuration UI

### Phase 3
- [ ] Real-time WebSocket updates
- [ ] Notifications system
- [ ] Advanced analytics
- [ ] Bulk operations

### Phase 4
- [ ] Mobile responsive design
- [ ] Dark mode
- [ ] Export/reporting
- [ ] User management

## Tech Stack

### Backend
- Python 3.12+
- Flask 3.0+
- Flask-SocketIO
- Flask-JWT-Extended
- Flask-CORS

### Frontend
- React 18.2+
- Vite 5.0+
- Ant Design 5.12+
- Axios 1.6+
- Socket.IO Client 4.5+
- Recharts 2.10+

## License

Private development repository. All rights reserved.

## Support

For issues and questions, refer to the main Enterprise Automation Suite documentation.
