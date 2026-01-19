import React from 'react';
import { RefreshCw, ShieldCheck, Activity, Box, Wrench } from 'lucide-react';
import { apiClient } from '../api/client';
import StatusPanel from './StatusPanel';
import DockerMonitor from './DockerMonitor';
import VerificationRunner from './VerificationRunner';
import { DockerContainerInfo, SystemFixResponse } from '../api/schemas';

interface SystemOperationsProps {
    readonly onViewLogs: (container: DockerContainerInfo) => void;
}

export function SystemOperations({ onViewLogs }: SystemOperationsProps) {
    return (
        <div className="bento-grid pb-20">
            {/* Row 1: Status & Recovery */}
            <div className="col-span-12 lg:col-span-8 glass-panel-prime rounded-2xl p-6 flex flex-col">
                <div className="flex items-center space-x-3 mb-6">
                    <Activity className="text-primary w-5 h-5" />
                    <h3 className="text-lg font-bold font-display tracking-wider text-white">SYSTEM STATUS</h3>
                </div>
                <div className="flex-1">
                    <StatusPanel />
                </div>
            </div>

            <div className="col-span-12 lg:col-span-4 space-y-6">
                <SystemRecovery />

                <div className="glass-panel-prime rounded-2xl p-6 relative overflow-hidden group">
                    {/* Decorative BG */}
                    <div className="absolute inset-0 bg-linear-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />

                    <div className="relative z-10">
                        <div className="flex items-center space-x-3 mb-4">
                            <ShieldCheck className="text-success w-5 h-5" />
                            <h3 className="text-lg font-bold font-display tracking-wider text-white">VERIFICATION</h3>
                        </div>
                        <VerificationRunner />
                    </div>
                </div>
            </div>

            {/* Row 2: Docker Monitor */}
            <div className="col-span-12 glass-panel-prime rounded-2xl p-6 min-h-[400px]">
                <div className="flex justify-between items-center mb-6">
                    <div className="flex items-center space-x-3">
                        <Box className="text-secondary w-5 h-5" />
                        <div>
                            <h3 className="text-lg font-bold font-display tracking-wider text-white">CONTAINER INFRASTRUCTURE</h3>
                            <p className="text-xs text-zinc-400 font-mono">Docker Socket: Connected</p>
                        </div>
                    </div>
                    <button
                        onClick={() => globalThis.location.reload()}
                        className="p-2 rounded-lg hover:bg-white/5 transition-colors text-primary border border-primary/20 hover:border-primary/50"
                        title="Refresh Status"
                    >
                        <RefreshCw className="w-4 h-4" />
                    </button>
                </div>
                <DockerMonitor onViewLogs={onViewLogs} />
            </div>
        </div>
    );
}

function SystemRecovery() {
    const [loading, setLoading] = React.useState(false);
    const [result, setResult] = React.useState<SystemFixResponse | null>(null);

    const runFix = async () => {
        setLoading(true);
        setResult(null);
        try {
            const data = await apiClient.runSystemFix();
            setResult(data);
        } catch (e) {
            setResult({ success: false, stderr: e instanceof Error ? e.message : String(e), stdout: '' });
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="glass-panel-prime rounded-2xl p-6 relative overflow-hidden hover:border-primary/30 transition-colors">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                    <Wrench className="text-warning w-5 h-5" />
                    <h3 className="text-lg font-bold font-display tracking-wider text-white">AUTO-RECOVERY</h3>
                </div>
            </div>

            <p className="text-xs text-zinc-400 mb-6 leading-relaxed">
                Initiate automated repair protocols to resolve container anomalies and system faults.
            </p>

            <button
                onClick={runFix}
                disabled={loading}
                className={`w-full flex items-center justify-center space-x-2 py-3 rounded-xl font-bold tracking-wide transition-all uppercase text-xs ${loading
                    ? 'bg-zinc-800 text-zinc-500 cursor-not-allowed'
                    : 'bg-primary/10 text-primary border border-primary/20 hover:bg-primary/20 hover:shadow-[0_0_15px_rgba(0,240,255,0.2)]'
                    }`}
            >
                {loading ? (
                    <>
                        <div className="w-4 h-4 border-2 border-primary/30 border-t-primary rounded-full animate-spin" />
                        <span>INITIALIZING...</span>
                    </>
                ) : (
                    <span>EXECUTE REPAIR</span>
                )}
            </button>

            {result && (
                <div className={`mt-4 p-3 rounded-lg border text-[10px] font-mono whitespace-pre-wrap ${result.success
                    ? 'bg-success/10 border-success/20 text-success'
                    : 'bg-error/10 border-error/20 text-error'
                    }`}>
                    {result.stdout || result.stderr || "Protocol executed."}
                </div>
            )}
        </div>
    );
}
