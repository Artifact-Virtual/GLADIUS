import dotenv from 'dotenv';
import express, { Request, Response } from 'express';
import http from 'http';
import path from 'path';
import { Server, Socket } from 'socket.io';

// Load environment variables
dotenv.config();

const PORT = process.env.PORT || 6000;

// Create Express app
const app = express();

// Middleware
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Serve static files
app.use(express.static(path.join(__dirname, '../public')));

// API Routes
app.get('/api/health', (req: Request, res: Response) => {
    res.json({ 
        status: 'OK', 
        message: 'Artifact Virtual Chat Server is running',
        timestamp: new Date().toISOString(),
        port: PORT,
        version: '1.0.0'
    });
});

app.get('/test', (req: Request, res: Response) => {
    res.json({ 
        message: 'Test endpoint working!', 
        status: 'OK', 
        server: 'Artifact Virtual Chat App',
        port: PORT
    });
});

// Interface definitions
interface User {
    username: string;
    socketId: string;
    joinedAt: Date;
}

interface ChatMessage {
    id: string;
    username: string;
    message: string;
    timestamp: string;
    room?: string;
}

// Create HTTP server and Socket.IO
const server = http.createServer(app);
const io = new Server(server, {
    cors: {
        origin: process.env.CORS_ORIGIN || [`http://localhost:${PORT}`, "http://localhost:3000"],
        methods: ["GET", "POST"],
        credentials: true
    }
});

// Connected users storage
const connectedUsers = new Map<string, User>();
const chatHistory: ChatMessage[] = [];

// Socket.io connection handling
io.on('connection', (socket: Socket) => {
    console.log(`📡 User connected: ${socket.id}`);
    
    // Handle user joining
    socket.on('join', (data: { username: string }) => {
        const { username } = data;
        const user: User = {
            username,
            socketId: socket.id,
            joinedAt: new Date()
        };
        
        connectedUsers.set(socket.id, user);
        
        console.log(`👤 User ${username} joined (${socket.id})`);
        
        // Send welcome message to the user
        socket.emit('message', {
            id: Date.now().toString(),
            username: 'System',
            message: `Welcome to Artifact Virtual Chat, ${username}!`,
            timestamp: new Date().toISOString()
        });
        
        // Notify others about new user
        socket.broadcast.emit('user_joined', { username });
        
        // Send current user count
        io.emit('user_count', { count: connectedUsers.size });
        
        // Send recent chat history to new user
        if (chatHistory.length > 0) {
            const recentMessages = chatHistory.slice(-10); // Last 10 messages
            socket.emit('chat_history', recentMessages);
        }
    });
    
    // Handle message sending
    socket.on('message', (data: { username: string; message: string; timestamp?: string }) => {
        const { username, message, timestamp } = data;
        
        const chatMessage: ChatMessage = {
            id: Date.now().toString(),
            username,
            message,
            timestamp: timestamp || new Date().toISOString()
        };
        
        // Store message in history
        chatHistory.push(chatMessage);
        
        // Keep only last 100 messages in memory
        if (chatHistory.length > 100) {
            chatHistory.shift();
        }
        
        console.log(`💬 Message from ${username}: ${message}`);
        
        // Broadcast message to all connected clients except sender
        socket.broadcast.emit('message', chatMessage);
    });
    
    // Handle room joining (for future room functionality)
    socket.on('join-room', (roomId: string) => {
        socket.join(roomId);
        console.log(`🏠 User ${socket.id} joined room ${roomId}`);
        
        // Notify room members
        socket.to(roomId).emit('user_joined_room', {
            username: connectedUsers.get(socket.id)?.username || 'Unknown',
            room: roomId
        });
    });
    
    // Handle room messages
    socket.on('send-message', (data: { room: string; message: string; user: string }) => {
        const { room, message, user } = data;
        console.log(`📨 Room message from ${user} in ${room}: ${message}`);
        
        const roomMessage: ChatMessage = {
            id: Date.now().toString(),
            username: user,
            message,
            timestamp: new Date().toISOString(),
            room
        };
        
        io.to(room).emit('new-message', roomMessage);
    });

    // Handle typing indicators
    socket.on('typing', (data: { username: string; isTyping: boolean }) => {
        socket.broadcast.emit('user_typing', data);
    });

    // Handle room creation
    socket.on('create-room', (data: { id: string; name: string; createdBy: string; createdAt: string }) => {
        const { id, name, createdBy, createdAt } = data;
        
        console.log(`🏠 Room created: ${name} by ${createdBy}`);
        
        // Store room information (in production, this would be in a database)
        // For now, we'll just broadcast the room creation
        
        // Join the creator to the room
        socket.join(id);
        
        // Broadcast room creation to all users
        io.emit('room_created', {
            id,
            name,
            createdBy,
            createdAt,
            members: 1
        });
        
        // Confirm to creator
        socket.emit('room_joined', { id, name });
    });

    // Handle disconnection
    socket.on('disconnect', () => {
        const user = connectedUsers.get(socket.id);
        if (user) {
            console.log(`👋 User ${user.username} disconnected (${socket.id})`);
            connectedUsers.delete(socket.id);
            
            // Notify others about user leaving
            socket.broadcast.emit('user_left', { username: user.username });
            
            // Send updated user count
            io.emit('user_count', { count: connectedUsers.size });
        } else {
            console.log(`🔌 User disconnected: ${socket.id}`);
        }
    });
    
    // Handle connection errors
    socket.on('error', (error: Error) => {
        console.error(`❌ Socket error for ${socket.id}:`, error);
    });
});

