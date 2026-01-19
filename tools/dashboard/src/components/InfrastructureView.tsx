import React, { useState } from 'react';
import { Terminal, Activity, BarChart3 } from 'lucide-react';
import { SystemOperations } from './SystemOperations';
import { LogsView } from './LogsView';
import BenchmarkRunner from './BenchmarkRunner';
import { DockerContainerInfo } from '../api/schemas';

export function InfrastructureView() {
    const [activeTab, setActiveTab] = useState('overview');
    const [selectedLogContainer, setSelectedLogContainer] = useState<DockerContainerInfo | null>(null);

    const handleViewLogs = (container: DockerContainerInfo) => {
        setSelectedLogContainer(container);
        setActiveTab('logs');
    };

    return (
        <div className="space-y-8 animate-in fade-in duration-700">
            {/* Command Header */}
            <header className="flex flex-col md:flex-row justify-between items-end md:items-center gap-4">
                <div>
                    <h2 className="text-3xl font-bold tracking-tight text-white font-display">
                        INFRASTRUCTURE
                    </h2>
                    <p className="text-zinc-400 font-mono text-sm mt-1 tracking-wide">
                        <span className="text-primary">///</span> SYSTEM MONITORING & CONTROL
                    </p>
                </div>

                {/* Segmented Control Tabs */}
                <div className="flex bg-white/5 p-1.5 rounded-xl border border-white/5 backdrop-blur-md">
                    <TabButton
                        active={activeTab === 'overview'}
                        onClick={() => setActiveTab('overview')}
                        icon={<Activity size={16} />}
                        label="Overview"
                    />
                    <TabButton
                        active={activeTab === 'logs'}
                        onClick={() => setActiveTab('logs')}
                        icon={<Terminal size={16} />}
                        label="Live Logs"
                    />
                    <TabButton
                        active={activeTab === 'benchmarks'}
                        onClick={() => setActiveTab('benchmarks')}
                        icon={<BarChart3 size={16} />}
                        label="Evaluations"
                    />
                </div>
            </header>

            {/* Viewport content */}
            <div className="min-h-[600px] relative">
                {activeTab === 'overview' && (
                    <div className="animate-in zoom-in-95 fade-in duration-300">
                        <SystemOperations onViewLogs={handleViewLogs} />
                    </div>
                )}
                {activeTab === 'logs' && (
                    <div className="animate-in zoom-in-95 fade-in duration-300">
                        <LogsView initialContainer={selectedLogContainer || undefined} />
                    </div>
                )}
                {activeTab === 'benchmarks' && (
                    <div className="animate-in zoom-in-95 fade-in duration-300">
                        <BenchmarkRunner />
                    </div>
                )}
            </div>
        </div>
    );
}

interface TabButtonProps {
    active: boolean;
    onClick: () => void;
    icon: React.ReactElement<{ className?: string }>;
    label: string;
}

function TabButton({ active, onClick, icon, label }: TabButtonProps) {
    return (
        <button
            onClick={onClick}
            className={`flex items-center space-x-2 px-5 py-2.5 rounded-lg text-sm font-medium transition-all duration-300 ${active
                ? 'bg-primary/20 text-primary shadow-[0_0_15px_rgba(0,240,255,0.15)] ring-1 ring-primary/30'
                : 'text-zinc-500 hover:text-white hover:bg-white/5'
                }`}
        >
            {React.cloneElement(icon, { className: active ? "animate-pulse-glow" : "" })}
            <span>{label}</span>
        </button>
    );
}
