export interface Message {
    id: string;
    content: string;
    senderId: string;
    roomId: string;
    timestamp: Date;
}

export class MessageModel {
    constructor(public message: Message) {}

    static createMessage(content: string, senderId: string, roomId: string): Message {
        return {
            id: this.generateId(),
            content,
            senderId,
            roomId,
            timestamp: new Date(),
        };
    }

    private static generateId(): string {
        return Math.random().toString(36).substr(2, 9);
    }
}