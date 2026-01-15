import bodyParser from 'body-parser';
import cors from 'cors';
import express, { NextFunction, Request, Response } from 'express';

const app = express();

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Basic health check route
app.get('/', (req: Request, res: Response) => {
    res.json({ message: 'Chat App Server is running!', timestamp: new Date().toISOString() });
});

// Simple test route
app.get('/test', (req: Request, res: Response) => {
    res.json({ message: 'Test endpoint working!' });
});

// Error handling middleware
app.use((err: any, req: Request, res: Response, next: NextFunction) => {
    console.error(err.stack);
    res.status(500).send('Something broke!');
});

export default app;