// API endpoint to get connected users
app.get('/api/users', (req: Request, res: Response) => {
    const users = Array.from(connectedUsers.values()).map(user => ({
        username: user.username,
        joinedAt: user.joinedAt
    }));
    
    res.json({
        users,
        count: users.length,
        timestamp: new Date().toISOString()
    });
});

// API endpoint to get chat history
app.get('/api/messages', (req: Request, res: Response) => {
    const limit = parseInt(req.query.limit as string) || 50;
    const messages = chatHistory.slice(-limit);
    
    res.json({
        messages,
        count: messages.length,
        total: chatHistory.length,
        timestamp: new Date().toISOString()
    });
});

// Error handling middleware
app.use((err: Error, req: Request, res: Response, next: Function) => {
    console.error('❌ Server error:', err.stack);
    res.status(500).json({
        error: 'Internal server error',
        message: process.env.NODE_ENV === 'development' ? err.message : 'An error occurred'
    });
});

// 404 handler
app.use((req: Request, res: Response) => {
    res.status(404).json({
        error: 'Not found',
        message: `Route ${req.method} ${req.path} not found`
    });
});

// Start server
server.listen(PORT, () => {
    console.log(`🚀 Artifact Virtual Chat Server running on port ${PORT}`);
    console.log(`📊 Socket.IO enabled for real-time communication`);
    console.log(`🌐 Web interface: http://localhost:${PORT}`);
    console.log(`🔗 WebSocket endpoint: ws://localhost:${PORT}`);
    console.log(`⚡ Environment: ${process.env.NODE_ENV || 'development'}`);
    console.log(`📋 API Endpoints:`);
    console.log(`   - GET /api/health - Health check`);
    console.log(`   - GET /api/users - Connected users`);
    console.log(`   - GET /api/messages - Chat history`);
    console.log(`   - GET /test - Test endpoint`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
    console.log('🛑 SIGTERM received, shutting down gracefully...');
    server.close(() => {
        console.log('💤 Server closed');
        process.exit(0);
    });
});

process.on('SIGINT', () => {
    console.log('🛑 SIGINT received, shutting down gracefully...');
    server.close(() => {
        console.log('💤 Server closed');
        process.exit(0);
    });
});

export default app;