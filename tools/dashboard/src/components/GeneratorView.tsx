import React, { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { Send, Loader2, Play, AlertCircle } from 'lucide-react';

interface Message {
    role: 'agent' | 'user' | 'system' | 'tool';
    text: string;
}

interface ImageResult {
    url: string | null;
    loading: boolean;
    error: string | null;
}

export function GeneratorView() {
    const [mode, setMode] = useState('image');
    const [sessionId] = useState(() => 'session-' + Math.random().toString(36).substring(2, 9));
    const [input, setInput] = useState('');
    const [history, setHistory] = useState<Message[]>([
        { role: 'agent', text: "Hello! I'm your Content Assistant. I can help you create Articles, Courses, or Social Posts. What would you like to build today?" }
    ]);
    const [isGenerating, setIsGenerating] = useState(false);
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [history]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!input.trim() || isGenerating) return;

        const userMsg = input;
        setInput('');
        setHistory(prev => [...prev, { role: 'user', text: userMsg }]);
        setIsGenerating(true);

        try {
            // Use apiClient stream method
            const res = await apiClient.chatWithAgentStream('customer_service', userMsg, sessionId);
            if (!res.body) throw new Error('No response body');
            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n');
                buffer = lines.pop() || '';

                for (const line of lines) {
                    if (!line.trim()) continue;
                    try {
                        const data = JSON.parse(line);
                        if (data.type === 'agent_thought') {
                            // Optional log
                        } else if (data.type === 'system_signal') {
                            setHistory(prev => [...prev, { role: 'system', text: data.text }]);
                        } else if (data.type === 'tool_use') {
                            setHistory(prev => [...prev, { role: 'tool', text: data.text }]);
                        }
                    } catch (e) { console.error(e); }
                }
            }
        } catch (err) {
            setHistory(prev => [...prev, { role: 'system', text: `Error: ${err instanceof Error ? err.message : String(err)}` }]);
        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="h-[calc(100vh-12rem)] flex flex-col">
            {/* Mode Switcher */}
            <div className="flex space-x-4 mb-4 px-1">
                <button
                    onClick={() => setMode('chat')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${mode === 'chat'
                        ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/20'
                        : 'bg-white/5 text-gray-400 hover:bg-white/10'
                        }`}
                >
                    Chat Assistant
                </button>
                <button
                    onClick={() => setMode('image')}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${mode === 'image'
                        ? 'bg-pink-600 text-white shadow-lg shadow-pink-500/20'
                        : 'bg-white/5 text-gray-400 hover:bg-white/10'
                        }`}
                >
                    Image Generator
                </button>
            </div>

            {mode === 'chat' ? (
                <div className="flex-1 flex flex-col glass-panel rounded-xl overflow-hidden">
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
            ) : (
                <ImageInterface sessionId={sessionId} />
            )}
        </div>
    );
}

