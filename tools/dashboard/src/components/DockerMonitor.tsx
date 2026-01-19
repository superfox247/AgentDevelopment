import { useState, useEffect } from 'react';
import { Box, ChevronDown, ChevronUp, Terminal, Play, Square, RotateCw } from 'lucide-react';
import Card3D from './Card3D';
import { apiClient } from '../api/client';

import { DockerContainerInfo } from '../api/schemas';

interface DockerMonitorProps {
    onViewLogs?: (container: DockerContainerInfo) => void;
}

export default function DockerMonitor({ onViewLogs }: DockerMonitorProps) {
    const [containers, setContainers] = useState<DockerContainerInfo[]>([]);
    const [loading, setLoading] = useState(true);
    const [expandedId, setExpandedId] = useState<string | null>(null);
    const [containerLogs, setContainerLogs] = useState<Record<string, string>>({}); // { id: logs }
    const [logLoading, setLogLoading] = useState(false);

    const fetchStats = () => {
        apiClient.getDockerStats()
            .then(data => {
                // apiClient unwraps response.data.data if present,
                // but our backend logic (server.py) sends { containers: [...] } inside that wrapper (if standard) or directly.
                // server.py: return DockerStatsResponse(containers=...) -> JSON { containers: [...] }
                // So apiClient returns { containers: [...] }
                if (data.containers && Array.isArray(data.containers)) {
                    setContainers(data.containers);
                } else if (Array.isArray(data)) {
                    setContainers(data);
                } else {
                    console.error("Docker API error:", data);
                }
                setLoading(false);
            })
            .catch(() => setLoading(false));
    };

    useEffect(() => {
        fetchStats();
        const interval = setInterval(fetchStats, 5000); // Live poll
        return () => clearInterval(interval);
    }, []);

    // Fetch logs when expanded
    useEffect(() => {
        if (expandedId) {
            const container = containers.find(c => c.id === expandedId);
            if (container) {
                // setLogLoading(true); // Moved to onClick
                apiClient.getContainerLogs(container.id, 50)
                    .then(data => {
                        setContainerLogs(prev => ({ ...prev, [expandedId]: data.logs || "" }));
                        setLogLoading(false);
                    })
                    .catch(err => {
                        console.error("Failed to fetch logs", err);
                        setLogLoading(false);
                    });
            }
        }
    }, [expandedId, containers]);

    const handleControl = async (e: React.MouseEvent, id: string, action: 'start' | 'stop' | 'restart') => {
        e.stopPropagation();
        try {
            await apiClient.controlContainer(id, action);
            fetchStats(); // Force refresh
        } catch (err) {
            console.error(`Failed to ${action} container`, err);
            alert(`Failed to ${action} container`);
        }
    };

    // Helper to determine status color based on logs + state
    const getStatusColor = (c: DockerContainerInfo) => {
        const isUp = c.status.startsWith('Up');
        const logs = containerLogs[c.id] || "";
        const hasError = logs.includes("ERROR") || logs.includes("CRITICAL");
        const hasWarn = logs.includes("WARNING");

        if (!isUp) return 'text-zinc-500 bg-zinc-500/10 border-zinc-500/20';
        if (hasError) return 'text-rose-400 bg-rose-500/10 border-rose-500/20';
        if (hasWarn) return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
        return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
    };

    // Filter logs for display (Warning/Error only or last few)
    const getFilteredLogs = (logs: string) => {
        if (!logs) return [];
        const lines = logs.split('\n').filter(l => l.trim());
        const interest = lines.filter(l => l.includes('WARNING') || l.includes('ERROR') || l.includes('CRITICAL'));
        return interest.length > 0 ? interest.slice(-5) : lines.slice(-5);
    };

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {containers.map(c => {
                    const isUp = c.status.startsWith('Up');
                    const isExpanded = expandedId === c.id;
                    const statusStyle = getStatusColor(c);
                    const logs = containerLogs[c.id] || "";
                    const filteredLogs = getFilteredLogs(logs);

                    return (
                        <Card3D key={c.id} className="h-full">
                            <div
                                onClick={(e) => {
                                    e.stopPropagation();
                                    if (c.id !== expandedId) {
                                        setLogLoading(true);
                                        setExpandedId(c.id);
                                    } else {
                                        setExpandedId(null);
                                    }
                                }}
                                className={`glass-card p-5 rounded-xl border-l-4 h-full relative overflow-hidden group cursor-pointer transition-all duration-300 hover:shadow-lg ${isUp ? 'border-emerald-500/50 shadow-emerald-500/10' : 'border-zinc-500/50'}`}
                            >
                                <div className="absolute top-0 right-0 p-4 opacity-5 text-white">
                                    <Box size={64} />
                                </div>

                                <div className="relative z-10">
                                    <div className="flex justify-between items-start mb-2">
                                        <div>
                                            <h3 className="font-bold text-lg text-white font-mono">{c.name.replace('/', '')}</h3>
                                            <p className="text-xs text-sky-400 truncate max-w-[150px]">{c.image}</p>
                                        </div>
                                        <div className={`px-2 py-1 rounded text-xs font-bold uppercase tracking-wider flex items-center gap-2 border ${statusStyle}`}>
                                            {isUp && <div className={`w-2 h-2 rounded-full animate-pulse ${statusStyle.split(' ')[0].replace('text-', 'bg-')}`} />}
                                            {c.status.split(' ')[0]}
                                        </div>
                                    </div>

                                    <div className={`transition-all duration-500 overflow-hidden ${isExpanded ? 'max-h-96 opacity-100 mt-4' : 'max-h-0 opacity-0'}`}>
                                        <div className="space-y-4 border-t border-white/5 pt-4">

                                            {/* Controls */}
                                            <div className="flex space-x-2">
                                                {isUp ? (
                                                    <button onClick={(e) => handleControl(e, c.id, 'stop')} className="flex-1 bg-rose-500/20 hover:bg-rose-500/30 text-rose-400 py-2 rounded flex items-center justify-center space-x-2 transition-colors">
                                                        <Square size={14} fill="currentColor" />
                                                        <span className="text-xs font-bold">STOP</span>
                                                    </button>
                                                ) : (
                                                    <button onClick={(e) => handleControl(e, c.id, 'start')} className="flex-1 bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-400 py-2 rounded flex items-center justify-center space-x-2 transition-colors">
                                                        <Play size={14} fill="currentColor" />
                                                        <span className="text-xs font-bold">START</span>
                                                    </button>
                                                )}
                                                <button onClick={(e) => handleControl(e, c.id, 'restart')} className="flex-1 bg-sky-500/20 hover:bg-sky-500/30 text-sky-400 py-2 rounded flex items-center justify-center space-x-2 transition-colors">
                                                    <RotateCw size={14} />
                                                    <span className="text-xs font-bold">RESTART</span>
                                                </button>
                                            </div>

                                            {/* Recent Logs Snippet */}
                                            <div className="bg-black/40 rounded p-3 font-mono text-[10px] text-zinc-400 min-h-[60px]">
                                                <div className="flex justify-between items-center mb-2 border-b border-white/5 pb-1">
                                                    <span className="font-bold text-zinc-500">RECENT LOGS</span>
                                                    <button
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            if (onViewLogs) onViewLogs(c);
                                                        }}
                                                        className="flex items-center space-x-1 text-sky-400 hover:text-sky-300"
                                                    >
                                                        <Terminal size={10} />
                                                        <span>FULL LOGS</span>
                                                    </button>
                                                </div>
                                                {logLoading ? (
                                                    <div className="animate-pulse">Loading logs...</div>
                                                ) : (
                                                    filteredLogs.length > 0 ? (
                                                        filteredLogs.map((l, i) => (
                                                            <div key={i} className={`truncate ${l.includes('ERROR') ? 'text-rose-400' : l.includes('WARNING') ? 'text-amber-400' : ''}`}>
                                                                {l}
                                                            </div>
                                                        ))
                                                    ) : (
                                                        <div className="text-zinc-600 italic">No recent warnings or errors.</div>
                                                    )
                                                )}
                                            </div>

                                        </div>
                                    </div>

                                    {/* Expand Toggle Icon */}
                                    <div className="flex justify-center mt-2 group-hover:translate-y-1 transition-transform">
                                        {isExpanded ? <ChevronUp size={16} className="text-white/20" /> : <ChevronDown size={16} className="text-white/20" />}
                                    </div>
                                </div>
                            </div>
                        </Card3D>
                    );
                })}

                {containers.length === 0 && !loading && (
                    <div className="col-span-full p-8 text-center text-zinc-500 border border-zinc-800 border-dashed rounded-xl">
                        No active containers detected.
                    </div>
                )}
            </div>
        </div>
    );
}
