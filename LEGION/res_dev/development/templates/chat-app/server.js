const express = require('express');
const http = require('http');
const { Server } = require('socket.io');
const bodyParser = require('body-parser');
const cors = require('cors');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Basic routes
app.get('/', (req, res) => {
    res.json({ 
        message: 'Chat App Server is running!', 
        timestamp: new Date().toISOString(),
        endpoints: {
            health: 'GET /',
            test: 'GET /test',
            websocket: `ws://localhost:${PORT}`
        }
    });
});

app.get('/test', (req, res) => {
    res.json({ 
        message: 'Test endpoint working!', 
        status: 'OK',
        server: 'Chat App'
    });
});

// Create HTTP server and Socket.IO
const server = http.createServer(app);
const io = new Server(server, {
    cors: {
        origin: process.env.CORS_ORIGIN || "http://localhost:3000",
        methods: ["GET", "POST"]
    }
});

// Socket.IO connection handling
io.on('connection', (socket) => {
    console.log('🔗 A user connected:', socket.id);
    
    // Handle joining a room
    socket.on('join-room', (roomId) => {
        socket.join(roomId);
        console.log(`👤 User ${socket.id} joined room ${roomId}`);
        socket.to(roomId).emit('user-joined', { userId: socket.id, roomId });
    });
    
    // Handle sending messages
    socket.on('send-message', (data) => {
        console.log('💬 Message received:', data);
        const messageData = {
            id: Date.now(),
            user: data.user || 'Anonymous',
            message: data.message,
            room: data.room,
            timestamp: new Date().toISOString()
        };
        
        // Send to all users in the room
        io.to(data.room).emit('new-message', messageData);
    });
    
    // Handle typing indicator
    socket.on('typing', (data) => {
        socket.to(data.room).emit('user-typing', { user: data.user, isTyping: data.isTyping });
    });

    // Handle disconnection
    socket.on('disconnect', () => {
        console.log('❌ User disconnected:', socket.id);
    });
});

// Error handling
app.use((err, req, res, next) => {
    console.error(err.stack);
    res.status(500).json({ error: 'Something broke!', message: err.message });
});

// Start server
server.listen(PORT, () => {
    console.log(`🚀 Chat App Server is running on http://localhost:${PORT}`);
    console.log(`📊 Socket.IO enabled for real-time communication`);
    console.log(`🔗 WebSocket endpoint: ws://localhost:${PORT}`);
    console.log(`📡 Test the API: curl http://localhost:${PORT}/test`);
});
