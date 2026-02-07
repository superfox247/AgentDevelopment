import type { MessageRole } from './types';

export function getMessageClass(role: MessageRole): string {
    switch (role) {
        case 'user':
            return 'bg-indigo-600 text-white';
        case 'system':
            return 'bg-green-500/20 text-green-300 border border-green-500/30';
        case 'tool':
            return 'bg-gray-800/50 text-gray-400 text-xs font-mono';
        default:
            return 'bg-white/10 text-gray-100';
    }
}