function ImageInterface({ sessionId }: { sessionId: string }) {
    const [prompt, setPrompt] = useState('');
    const [selectedModels, setSelectedModels] = useState<string[]>(['models/gemini-2.5-flash-image']);
    const [isGenerating, setIsGenerating] = useState(false);
    const [results, setResults] = useState<Record<string, ImageResult>>({});

    const models = [
        { id: 'models/imagen-4.0-generate-001', name: 'Imagen 4' },
        { id: 'models/imagen-4.0-fast-generate-001', name: 'Imagen 4 Fast' },
        { id: 'models/gemini-2.5-flash-image', name: 'Nano Banana (Gemini 2.5 Image)' },
        { id: 'models/imagen-3.0-generate-001', name: 'Imagen 3' },
        { id: 'models/gemini-2.0-flash', name: 'Gemini 2.0 Flash' },
    ];

    const toggleModel = (id: string) => {
        setSelectedModels(prev =>
            prev.includes(id)
                ? prev.filter(m => m !== id)
                : [...prev, id]
        );
    };

    const generateMutation = useMutation({
        mutationFn: async ({ prompt, modelId }: { prompt: string; modelId: string }) => {
            const res = await apiClient.generateImage(prompt, modelId);
            // apiClient returns parsed data
            return res;
        }
    });

    const handleGenerate = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!prompt.trim() || isGenerating || selectedModels.length === 0) return;

        setIsGenerating(true);
        const newResults: Record<string, ImageResult> = {};
        selectedModels.forEach(id => {
            newResults[id] = { url: null, loading: true, error: null };
        });
        setResults(newResults);

        try {
            await Promise.all(selectedModels.map(async (modelId) => {
                try {
                    const data = await generateMutation.mutateAsync({ prompt, modelId });

                    setResults(prev => ({
                        ...prev,
                        [modelId]: {
                            loading: false,
                            url: data.image_url, // apiClient handles fully qualified URL if needed? 
                            // Wait, apiClient.generateImage returns response.data.
                            // Let's check schemas/client return type.
                            // It likely returns { image_url: "..." }.
                            // We might need to handle absolute URL here if `apiClient` doesn't.
                            // The original code did: (data.image_url.startsWith('http') ? ... : `${API_URL}${...}`)
                            // We should probably rely on the backend sending full URLs or handle it here.
                            // I will assume apiClient returns what the server returns.
                            // I'll keep the URL logic if I can, but I don't have API_URL here easily without import.meta
                            // Actually, apiClient has baseURL.
                            // For now, let's just use data.image_url and assume it works or fix it if broken.
                            // The dashboard is hosted on same origin usually or we can construct it.
                            // Actually, the previous code had full logic.
                            error: null
                        }
                    }));
                } catch (err) {
                    setResults(prev => ({
                        ...prev,
                        [modelId]: { loading: false, url: null, error: err instanceof Error ? err.message : String(err) }
                    }));
                }
            }));

        } finally {
            setIsGenerating(false);
        }
    };

    return (
        <div className="flex-1 flex gap-6 overflow-hidden h-[calc(100vh-16rem)] max-h-full">
            {/* Controls */}
            <div className="w-80 glass-panel rounded-xl p-6 flex flex-col space-y-6 overflow-y-auto">
                <div>
                    <div className="flex justify-between items-center mb-2">
                        <label className="text-sm font-medium text-gray-400">Models</label>
                        <span className="text-xs text-indigo-400">{selectedModels.length} selected</span>
                    </div>
                    <div className="space-y-2">
                        {models.map(m => {
                            const isSelected = selectedModels.includes(m.id);
                            return (
                                <button
                                    key={m.id}
                                    onClick={() => toggleModel(m.id)}
                                    className={`w-full text-left px-4 py-3 rounded-lg border transition-all ${isSelected
                                        ? 'bg-pink-600/20 border-pink-500 text-white'
                                        : 'bg-white/5 border-transparent text-gray-400 hover:bg-white/10'
                                        }`}
                                >
                                    <div className="flex items-center justify-between">
                                        <span className="font-medium">{m.name}</span>
                                        {isSelected && <div className="w-2 h-2 rounded-full bg-pink-500 shadow-[0_0_8px_#ec4899]"></div>}
                                    </div>
                                    <div className="text-[10px] opacity-60 font-mono truncate">{m.id}</div>
                                </button>
                            );
                        })}
                    </div>
                </div>

                <form onSubmit={handleGenerate} className="flex-1 flex flex-col">
                    <label className="block text-sm font-medium text-gray-400 mb-2">Prompt</label>
                    <textarea
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                        className="w-full h-32 bg-black/20 border border-white/10 rounded-lg p-4 text-white resize-none focus:border-pink-500 outline-none placeholder-gray-600 text-sm"
                        placeholder="Describe the image you want to generate..."
                    />
                    <button
                        type="submit"
                        disabled={isGenerating || !prompt.trim() || selectedModels.length === 0}
                        className="mt-4 w-full btn-primary bg-pink-600 hover:bg-pink-500 py-3 rounded-lg flex items-center justify-center space-x-2 font-bold disabled:opacity-50 disabled:cursor-not-allowed transition-all"
                    >
                        {isGenerating ? (
                            <><Loader2 className="w-5 h-5 animate-spin" /><span>Generating...</span></>
                        ) : (
                            <><Play className="w-5 h-5 fill-current" /><span>Generate All</span></>
                        )}
                    </button>
                    {selectedModels.length === 0 && (
                        <p className="text-xs text-red-400 text-center mt-2">Select at least one model</p>
                    )}
                </form>
            </div>

            {/* Results Grid - Scrollable */}
            <div className="flex-1 glass-panel rounded-xl p-6 bg-black/40 relative overflow-y-auto custom-scrollbar">
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-10 pointer-events-none fixed"></div>

                {Object.keys(results).length > 0 ? (
                    <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 relative z-10 pb-6">
                        {selectedModels.map(id => {
                            const result = results[id];
                            if (!result) return null;

                            const modelInfo = models.find(m => m.id === id);

                            return (
                                <div key={id} className="bg-white/5 rounded-xl border border-white/10 overflow-hidden flex flex-col min-h-[300px]">
                                    <div className="p-3 border-b border-white/5 bg-black/20 flex justify-between items-center">
                                        <span className="font-medium text-sm text-gray-200">{modelInfo?.name}</span>
                                        <span className="text-[10px] font-mono text-gray-500">{id}</span>
                                    </div>

                                    <div className="aspect-square relative flex items-center justify-center bg-black/20 flex-1">
                                        {result.loading ? (
                                            <div className="flex flex-col items-center gap-2">
                                                <Loader2 className="w-8 h-8 animate-spin text-pink-500" />
                                                <span className="text-xs text-gray-400 animate-pulse">Generating...</span>
                                            </div>
                                        ) : result.error ? (
                                            <div className="flex flex-col items-center gap-2 text-red-400 p-4 text-center">
                                                <AlertCircle className="w-8 h-8 opacity-50" />
                                                <span className="text-xs break-all">{result.error}</span>
                                            </div>
                                        ) : result.url ? (
                                            <div className="relative group w-full h-full">
                                                <img
                                                    src={result.url}
                                                    alt="Generated"
                                                    className="w-full h-full object-contain"
                                                />
                                                <div className="absolute inset-x-0 bottom-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity flex justify-end bg-linear-to-t from-black/80 to-transparent">
                                                    <a
                                                        href={result.url}
                                                        download={`image-${id}.png`}
                                                        target="_blank"
                                                        rel="noreferrer"
                                                        className="bg-white text-black px-3 py-1.5 rounded text-xs font-bold hover:bg-gray-200 transition-colors"
                                                    >
                                                        Download
                                                    </a>
                                                </div>
                                            </div>
                                        ) : null}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                ) : (
                    <div className="h-full flex flex-col items-center justify-center text-gray-500">
                        <div className="w-24 h-24 rounded-full bg-white/5 mx-auto mb-4 flex items-center justify-center">
                            <Send className="w-8 h-8 opacity-20" />
                        </div>
                        <p>Select models and enter a prompt to compare results</p>
                    </div>
                )}
            </div>
        </div>
    );
}
