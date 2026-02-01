import React, { useState, useRef, useEffect } from 'react';
import { apiClient } from '../api/client';
import { Send } from 'lucide-react';

const BASELINE_AGENTS = [
    { id: 'researcher_agent', label: 'Researcher' },
    { id: 'customer_service_agent', label: 'Customer Service' },
] as const;

type MessageRole = 'agent' | 'user' | 'system' | 'tool';

interface Message {
    role: MessageRole;
    text: string;
}

function getMessageClass(role: MessageRole): string {
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

export function ChatView() {
    const [sessionId] = useState(() => 'session-' + Math.random().toString(36).slice(2, 11));
    const [input, setInput] = useState('');
    const [selectedAgent, setSelectedAgent] = useState<string>(BASELINE_AGENTS[0].id);
    const [history, setHistory] = useState<Message[]>([
        { role: 'agent', text: "Hello. Choose an agent and send a message." },
    ]);
    const [isGenerating, setIsGenerating] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        scrollRef.current?.scrollTo(0, scrollRef.current.scrollHeight);
    }, [history]);

    const parseLine = (line: string) => {
        if (!line.trim()) return;
        try {
            const data = JSON.parse(line) as { type?: string; text?: string };
            if (data.type === 'system_signal' && data.text) {
                setHistory((prev) => [...prev, { role: 'system', text: data.text! }]);
            } else if (data.type === 'tool_use' && data.text) {
                setHistory((prev) => [...prev, { role: 'tool', text: data.text! }]);
            }
        } catch {
            /* ignore */
        }
    };

    const processStream = async (res: Response) => {
        if (!res.body) throw new Error('No response body');
        const reader = res.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() ?? '';
            lines.forEach(parseLine);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isGenerating) return;
        const userMsg = input.trim();
        setInput('');
        setHistory((prev) => [...prev, { role: 'user', text: userMsg }]);
        setIsGenerating(true);
        try {
            const res = await apiClient.chatWithAgentStream(selectedAgent, userMsg, sessionId);
            await processStream(res);
        } catch (err) {
            setHistory((prev) => [
                ...prev,
                { role: 'system', text: `Error: ${err instanceof Error ? err.message : String(err)}` },
            ]);
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="h-full flex flex-col max-w-3xl mx-auto">
            <div className="mb-4">
                <label htmlFor="agent-select" className="block text-sm font-medium text-zinc-400 mb-1">
                    Agent
                </label>
                <select
                    id="agent-select"
                    value={selectedAgent}
                    onChange={(e) => setSelectedAgent(e.target.value)}
                    className="bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white text-sm focus:outline-none focus:border-indigo-500"
                    aria-label="Select agent"
                >
                    {BASELINE_AGENTS.map((a) => (
                        <option key={a.id} value={a.id}>
                            {a.label}
                        </option>
                    ))}
                </select>
            </div>

            <div className="flex-1 flex flex-col min-h-0 rounded-xl border border-white/10 bg-white/5 overflow-hidden">
                <div
                    ref={scrollRef}
                    className="flex-1 overflow-y-auto p-4 space-y-3"
                >
                    {history.map((msg, i) => (
                        <div
                            key={i}
                            className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                        >
                            <div
                                className={`max-w-[85%] rounded-lg px-3 py-2 ${getMessageClass(msg.role)}`}
                            >
                                {msg.text}
                            </div>
                        </div>
                    ))}
                </div>
                <form
                    onSubmit={handleSubmit}
                    className="flex gap-2 p-4 border-t border-white/10 bg-black/20"
                >
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type a message..."
                        className="flex-1 bg-white/5 border border-white/10 rounded-lg px-3 py-2 text-white placeholder-zinc-500 focus:outline-none focus:border-indigo-500"
                        disabled={isGenerating}
                        aria-label="Message input"
                    />
                    <button
                        type="submit"
                        disabled={isGenerating || !input.trim()}
                        className="px-4 py-2 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
                        aria-label="Send"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </form>
            </div>
        </div>
    );
}
