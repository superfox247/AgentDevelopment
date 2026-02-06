import React, { useEffect, useRef, useState } from 'react';
import { Send } from 'lucide-react';
import { BASELINE_AGENTS } from './chat/constants';
import { getMessageClass } from './chat/messageStyles';
import { useAgentChat } from './chat/useAgentChat';

export function ChatView() {
    const [input, setInput] = useState('');
    const [selectedAgent, setSelectedAgent] = useState<string>(BASELINE_AGENTS[0].id);
    const { history, isGenerating, sendMessage } = useAgentChat(selectedAgent);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (!scrollRef.current) {
            return;
        }

        const { scrollHeight } = scrollRef.current;
        scrollRef.current.scrollTo?.(0, scrollHeight);
    }, [history]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        await sendMessage(input);
        setInput('');
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
                <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-3">
                    {history.map((msg, i) => (
                        <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                            <div className={`max-w-[85%] rounded-lg px-3 py-2 ${getMessageClass(msg.role)}`}>{msg.text}</div>
                        </div>
                    ))}
                </div>
                <form onSubmit={handleSubmit} className="flex gap-2 p-4 border-t border-white/10 bg-black/20">
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
