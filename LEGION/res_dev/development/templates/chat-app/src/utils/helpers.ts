export const generateUniqueId = (): string => {
    return Math.random().toString(36).substr(2, 9);
};

export const formatTimestamp = (timestamp: number): string => {
    const date = new Date(timestamp);
    return date.toLocaleString();
};

export const validateEmail = (email: string): boolean => {
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return regex.test(email);
};

export const sanitizeInput = (input: string): string => {
    return input.replace(/<[^>]*>/g, '');
};