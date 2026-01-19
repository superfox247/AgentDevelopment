import { useState, useEffect, useRef } from 'react';
import { apiClient } from '../api/client';
import { X, Terminal, Pause, Play } from 'lucide-react';

interface LogViewerProps {
    readonly containerName: string;
    readonly onClose: () => void;
}

export default function LogViewer({ containerName, onClose }: LogViewerProps) {
    const [logs, setLogs] = useState<string[]>([]);
    const [isPaused, setIsPaused] = useState(false);
    const endRef = useRef<HTMLDivElement>(null);
    const abortControllerRef = useRef<AbortController | null>(null);

    useEffect(() => {
        const onKeyDown = (e: KeyboardEvent) => {
            if (e.key === 'Escape') onClose();
        };
        window.addEventListener('keydown', onKeyDown);
        return () => window.removeEventListener('keydown', onKeyDown);
    }, [onClose]);

    useEffect(() => {
        setLogs([]);
        abortControllerRef.current = new AbortController();
        if (!abortControllerRef.current) return; // Should not happen but strict check

        const fetchLogs = async () => {
            try {
                if (!abortControllerRef.current) throw new Error("AbortController not successfully initialized");
                const response = await apiClient.getContainerLogsStream(containerName, abortControllerRef.current.signal);
                if (!response.body) throw new Error("No response body");

                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                while (true) {
                    const { value, done } = await reader.read();
                    if (done) break;

                    const text = decoder.decode(value, { stream: true });
                    // Docker logs might come in chunks, split by newlines
                    // Some basic cleanup of raw bytes if needed
                    const lines = text.split('\n');

                    setLogs(prev => {
                        const newLogs = [...prev, ...lines].slice(-1000); // Keep last 1000 lines
                        return newLogs;
                    });
                }
            } catch (err: unknown) {
                if (err instanceof Error && err.name !== 'AbortError') {
                    console.error("Log stream error:", err);
                    setLogs(prev => [...prev, `\n[ERROR] Stream disconnected: ${err.message}`]);
                }
            }
        };

        fetchLogs();

        return () => {
            if (abortControllerRef.current) {
                abortControllerRef.current.abort();
            }
        };
    }, [containerName]);

    useEffect(() => {
        if (!isPaused) {
            endRef.current?.scrollIntoView({ behavior: 'smooth' });
        }
    }, [logs, isPaused]);

    return (
        <div
            className="fixed inset-0 bg-black/90 backdrop-blur-md z-50 flex items-center justify-center p-4 animate-in fade-in duration-200"
            onClick={onClose}
        >
            <div
                className="glass-panel w-full max-w-5xl h-[85vh] flex flex-col rounded-xl overflow-hidden shadow-2xl border border-zinc-700 relative"
                onClick={e => e.stopPropagation()}
            >
                {/* Header */}
                <div className="bg-zinc-900 px-4 py-3 border-b border-zinc-800 flex justify-between items-center shrink-0">
                    <div className="flex items-center space-x-3">
                        <Terminal size={18} className="text-zinc-400" />
                        <div>
                            <h3 className="text-white font-mono font-bold text-sm tracking-wide">{containerName}</h3>
                            <div className="flex items-center space-x-2">
                                <span className={`w-2 h-2 rounded-full ${isPaused ? 'bg-amber-500' : 'bg-emerald-500 animate-pulse'}`}></span>
                                <span className="text-xs text-zinc-400 font-mono">LIVE LOG STREAM</span>
                            </div>
                        </div>
                    </div>
                    <div className="flex items-center space-x-3">
                        <button
                            onClick={() => setIsPaused(!isPaused)}
                            className={`flex items-center space-x-2 px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider transition-colors ${isPaused ? 'bg-amber-500/20 text-amber-500' : 'bg-zinc-800 text-zinc-400 hover:text-white'
                                }`}
                        >
                            {isPaused ? <><Pause size={12} /><span>Paused</span></> : <><Play size={12} /><span>Auto-Scroll</span></>}
                        </button>
                        <button
                            onClick={onClose}
                            className="p-2 bg-red-500/20 hover:bg-red-500 text-red-500 hover:text-white rounded-lg transition-all duration-200"
                            title="Close Logs"
                        >
                            <X size={20} />
                        </button>
                    </div>
                </div>

                {/* Log Content */}
                <div className="flex-1 bg-black/95 p-4 overflow-y-auto font-mono text-xs md:text-sm text-zinc-300 space-y-1 custom-scrollbar">
                    {logs.map((log, i) => (
                        <div key={i} className="whitespace-pre-wrap break-words border-l-2 border-transparent hover:border-zinc-700 hover:bg-white/5 pl-2 py-0.5 animate-in fade-in duration-0">
                            {log}
                        </div>
                    ))}
                    {logs.length === 0 && (
                        <div className="h-full flex flex-col items-center justify-center text-zinc-600 space-y-4">
                            <Terminal size={48} className="opacity-20" />
                            <div className="flex items-center space-x-2">
                                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
                                <span className="text-sm">Connecting to stream...</span>
                            </div>
                        </div>
                    )}
                    <div ref={endRef} />
                </div>
            </div>
        </div>
    );
}
