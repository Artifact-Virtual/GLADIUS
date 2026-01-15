export interface User {
    id: string;
    username: string;
    password: string;
}

export interface Message {
    id: string;
    content: string;
    senderId: string;
    roomId: string;
}

export interface Room {
    id: string;
    name: string;
    userIds: string[];
}