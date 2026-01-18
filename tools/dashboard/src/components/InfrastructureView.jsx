import React, { useState } from 'react';
import { Terminal, Activity, BarChart3, Server } from 'lucide-react';
import { SystemOperations } from './SystemOperations';
import { LogsView } from './LogsView';
import BenchmarkRunner from './BenchmarkRunner';

export function InfrastructureView() {
    const [activeTab, setActiveTab] = useState('overview');

    return (
        <div className="space-y-6">
            <header className="flex justify-between items-center bg-black/20 p-4 rounded-xl border border-cyan-500/10 backdrop-blur-sm">
                <div>
                    <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-linear-to-r from-cyan-400 to-blue-500 font-display">
                        Infrastructure Command
                    </h2>
                    <p className="text-cyan-400/60 font-mono text-sm mt-1">
                        System monitoring, logs, and performance validation.
                    </p>
                </div>

                <div className="flex bg-black/40 p-1 rounded-lg border border-cyan-500/20">
                    <TabButton
                        active={activeTab === 'overview'}
                        onClick={() => setActiveTab('overview')}
                        icon={<Activity size={16} />}
                        label="System Overview"
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
                        label="Benchmarks"
                    />
                </div>
            </header>

            <div className="min-h-[600px]">
                {activeTab === 'overview' && (
                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <SystemOperations />
                    </div>
                )}
                {activeTab === 'logs' && (
                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <LogsView />
                    </div>
                )}
                {activeTab === 'benchmarks' && (
                    <div className="animate-in fade-in slide-in-from-bottom-4 duration-500">
                        <BenchmarkRunner />
                    </div>
                )}
            </div>
        </div>
    );
}

function TabButton({ active, onClick, icon, label }) {
    return (
        <button
            onClick={onClick}
            className={`flex items-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200 ${active
                    ? 'bg-cyan-500/20 text-cyan-300 shadow-[0_0_10px_rgba(34,211,238,0.1)]'
                    : 'text-gray-400 hover:text-cyan-200 hover:bg-white/5'
                }`}
        >
            {icon}
            <span>{label}</span>
        </button>
    );
}
