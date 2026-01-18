import React, { useState, useEffect, useRef } from 'react';
import { Terminal, RefreshCw, Box, AlertCircle } from 'lucide-react';

export function LogsView() {
    const [containers, setContainers] = useState([]);
    const [selectedContainer, setSelectedContainer] = useState(null);
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const logEndRef = useRef(null);
    const abortControllerRef = useRef(null);

    useEffect(() => {
        fetchContainers();
    }, [fetchContainers]);

    useEffect(() => {
        if (selectedContainer) {
            streamLogs(selectedContainer.name);
        }
        return () => {
            // Cleanup previous stream
            if (abortControllerRef.current) {
                abortControllerRef.current.abort();
            }
        };
    }, [selectedContainer]);

    useEffect(() => {
        // Auto-scroll to bottom
        logEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [logs]);

    const fetchContainers = React.useCallback(async () => {
        try {
            const response = await fetch('/api/docker');
            const data = await response.json();

            if (data.error) throw new Error(data.error);

            // Ensure data is an array before setting state
            const containerList = Array.isArray(data) ? data : [];
            setContainers(containerList);

            if (!selectedContainer && containerList.length > 0) {
                // Default to orchestrator if available, else first
                const orchestrator = containerList.find(c => c.name.includes('orchestrator'));
                setSelectedContainer(orchestrator || containerList[0]);
            }
        } catch (err) {
            setError(err.message);
        }
    }, [selectedContainer]);

    const streamLogs = async (containerName) => {
        setLogs([]);
        setLoading(true);

        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
        }

        const ac = new AbortController();
        abortControllerRef.current = ac;

        try {
            const response = await fetch(`/api/logs/${containerName}`, {
                signal: ac.signal
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            setLoading(false);

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const text = decoder.decode(value);
                setLogs(prev => [...prev, { id: crypto.randomUUID(), text }]);
            }
        } catch (err) {
            if (err.name !== 'AbortError') {
                setLogs(prev => [...prev, { id: crypto.randomUUID(), text: `\n[Error reading logs: ${err.message}]\n` }]);
            }
        }
    };

    return (
        <div className="space-y-6 h-[calc(100vh-6rem)] flex flex-col">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-linear-to-r from-cyan-400 to-indigo-500 font-display">System Logs</h2>
                    <p className="text-cyan-400/60 font-mono text-sm">Real-time container log streaming protocol.</p>
                </div>
                <button
                    onClick={fetchContainers}
                    className="p-2 glass-button rounded-lg hover:bg-cyan-400/10 text-cyan-400 border border-cyan-500/30 transition-all hover:shadow-[0_0_10px_rgba(34,211,238,0.2)]"
                >
                    <RefreshCw size={20} />
                </button>
            </div>

            {error && (
                <div className="bg-red-500/10 border border-red-500/20 text-red-200 p-4 rounded-lg flex items-center space-x-3">
                    <AlertCircle size={20} />
                    <span>{error}</span>
                </div>
            )}

            <div className="flex-1 flex gap-6 min-h-0">
                {/* Container List */}
                <div className="w-64 glass-panel rounded-xl overflow-hidden flex flex-col border border-cyan-500/20">
                    <div className="p-4 border-b border-cyan-500/20 bg-cyan-950/20">
                        <h3 className="text-xs font-bold text-cyan-500/70 uppercase tracking-[0.2em] font-display">Containers</h3>
                    </div>
                    <div className="overflow-y-auto flex-1 p-2 space-y-1">
                        {containers.map(container => (
                            <button
                                key={container.id}
                                onClick={() => setSelectedContainer(container)}
                                className={`w-full text-left px-3 py-3 rounded-lg flex items-center space-x-3 transition-colors ${selectedContainer?.id === container.id
                                    ? 'bg-cyan-500/20 border border-cyan-500/40 text-cyan-100 shadow-[0_0_10px_rgba(6,182,212,0.1)]'
                                    : 'text-gray-400 hover:bg-cyan-950/30 hover:text-cyan-200 border border-transparent'
                                    }`}
                            >
                                <Box size={16} className={selectedContainer?.id === container.id ? 'text-cyan-400' : 'text-zinc-600'} />
                                <span className="truncate text-sm font-medium font-mono">{container.name.replace('course_creator-', '')}</span>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Log Terminal */}
                <div className="flex-1 glass-panel rounded-xl overflow-hidden flex flex-col border border-cyan-500/10">
                    <div className="p-3 bg-black/40 border-b border-cyan-500/10 flex items-center justify-between">
                        <div className="flex items-center space-x-2 text-sm text-zinc-400">
                            <Terminal size={14} className="text-cyan-500/50" />
                            <span className="font-mono text-cyan-300">{selectedContainer?.name || 'Select a container'}</span>
                        </div>
                        {loading && (
                            <div className="flex items-center space-x-2">
                                <span className="w-2 h-2 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_5px_#22d3ee]"></span>
                                <span className="text-xs text-cyan-400/70 font-mono">Receiving stream...</span>
                            </div>
                        )}
                    </div>
                    <div className="flex-1 overflow-y-auto p-4 font-mono text-xs md:text-sm text-zinc-300 space-y-0.5 custom-scrollbar bg-black/40">
                        {logs.length === 0 && !loading && (
                            <div className="text-zinc-600 italic font-mono">No logs received or container is silent.</div>
                        )}
                        {logs.map((chunk) => (
                            <span key={chunk.id} className="whitespace-pre-wrap wrap-break-word">{chunk.text}</span>
                        ))}
                        <div ref={logEndRef} />
                    </div>
                </div>
            </div>
        </div>
    );
}
