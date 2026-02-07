export type MessageRole = 'agent' | 'user' | 'system' | 'tool';

export interface Message {
    role: MessageRole;
    text: string;
}
