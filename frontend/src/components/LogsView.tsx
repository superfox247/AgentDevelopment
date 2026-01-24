import { useState, useEffect, useRef } from 'react';
import { Terminal, RefreshCw, Box, AlertCircle, Pause, Play } from 'lucide-react';
import { ErrorBoundary } from './ErrorBoundary';
import { apiClient } from '../api/client';

import { DockerContainerInfo } from '../api/schemas';

interface LogsViewProps {
    initialContainer?: DockerContainerInfo;
}

export function LogsView({ initialContainer }: LogsViewProps) {
    return (
        <ErrorBoundary>
            <LogsViewContent initialContainer={initialContainer} />
        </ErrorBoundary>
    );
}

function LogsViewContent({ initialContainer }: LogsViewProps) {
    const [containers, setContainers] = useState<DockerContainerInfo[]>([]);
    const [selectedContainer, setSelectedContainer] = useState<DockerContainerInfo | null>(null);
    const [error, setError] = useState(null);

    // Initial load
    useEffect(() => {
        apiClient.getDockerStats()
            .then(data => {
                const list = data.containers;
                setContainers(list);

                if (initialContainer) {
                    const found = list.find(c => c.id === initialContainer.id);
                    setSelectedContainer(found || initialContainer);
                } else if (list.length > 0) {
                    // Default to orchestrator
                    const orchestrator = list.find(c => c.name.includes('orchestrator'));
                    setSelectedContainer(orchestrator || list[0]);
                }
            })
            .catch(err => setError(err.message));
    }, [initialContainer]);

    return (
        <div className="space-y-6 h-[calc(100vh-6rem)] flex flex-col">
            <header className="flex justify-between items-center shrink-0">
                <div>
                    <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-linear-to-r from-cyan-400 to-indigo-500 font-display">System Logs</h2>
                    <p className="text-cyan-400/60 font-mono text-sm">Real-time container log streaming protocol</p>
                </div>
            </header>

            {error && (
                <div className="bg-red-500/10 border border-red-500/20 text-red-200 p-4 rounded-lg flex items-center space-x-3 shrink-0">
                    <AlertCircle size={20} />
                    <span>{error}</span>
                </div>
            )}

            <div className="flex-1 flex gap-6 min-h-0">
                {/* Sidebar */}
                <div className="w-64 glass-panel rounded-xl overflow-hidden flex flex-col border border-cyan-500/20 shrink-0">
                    <div className="p-3 border-b border-cyan-500/20 bg-cyan-950/20">
                        <h3 className="text-xs font-bold text-cyan-500/70 uppercase tracking-widest">Containers</h3>
                    </div>
                    <div className="overflow-y-auto flex-1 p-2 space-y-1 custom-scrollbar">
                        {containers.map(c => (
                            <button
                                key={c.id}
                                onClick={() => setSelectedContainer(c)}
                                className={`w-full text-left px-3 py-2 rounded-lg flex items-center space-x-3 transition-all text-sm font-mono ${selectedContainer?.id === c.id
                                    ? 'bg-cyan-500/20 text-cyan-100 border border-cyan-500/30'
                                    : 'text-zinc-500 hover:text-zinc-300 hover:bg-white/5 border border-transparent'
                                    }`}
                            >
                                <Box size={14} className={selectedContainer?.id === c.id ? 'text-cyan-400' : 'opacity-50'} />
                                <span className="truncate">{c.name.replace('content_creation-', '')}</span>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Main Log Area */}
                <div className="flex-1 glass-panel rounded-xl border border-cyan-500/10 flex flex-col min-w-0 overflow-hidden bg-black/40">
                    {selectedContainer ? (
                        <LogStreamer key={selectedContainer.id} container={selectedContainer} />
                    ) : (
                        <div className="flex-1 flex items-center justify-center text-zinc-500 font-mono">
                            Select a container to view logs
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

interface LogStreamerProps {
    container: DockerContainerInfo;
}

interface LogEntry {
    id: string;
    text: string;
    type: 'system' | 'stdout';
}

function LogStreamer({ container }: LogStreamerProps) {
    const [logs, setLogs] = useState<LogEntry[]>([]);
    const [status, setStatus] = useState('connecting'); // connecting, connected, error, paused
    const [autoScroll, setAutoScroll] = useState(true);
    const scrollRef = useRef<HTMLDivElement>(null);
    const eventSourceRef = useRef<EventSource | null>(null);

    // Filter duplicates helper if needed (UUIDs)

    useEffect(() => {

        const url = `/api/logs/${container.name}/stream`;
        const es = new EventSource(url);
        eventSourceRef.current = es;

        es.onopen = () => {
            setStatus('connected');
            // Add a system message
            setLogs(prev => [...prev, { id: 'sys-start', text: `[SYSTEM] Connected to stream: ${container.name}`, type: 'system' }]);
        };

        es.onmessage = (event) => {
            try {
                const payload = JSON.parse(event.data);
                if (payload.text) {
                    setLogs(prev => {
                        // Keep buffer size reasonable (e.g. 2000 lines)
                        const rawType = payload.type;
                        const logType: 'system' | 'stdout' = (rawType === 'system' || rawType === 'stdout') ? rawType : 'stdout';
                        const newState = [...prev, { id: crypto.randomUUID(), text: payload.text, type: logType }];
                        if (newState.length > 2000) return newState.slice(-2000);
                        return newState;
                    });
                }
            } catch (e) {
                console.error("Failed to parse log", e);
            }
        };

        es.onerror = (err) => {
            console.error("SSE Error", err);
            setStatus('error');
            es.close();
        };

        return () => {
            es.close();
        };
    }, [container.name]);

    // Auto-scroll logic
    useEffect(() => {
        if (autoScroll && scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs, autoScroll]);

    const handleScroll = (e: React.UIEvent<HTMLDivElement>) => {
        const { scrollTop, scrollHeight, clientHeight } = e.currentTarget; // Typed correctly
        const isAtBottom = scrollHeight - scrollTop - clientHeight < 100;
        if (!isAtBottom && autoScroll) setAutoScroll(false);
        if (isAtBottom && !autoScroll) setAutoScroll(true);
    };

    return (
        <>
            {/* Toolbar */}
            <div className="h-10 border-b border-cyan-500/10 flex items-center justify-between px-4 bg-white/5">
                <div className="flex items-center space-x-2 text-xs font-mono text-zinc-400">
                    <Terminal size={12} />
                    <span>{container.name}</span>
                    <span className={`w-2 h-2 rounded-full ${status === 'connected' ? 'bg-emerald-500 animate-pulse' :
                        status === 'error' ? 'bg-red-500' : 'bg-yellow-500'
                        }`} />
                    <span className="uppercase opacity-50">{status}</span>
                </div>

                <div className="flex items-center space-x-2">
                    <button
                        onClick={() => setAutoScroll(!autoScroll)}
                        className={`p-1 rounded hover:bg-white/10 ${autoScroll ? 'text-cyan-400' : 'text-zinc-500'}`}
                        title={autoScroll ? "Auto-scroll ON" : "Auto-scroll OFF"}
                    >
                        {autoScroll ? <Pause size={14} /> : <Play size={14} />}
                    </button>
                    <button
                        onClick={() => setLogs([])}
                        className="p-1 rounded hover:bg-white/10 text-zinc-500 hover:text-white"
                        title="Clear Buffer"
                    >
                        <RefreshCw size={14} />
                    </button>
                </div>
            </div>

            {/* Scroll Area */}
            <div
                className="flex-1 overflow-y-auto p-4 font-mono text-xs leading-relaxed space-y-0.5 custom-scrollbar"
                ref={scrollRef}
                onScroll={handleScroll}
            >
                {logs.length === 0 && status === 'connected' && (
                    <div className="text-zinc-600 italic">Waiting for logs...</div>
                )}

                {logs.map((log) => (
                    <div key={log.id} className={`${log.type === 'system' ? 'text-cyan-400 italic opacity-70 my-2 padding-y-2 border-y border-cyan-500/10' :
                        'text-zinc-300 break-words whitespace-pre-wrap'
                        }`}>
                        {log.text}
                    </div>
                ))}
            </div>
        </>
    );
}
