import { useState, useEffect } from 'react';
import { Server, Shield, Activity, Box, Zap, MessageSquare } from 'lucide-react';
import LogViewer from './LogViewer';

export default function StatusPanel() {
    const [status, setStatus] = useState(null);
    const [loading, setLoading] = useState(true);
    const [selectedContainer, setSelectedContainer] = useState(null);

    useEffect(() => {
        fetch('/api/status')
            .then(res => res.json())
            .then(data => {
                setStatus(data);
                setLoading(false);
            })
            .catch(err => {
                console.error(err);
                setLoading(false);
            });
    }, []);

    // Helper to map UI label keys to actual container names for logs
    const getContainerName = (key) => {
        const map = {
            'orchestrator': 'course_creator-orchestrator',
            'content_builder': 'course_creator-content_builder',
            'image_generator': 'course_creator-image_generator',
            'customer_service': 'course_creator-customer_service',
            'status': 'course_creator-phoenix' // Mapping System Core to Phoenix/Telemetry for now
        };
        return map[key] || key;
    };

    const StatusCard = ({ label, value, icon, typeKey }) => {
        const Icon = icon;
        return (
            <div
                onClick={() => value !== 'unknown' && setSelectedContainer(getContainerName(typeKey))}
                className={`glass-card p-5 rounded-xl border-l-2 ${value === 'online' ? 'border-l-emerald-500' : 'border-l-zinc-700'} relative overflow-hidden group cursor-pointer transition-all hover:scale-[1.02] active:scale-[0.98]`}
            >
                <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                    <Icon size={48} />
                </div>
                <div className="relative z-10">
                    <div className="flex items-center space-x-2 mb-3">
                        <Icon size={16} className={value === 'online' ? 'text-emerald-400' : 'text-zinc-500'} />
                        <span className="text-xs font-mono text-zinc-400 uppercase tracking-widest">{label}</span>
                    </div>
                    <div className="flex items-baseline space-x-2">
                        <span className={`text-2xl font-bold ${value === 'online' ? 'text-white' : 'text-zinc-500'}`}>
                            {value === 'online' ? 'ACTIVE' : value.toUpperCase()}
                        </span>
                        {value === 'online' && (
                            <span className="flex h-2 w-2 relative">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                            </span>
                        )}
                    </div>
                    <div className="mt-2 opacity-0 group-hover:opacity-100 transition-opacity text-[10px] text-zinc-500 font-mono">
                        CLICK TO VIEW LOGS
                    </div>
                </div>
            </div>
        );
    };

    if (loading) return (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 animate-pulse">
            {[1, 2, 3, 4, 5].map(i => <div key={i} className="h-32 bg-zinc-900/50 rounded-xl"></div>)}
        </div>
    );

    if (!status) return <div className="p-4 bg-rose-900/20 text-rose-400 border border-rose-500/30 rounded-xl">System Unreachable</div>;

    return (
        <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
                <StatusCard label="System Core" value={status.status} icon={Shield} typeKey="status" />
                <StatusCard label="Orchestrator" value={status.orchestrator} icon={Server} typeKey="orchestrator" />
                <StatusCard label="Content Factory" value={status.content_builder} icon={Box} typeKey="content_builder" />
                <StatusCard label="Image Gen" value={status.image_generator} icon={Zap} typeKey="image_generator" />
                <StatusCard label="Customer Svc" value={status.customer_service || 'offline'} icon={MessageSquare} typeKey="customer_service" />
            </div>

            {selectedContainer && (
                <LogViewer
                    containerName={selectedContainer}
                    onClose={() => setSelectedContainer(null)}
                />
            )}
        </div>
    );
}
