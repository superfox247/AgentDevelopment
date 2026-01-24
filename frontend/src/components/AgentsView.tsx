import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { Users, Bot, AlertCircle, FileCode } from 'lucide-react';
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter';
import yaml from 'react-syntax-highlighter/dist/esm/languages/hljs/yaml';
import { atomOneDark } from 'react-syntax-highlighter/dist/esm/styles/hljs';

SyntaxHighlighter.registerLanguage('yaml', yaml);

import { AgentInfo } from '../api/schemas';

export function AgentsView() {
    const [selectedAgent, setSelectedAgent] = useState<{ domain: string; name: string } | null>(null);

    // 1. Agents List Query
    const { data: agentsData, isLoading: agentsLoading, error: agentsError } = useQuery({
        queryKey: ['agents'],
        queryFn: () => apiClient.getAgents(),
    });

    const agents = agentsData?.agents || [];

    // 2. Selected Agent Config Query
    const { data: configContent, isLoading: configLoading } = useQuery({
        queryKey: ['agent', selectedAgent?.domain, selectedAgent?.name],
        queryFn: () => apiClient.getAgentDetails(selectedAgent!.domain, selectedAgent!.name),
        enabled: !!selectedAgent,
    });

    // Derived content
    const content = typeof configContent === 'string'
        ? configContent
        : (configContent ? JSON.stringify(configContent, null, 2) : '');

    if (agentsError) return (
        <div className="flex items-center justify-center h-full text-red-400 gap-2">
            <AlertCircle className="w-5 h-5" />
            <span>Error: {agentsError instanceof Error ? agentsError.message : String(agentsError)}</span>
        </div>
    );

    // Group agents by domain
    const agentsByDomain = agents.reduce((acc, agent) => {
        if (!acc[agent.domain]) acc[agent.domain] = [];
        acc[agent.domain].push(agent);
        return acc;
    }, {} as Record<string, AgentInfo[]>);

    // Helper for rendering content area
    const renderContent = () => {
        if (configLoading) {
            return (
                <div className="flex items-center justify-center h-full text-gray-500">
                    Loading config...
                </div>
            );
        }

        if (selectedAgent) {
            return (
                <div className="absolute inset-0">
                    <SyntaxHighlighter
                        language="yaml"
                        style={atomOneDark}
                        customStyle={{ margin: 0, height: '100%', padding: '1.5rem', background: 'transparent' }}
                    >
                        {content}
                    </SyntaxHighlighter>
                </div>
            );
        }

        return (
            <div className="h-full flex flex-col items-center justify-center text-gray-500 gap-4">
                <Bot className="w-16 h-16 opacity-20" />
                <p>Select an agent to view its configuration.</p>
            </div>
        );
    };

    return (
        <div className="h-[calc(100vh-8rem)] flex gap-6">
            {/* Agents List */}
            <div className="w-1/3 glass-panel rounded-xl overflow-hidden flex flex-col">
                <div className="p-4 border-b border-white/5 bg-white/5">
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                        <Users className="w-5 h-5 text-indigo-400" />
                        Agent Registry
                    </h2>
                </div>
                <div className="flex-1 overflow-y-auto p-4 space-y-6">
                    {agentsLoading && !agents.length ? (
                        <div className="text-center text-gray-500 py-8">Loading agents...</div>
                    ) : (
                        Object.entries(agentsByDomain).map(([domain, domainAgents]) => (
                            <div key={domain}>
                                <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2 px-2">
                                    {domain.replace(/_/g, ' ')}
                                </h3>
                                <div className="space-y-1">
                                    {domainAgents.map(agent => (
                                        <button
                                            key={`${agent.domain}-${agent.name}`}
                                            onClick={() => setSelectedAgent({ domain: agent.domain, name: agent.name })}
                                            className={`w-full text-left px-4 py-3 rounded-lg transition-all duration-200 flex items-center justify-between group ${selectedAgent?.name === agent.name
                                                ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                                                : 'text-gray-400 hover:bg-white/5 hover:text-gray-200'
                                                }`}
                                        >
                                            <div className="flex items-center gap-3">
                                                <Bot className="w-4 h-4 opacity-70" />
                                                <span className="font-mono text-sm">{agent.name}</span>
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            </div>
                        ))
                    )}
                </div>
            </div>

            {/* Config Viewer */}
            <div className="flex-1 glass-panel rounded-xl overflow-hidden flex flex-col">
                <div className="p-4 border-b border-white/5 bg-white/5 flex justify-between items-center">
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                        <FileCode className="w-5 h-5 text-pink-400" />
                        {selectedAgent ? `${selectedAgent.domain} / ${selectedAgent.name}` : 'Select an Agent'}
                    </h2>
                </div>
                <div className="flex-1 overflow-y-auto bg-[#282c34] relative">
                    {renderContent()}
                </div>
            </div>
        </div>
    );
}
