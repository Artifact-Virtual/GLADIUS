export interface Room {
    id: string;
    name: string;
    userIds: string[];
}

export class RoomModel {
    private rooms: Room[] = [];

    createRoom(name: string, userIds: string[]): Room {
        const newRoom: Room = {
            id: this.generateId(),
            name,
            userIds,
        };
        this.rooms.push(newRoom);
        return newRoom;
    }

    getRoomById(id: string): Room | undefined {
        return this.rooms.find(room => room.id === id);
    }

    getAllRooms(): Room[] {
        return this.rooms;
    }

    private generateId(): string {
        return Math.random().toString(36).substr(2, 9);
    }
}