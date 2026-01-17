import { useState, useEffect, useRef } from 'react';
import { Play, Terminal, Cpu, Activity, AlertCircle, CheckCircle } from 'lucide-react';

export default function VerificationRunner() {
    const [running, setRunning] = useState(false);
    const [logs, setLogs] = useState([]);
    const [status, setStatus] = useState('idle'); // idle, running, success, failure
    const terminalEndRef = useRef(null);

    const runTest = async () => {
        if (running) return;

        setRunning(true);
        setLogs([]);
        setStatus('running');

        try {
            const response = await fetch('/api/verify/stream');
            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            while (true) {
                const { value, done } = await reader.read();
                if (done) break;

                const text = decoder.decode(value, { stream: true });
                setLogs(prev => [...prev, ...text.split('\n')]);

                // Simple heuristic to detect final status from logs if backend doesn't send explicit event
                // Ideally backend sends structured events, but raw stream is fine for now
                if (text.includes("[SUCCESS]")) setStatus('success');
                if (text.includes("[FAILURE]")) setStatus('failure');

                // Active alerts
                if (text.includes("429") || text.includes("RESOURCE_EXHAUSTED")) {
                    setLogs(prev => [...prev, "\n[ALERT] Quota Limit Reached! Retrying..."]);
                }
            }
        } catch (err) {
            console.error(err);
            setLogs(prev => [...prev, `\n[ERROR] Network failure: ${err.message}`]);
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
                        <div className="p-2 bg-indigo-500/10 rounded-lg text-indigo-400">
                            <Terminal size={20} />
                        </div>
                        <div>
                            <h2 className="font-semibold text-white">System Verification</h2>
                            <p className="text-xs text-zinc-400 font-mono">E2E_TEST_SUITE::CONTENT_ENGINE</p>
                        </div>
                    </div>

                    <button
                        onClick={runTest}
                        disabled={running}
                        className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium transition-all duration-200 border border-transparent ${running
                            ? 'bg-zinc-800 text-zinc-500 cursor-wait'
                            : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-lg shadow-indigo-500/20 border-indigo-500/50'
                            }`}
                    >
                        {running ? <Activity size={18} className="animate-spin" /> : <Play size={18} />}
                        <span>{running ? 'EXECUTING...' : 'INITIATE SEQUENCE'}</span>
                    </button>
                </div>

                <div className="p-6 bg-black/40 min-h-[400px] font-mono text-sm relative">
                    {status === 'idle' && logs.length === 0 && (
                        <div className="absolute inset-0 flex flex-col items-center justify-center text-zinc-600 space-y-4">
                            <Cpu size={48} strokeWidth={1} />
                            <p>AWAITING COMMAND INPUT</p>
                        </div>
                    )}

                    <div className="space-y-1">
                        {logs.map((line, i) => (
                            <div key={i} className={`break-words ${line.includes('ERROR') || line.includes('FAILURE') ? 'text-rose-400' : line.includes('SUCCESS') ? 'text-emerald-400' : 'text-zinc-300'}`}>
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
