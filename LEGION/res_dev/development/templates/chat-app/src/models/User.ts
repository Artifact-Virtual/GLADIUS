export interface User {
    id: string;
    username: string;
    password: string;
}

export class UserModel {
    private users: User[] = [];

    constructor() {}

    createUser(username: string, password: string): User {
        const newUser: User = {
            id: this.generateId(),
            username,
            password,
        };
        this.users.push(newUser);
        return newUser;
    }

    getUserById(id: string): User | undefined {
        return this.users.find(user => user.id === id);
    }

    getAllUsers(): User[] {
        return this.users;
    }

    private generateId(): string {
        return Math.random().toString(36).substr(2, 9);
    }
}