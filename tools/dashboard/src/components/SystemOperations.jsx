import React from 'react';
import { RefreshCw } from 'lucide-react';
import StatusPanel from './StatusPanel';
import DockerMonitor from './DockerMonitor';
import VerificationRunner from './VerificationRunner';

export function SystemOperations() {
    return (
        <div className="space-y-8">
            <section>
                <div className="mb-6">
                    <h2 className="text-2xl font-bold text-white">System Status</h2>
                    <p className="text-gray-400">Real-time operational status of all agents and services.</p>
                </div>
                <StatusPanel />
            </section>

            <section>
                <div className="flex justify-between items-center mb-6">
                    <div>
                        <h2 className="text-2xl font-bold font-display text-transparent bg-clip-text bg-linear-to-r from-cyan-400 to-blue-500">
                            Container Infrastructure
                        </h2>
                        <p className="text-gray-400 font-mono text-sm">Docker container monitoring and logs.</p>
                    </div>
                    <div className="flex space-x-3">
                        <button
                            onClick={() => window.location.reload()}
                            className="p-2 rounded-lg hover:bg-white/5 transition-colors text-cyan-400 border border-cyan-500/30"
                            title="Refresh Status"
                        >
                            <RefreshCw className="w-5 h-5" />
                        </button>
                    </div>
                </div>
                <DockerMonitor />
            </section>

            <section>
                <div className="mb-6">
                    <h2 className="text-2xl font-bold text-white">System Verification</h2>
                    <p className="text-gray-400">Run system-wide integrity checks.</p>
                </div>
                <VerificationRunner />
            </section>

            <section>
                <div className="mb-6">
                    <h2 className="text-2xl font-bold text-white">System Recovery</h2>
                    <p className="text-gray-400">Auto-fix issues and repair the environment.</p>
                </div>
                <SystemRecovery />
            </section>
        </div>
    );
}

function SystemRecovery() {
    const [loading, setLoading] = React.useState(false);
    const [result, setResult] = React.useState(null);

    const runFix = async () => {
        setLoading(true);
        setResult(null);
        try {
            const res = await fetch('/api/system/fix', { method: 'POST' });
            const data = await res.json();
            setResult(data);
        } catch (e) {
            setResult({ success: false, stderr: e.message });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="glass-panel p-6 rounded-xl border border-white/5">
            <div className="flex items-start justify-between">
                <div>
                    <h3 className="text-lg font-semibold text-white mb-2">Auto-Heal System</h3>
                    <p className="text-sm text-gray-400 mb-4 max-w-xl">
                        Runs the <code className="text-indigo-300 bg-indigo-900/30 px-1 py-0.5 rounded">debug_system --fix</code> command
                        to automatically restart dead containers and resolve common infrastructure issues.
                    </p>
                </div>
                <button
                    onClick={runFix}
                    disabled={loading}
                    className={`flex items-center space-x-2 px-6 py-3 rounded-lg font-medium transition-all ${loading
                        ? 'bg-gray-700 text-gray-400 cursor-not-allowed'
                        : 'bg-linear-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white shadow-lg shadow-emerald-900/20'
                        }`}
                >
                    {loading ? (
                        <>
                            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            <span>Fixing...</span>
                        </>
                    ) : (
                        <span>🩹 Heal System</span>
                    )}
                </button>
            </div>

            {result && (
                <div className={`mt-4 p-4 rounded-lg border text-sm font-mono whitespace-pre-wrap ${result.success
                    ? 'bg-emerald-900/20 border-emerald-500/30 text-emerald-300'
                    : 'bg-red-900/20 border-red-500/30 text-red-300'
                    }`}>
                    {result.stdout || result.stderr || "Command executed."}
                </div>
            )}
        </div>
    );
}
