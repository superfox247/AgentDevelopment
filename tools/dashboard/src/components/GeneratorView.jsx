import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Play } from 'lucide-react';

export function GeneratorView() {
    const [sessionId] = useState(() => 'session-' + Math.random().toString(36).substr(2, 9));
    const [input, setInput] = useState('');
    const [history, setHistory] = useState([
        { role: 'agent', text: "Hello! I'm your Content Assistant. I can help you create Articles, Courses, or Social Posts. What would you like to build today?" }
    ]);
    const [isGenerating, setIsGenerating] = useState(false);
    const scrollRef = useRef(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [history]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!input.trim() || isGenerating) return;

        const userMsg = input;
        setInput('');
        setHistory(prev => [...prev, { role: 'user', text: userMsg }]);
        setIsGenerating(true);

        try {
            const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8010';
            const res = await fetch(`${API_URL}/api/chat/customer_service`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMsg, session_id: sessionId })
            });

            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop(); // Keep incomplete line

                for (const line of lines) {
                    if (!line.trim()) continue;
                    try {
                        const data = JSON.parse(line);

                        if (data.type === 'agent_thought') {
                            // Optional: Show thoughts? For now, maybe skip or show as subtle logs
                            console.log('Thought:', data.text);
                        } else if (data.type === 'system_signal' && data.signal === 'research_started') {
                            setHistory(prev => [...prev, { role: 'system', text: data.text }]);
                        } else if (data.type === 'tool_use') {
                            setHistory(prev => [...prev, { role: 'tool', text: data.text }]);
                        } else {
                            // Standard message (CustomerServiceResponse usually comes inside tool args or final extraction)
                            // But wait, server.py _extract_event_data handles thoughts. 
                            // Real agent output usually comes as `Content` parts.
                            // My server logic sends thoughts/messages.

                            // If it's the final output from CustomerService, it might be buried.
                            // Let's assume server logic sends "message" type if implemented?
                            // Wait, server.py only sends 'agent_thought' or 'tool_use'.
                            // Ah, the server.py logic:
                            // if event.content... -> type: agent_thought.

                            // CustomerService agent output is structured (JSON). 
                            // The generic `_extract_event_data` treats it as text/thought.
                            // So we need to parse the JSON string in the thought if it looks like a response.

                            if (data.type === 'agent_thought') {
                                // Clean up if it's JSON-like
                                let text = data.text;
                                if (text.trim().startsWith('{')) {
                                    try {
                                        const json = JSON.parse(text);
                                        if (json.message) {
                                            setHistory(prev => [...prev, { role: 'agent', text: json.message }]);
                                        } else {
                                            setHistory(prev => [...prev, { role: 'agent', text: text }]);
                                        }
                                    } catch {
                                        setHistory(prev => [...prev, { role: 'agent', text: text }]);
                                    }
                                } else {
                                    setHistory(prev => [...prev, { role: 'agent', text: text }]);
                                }
                            }
                        }
                    } catch (e) {
                        console.error("Error parsing line", e);
                    }
                }
            }
        } catch (err) {
            setHistory(prev => [...prev, { role: 'system', text: `Error: ${err.message}` }]);
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="h-[calc(100vh-12rem)] flex flex-col glass-panel rounded-xl overflow-hidden">
            <div className="flex-1 overflow-y-auto p-6 space-y-4" ref={scrollRef}>
                {history.map((msg, idx) => (
                    <div key={idx} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-[80%] rounded-lg px-4 py-3 ${msg.role === 'user'
                            ? 'bg-indigo-600 text-white'
                            : msg.role === 'system'
                                ? 'bg-green-500/20 text-green-300 border border-green-500/30'
                                : msg.role === 'tool'
                                    ? 'bg-gray-800/50 text-gray-400 text-xs font-mono'
                                    : 'bg-white/10 text-gray-100'
                            }`}>
                            {msg.text}
                        </div>
                    </div>
                ))}
                {isGenerating && (
                    <div className="flex justify-start">
                        <div className="bg-white/5 rounded-lg px-4 py-3 flex items-center space-x-2">
                            <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                            <span className="text-gray-400 text-sm">Thinking...</span>
                        </div>
                    </div>
                )}
            </div>

            <div className="p-4 border-t border-white/5 bg-black/20">
                <form onSubmit={handleSubmit} className="flex space-x-2">
                    <input
                        type="text"
                        value={input}
                        onChange={(e) => setInput(e.target.value)}
                        placeholder="Type a message..."
                        className="flex-1 bg-white/5 border border-white/10 rounded-lg px-4 py-2 focus:outline-none focus:border-indigo-500 transition-colors text-white placeholder-gray-500"
                        disabled={isGenerating}
                    />
                    <button
                        type="submit"
                        disabled={isGenerating || !input.trim()}
                        className="btn-primary px-4 py-2 rounded-lg flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        <Send className="w-5 h-5" />
                    </button>
                </form>
            </div>
        </div>
    );
}
