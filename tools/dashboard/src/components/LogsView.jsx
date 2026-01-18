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
    }, []);

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

    const fetchContainers = async () => {
        try {
            const response = await fetch('http://localhost:8010/api/docker');
            const data = await response.json();

            if (data.error) throw new Error(data.error);

            setContainers(data);
            if (!selectedContainer && data.length > 0) {
                // Default to orchestrator if available, else first
                const orchestrator = data.find(c => c.name.includes('orchestrator'));
                setSelectedContainer(orchestrator || data[0]);
            }
        } catch (err) {
            setError(err.message);
        }
    };

    const streamLogs = async (containerName) => {
        setLogs([]);
        setLoading(true);

        if (abortControllerRef.current) {
            abortControllerRef.current.abort();
        }

        const ac = new AbortController();
        abortControllerRef.current = ac;

        try {
            const response = await fetch(`http://localhost:8010/api/logs/${containerName}`, {
                signal: ac.signal
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            setLoading(false);

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const text = decoder.decode(value);
                setLogs(prev => [...prev, text]);
            }
        } catch (err) {
            if (err.name !== 'AbortError') {
                setLogs(prev => [...prev, `\n[Error reading logs: ${err.message}]\n`]);
            }
        }
    };

    return (
        <div className="space-y-6 h-[calc(100vh-8rem)] flex flex-col">
            <div className="flex justify-between items-center">
                <div>
                    <h2 className="text-2xl font-bold text-white">System Logs</h2>
                    <p className="text-gray-400">Real-time container log streaming.</p>
                </div>
                <button
                    onClick={fetchContainers}
                    className="p-2 glass-button rounded-lg hover:bg-white/10 transition-colors"
                >
                    <RefreshCw size={20} className="text-indigo-400" />
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
                <div className="w-64 glass-panel rounded-xl overflow-hidden flex flex-col">
                    <div className="p-4 border-b border-white/5 bg-white/5">
                        <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wider">Containers</h3>
                    </div>
                    <div className="overflow-y-auto flex-1 p-2 space-y-1">
                        {containers.map(container => (
                            <button
                                key={container.id}
                                onClick={() => setSelectedContainer(container)}
                                className={`w-full text-left px-3 py-3 rounded-lg flex items-center space-x-3 transition-colors ${selectedContainer?.id === container.id
                                    ? 'bg-indigo-600/20 border border-indigo-500/30 text-white'
                                    : 'text-gray-400 hover:bg-white/5 hover:text-gray-200 border border-transparent'
                                    }`}
                            >
                                <Box size={16} className={selectedContainer?.id === container.id ? 'text-indigo-400' : 'text-gray-500'} />
                                <span className="truncate text-sm font-medium">{container.name.replace('course_creator-', '')}</span>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Log Terminal */}
                <div className="flex-1 glass-panel rounded-xl overflow-hidden flex flex-col border border-white/10 bg-black/40">
                    <div className="p-3 bg-black/60 border-b border-white/10 flex items-center justify-between">
                        <div className="flex items-center space-x-2 text-sm text-gray-400">
                            <Terminal size={14} />
                            <span className="font-mono text-indigo-300">{selectedContainer?.name || 'Select a container'}</span>
                        </div>
                        {loading && <span className="text-xs text-indigo-400 animate-pulse">Connecting...</span>}
                    </div>
                    <div className="flex-1 overflow-y-auto p-4 font-mono text-xs md:text-sm text-gray-300 space-y-1 custom-scrollbar">
                        {logs.length === 0 && !loading && (
                            <div className="text-gray-600 italic">No logs received or container is silent.</div>
                        )}
                        {logs.map((chunk, i) => (
                            <span key={i} className="whitespace-pre-wrap wrap-break-word">{chunk}</span>
                        ))}
                        <div ref={logEndRef} />
                    </div>
                </div>
            </div>
        </div>
    );
}
