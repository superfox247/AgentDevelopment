import { useState, useEffect, useRef } from 'react';
import { X, Terminal, Download, Pause, Play } from 'lucide-react';

export default function LogViewer({ containerName, onClose }) {
    const [logs, setLogs] = useState([]);
    const [isPaused, setIsPaused] = useState(false);
    const endRef = useRef(null);
    const abortControllerRef = useRef(null);

    useEffect(() => {
        setLogs([]);
        abortControllerRef.current = new AbortController();

        const fetchLogs = async () => {
            try {
                const response = await fetch(`/api/logs/${containerName}`, {
                    signal: abortControllerRef.current.signal
                });

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
            } catch (err) {
                if (err.name !== 'AbortError') {
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
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <div className="glass-panel w-full max-w-5xl h-[80vh] flex flex-col rounded-xl overflow-hidden shadow-2xl border border-zinc-700">
                {/* Header */}
                <div className="bg-zinc-900 px-4 py-3 border-b border-zinc-800 flex justify-between items-center">
                    <div className="flex items-center space-x-3">
                        <Terminal size={18} className="text-zinc-400" />
                        <div>
                            <h3 className="text-white font-mono font-bold text-sm">{containerName}</h3>
                            <div className="flex items-center space-x-2">
                                <span className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"></span>
                                <span className="text-xs text-zinc-400">LIVE LOG STREAM</span>
                            </div>
                        </div>
                    </div>
                    <div className="flex items-center space-x-2">
                        <button
                            onClick={() => setIsPaused(!isPaused)}
                            className="p-2 hover:bg-zinc-800 rounded-lg text-zinc-400 hover:text-white transition-colors"
                            title={isPaused ? "Resume Auto-scroll" : "Pause Auto-scroll"}
                        >
                            {isPaused ? <Play size={18} /> : <Pause size={18} />}
                        </button>
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-red-900/50 rounded-lg text-zinc-400 hover:text-red-400 transition-colors"
                        >
                            <X size={18} />
                        </button>
                    </div>
                </div>

                {/* Log Content */}
                <div className="flex-1 bg-black p-4 overflow-y-auto font-mono text-xs md:text-sm text-zinc-300 space-y-0.5">
                    {logs.map((log, i) => (
                        <div key={i} className="whitespace-pre-wrap break-words border-l-2 border-transparent hover:border-zinc-700 hover:bg-zinc-900/30 pl-2">
                            {log}
                        </div>
                    ))}
                    {logs.length === 0 && (
                        <div className="text-zinc-600 italic">Connected to stream. Waiting for output...</div>
                    )}
                    <div ref={endRef} />
                </div>
            </div>
        </div>
    );
}
