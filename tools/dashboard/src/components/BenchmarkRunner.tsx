import { useState, useEffect, useRef } from 'react';
import { apiClient } from '../api/client';
import { Play, BarChart2, Cpu, Activity } from 'lucide-react';

export default function BenchmarkRunner() {
    const [running, setRunning] = useState(false);
    const [logs, setLogs] = useState<string[]>([]);
    const [status, setStatus] = useState<'idle' | 'running' | 'success' | 'failure'>('idle');
    const terminalEndRef = useRef<HTMLDivElement>(null);

    const runTest = async () => {
        if (running) return;

        setRunning(true);
        setLogs([]);
        setStatus('running');

        try {
            const response = await apiClient.runBenchmarkStream();
            if (!response.body) throw new Error("No response body");

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const text = decoder.decode(value, { stream: true });
                setLogs(prev => [...prev, ...text.split('\n')]);

                if (text.includes("[SUCCESS]")) setStatus('success');
                if (text.includes("[FAILURE]")) setStatus('failure');
            }
        } catch (err: unknown) {
            console.error(err);
            const msg = err instanceof Error ? err.message : String(err);
            setLogs(prev => [...prev, `\n[ERROR] Network failure: ${msg}`]);
            setStatus('failure');
        } finally {
            setRunning(false);
        }
    };

    useEffect(() => {
        terminalEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [logs]);

    return (
        <div className="space-y-6">
            <div className="glass-panel p-1 rounded-xl overflow-hidden">
                <div className="bg-zinc-900/50 p-4 border-b border-zinc-800 flex justify-between items-center">
                    <div className="flex items-center space-x-3">
                        <div className="p-2 bg-rose-500/10 rounded-lg text-rose-400">
                            <BarChart2 size={20} />
                        </div>
                        <div>
                            <h2 className="font-semibold text-white">Evaluations</h2>
                            <p className="text-xs text-zinc-400 font-mono">LATENCY & QUALITY TESTS</p>
                        </div>
                    </div>

                    <button
                        onClick={runTest}
                        disabled={running}
                        className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 border border-transparent ${running
                            ? 'bg-zinc-800 text-zinc-500 cursor-wait'
                            : 'bg-rose-600 hover:bg-rose-500 text-white shadow-lg shadow-rose-500/20 border-rose-500/50'
                            }`}
                    >
                        {running ? <Activity size={18} className="animate-spin" /> : <Play size={18} />}
                        <span>{running ? 'RUN EVALUATION' : 'START EVALUATION'}</span>
                    </button>
                </div>

                <div className="p-6 bg-black/40 min-h-[400px] font-mono text-sm relative">
                    {status === 'idle' && logs.length === 0 && (
                        <div className="absolute inset-0 flex flex-col items-center justify-center text-zinc-600 space-y-4 text-center p-8">
                            <Cpu size={48} strokeWidth={1} />
                            <p>READY TO RUN CONTENT ENGINE EVALUATIONS</p>
                            <p className="text-xs max-w-md text-zinc-500">
                                This process runs the full content generation pipeline (Research → Write → Image)
                                to verify system integrity and measure end-to-end latency.
                            </p>
                        </div>
                    )}

                    <div className="space-y-1">
                        {logs.map((line, i) => (
                            <div key={i} className={`break-words ${line.includes('ERROR') || line.includes('FAILURE') ? 'text-rose-400' : line.includes('Testing') ? 'text-blue-400' : line.includes('SUCCESS') ? 'text-emerald-400' : 'text-zinc-300'}`}>
                                {line}
                            </div>
                        ))}
                        <div ref={terminalEndRef} />
                    </div>
                </div>
            </div>
        </div>
    );
}
