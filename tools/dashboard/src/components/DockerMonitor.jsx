import { useState, useEffect } from 'react';
import { Container, RefreshCw, Box, Server } from 'lucide-react';
import Card3D from './Card3D';

export default function DockerMonitor() {
    const [containers, setContainers] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchStats = () => {
        fetch('/api/docker')
            .then(res => res.json())
            .then(data => {
                if (Array.isArray(data)) setContainers(data);
                else console.error("Docker API error:", data);
                setLoading(false);
            })
            .catch(() => setLoading(false));
    };

    useEffect(() => {
        fetchStats();
        const interval = setInterval(fetchStats, 5000); // Live poll
        return () => clearInterval(interval);
    }, []);

    return (
        <div className="space-y-6">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                    <div className="p-2 bg-sky-500/10 rounded-lg text-sky-400">
                        <Container size={20} />
                    </div>
                    <div>
                        <h2 className="font-semibold text-white">Container Infrastructure</h2>
                        <p className="text-xs text-zinc-400 font-mono">DOCKER_ENGINE::LOCAL</p>
                    </div>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {containers.map(c => (
                    <Card3D key={c.id} className="h-full">
                        <div className="glass-card p-5 rounded-xl border-l-2 border-l-sky-500 h-full relative overflow-hidden group">
                            <div className="absolute top-0 right-0 p-4 opacity-5 text-sky-400">
                                <Box size={64} />
                            </div>

                            <div className="flex justify-between items-start mb-4 relative z-10">
                                <div>
                                    <h3 className="font-bold text-lg text-white font-mono">{c.name.replace('/', '')}</h3>
                                    <p className="text-xs text-sky-400 truncate max-w-[150px]">{c.image}</p>
                                </div>
                                <span className={`px-2 py-1 rounded text-xs font-bold uppercase tracking-wider ${c.status.startsWith('Up') ? 'bg-emerald-500/20 text-emerald-400' : 'bg-zinc-700 text-zinc-400'
                                    }`}>
                                    {c.status.split(' ')[0]}
                                </span>
                            </div>

                            <div className="space-y-2 relative z-10">
                                <div className="flex justify-between text-sm border-t border-zinc-700/50 pt-2">
                                    <span className="text-zinc-500">CONTAINER ID</span>
                                    <span className="font-mono text-zinc-300">{c.id}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-zinc-500">RUNTIME</span>
                                    <span className="font-mono text-zinc-300">Docker</span>
                                </div>
                            </div>
                        </div>
                    </Card3D>
                ))}

                {containers.length === 0 && !loading && (
                    <div className="col-span-full p-8 text-center text-zinc-500 border border-zinc-800 border-dashed rounded-xl">
                        No active containers detected.
                    </div>
                )}
            </div>
        </div>
    );
}
