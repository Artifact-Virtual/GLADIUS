import express from 'express';
// import UserService from '../services/UserService';

const router = express.Router();

// Fetch user profile by ID
router.get('/:id', async (req, res) => {
    try {
        // const user = await UserService.getUserById(req.params.id);
        // Mock user for testing
        const user = { id: req.params.id, name: 'Test User', email: 'test@example.com' };
        if (!user) {
            return res.status(404).json({ message: 'User not found' });
        }
        res.json(user);
    } catch (error) {
        res.status(500).json({ message: 'Server error', error });
    }
});

// Update user information
router.put('/:id', async (req, res) => {
    try {
        // const updatedUser = await UserService.updateUser(req.params.id, req.body);
        // Mock updated user for testing
        const updatedUser = { id: req.params.id, ...req.body };
        if (!updatedUser) {
            return res.status(404).json({ message: 'User not found' });
        }
        res.json(updatedUser);
    } catch (error) {
        res.status(500).json({ message: 'Server error', error });
    }
});

export default router;
