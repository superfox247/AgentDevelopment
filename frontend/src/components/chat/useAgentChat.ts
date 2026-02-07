import { useCallback, useState } from 'react';
import { apiClient } from '../../api/client';
import { INITIAL_AGENT_MESSAGE } from './constants';
import type { Message } from './types';

function createSessionId(): string {
    return `session-${Math.random().toString(36).slice(2, 11)}`;
}

function parseStreamLine(line: string): Message | null {
    if (!line.trim()) {
        return null;
    }

    try {
        const data = JSON.parse(line) as { type?: string; text?: string };
        if (data.type === 'system_signal' && data.text) {
            return { role: 'system', text: data.text };
        }
        if (data.type === 'tool_use' && data.text) {
            return { role: 'tool', text: data.text };
        }
        if (data.type === 'agent_thought' && data.text) {
            return { role: 'agent', text: data.text };
        }
    } catch {
        return null;
    }

    return null;
}

async function processStream(res: Response, onMessage: (message: Message) => void): Promise<void> {
    if (!res.body) {
        throw new Error('No response body');
    }

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
        const { done, value } = await reader.read();
        if (done) {
            return;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() ?? '';

        for (const line of lines) {
            const parsed = parseStreamLine(line);
            if (parsed) {
                onMessage(parsed);
            }
        }
    }
}

export function useAgentChat(selectedAgent: string) {
    const [sessionId] = useState(createSessionId);
    const [history, setHistory] = useState<Message[]>([{ role: 'agent', text: INITIAL_AGENT_MESSAGE }]);
    const [isGenerating, setIsGenerating] = useState(false);

    const sendMessage = useCallback(
        async (rawMessage: string) => {
            const userMessage = rawMessage.trim();
            if (!userMessage || isGenerating) {
                return;
            }

            setHistory((prev) => [...prev, { role: 'user', text: userMessage }]);
            setIsGenerating(true);

            try {
                const response = await apiClient.chatWithAgentStream(selectedAgent, userMessage, sessionId);
                await processStream(response, (message) => {
                    setHistory((prev) => [...prev, message]);
                });
            } catch (error) {
                setHistory((prev) => [
                    ...prev,
                    { role: 'system', text: `Error: ${error instanceof Error ? error.message : String(error)}` },
                ]);
            } finally {
                setIsGenerating(false);
            }
        },
        [isGenerating, selectedAgent, sessionId],
    );

    return {
        history,
        isGenerating,
        sendMessage,
    };
}
