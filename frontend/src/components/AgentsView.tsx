import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { apiClient } from '../api/client';
import { Users, Bot, AlertCircle, FileCode, Server, Cpu, Info } from 'lucide-react';
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

    // 2. Selected Agent Metadata Query
    const { data: agentMetadata, isLoading: metadataLoading } = useQuery({
        queryKey: ['agent-metadata', selectedAgent?.name],
        queryFn: () => apiClient.getAgentMetadata(selectedAgent!.name),
        enabled: !!selectedAgent,
    });

    // 3. Selected Agent Config Query
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
        if (configLoading || metadataLoading) {
            return (
                <div className="flex items-center justify-center h-full text-gray-500">
                    Loading...
                </div>
            );
        }

        if (selectedAgent && agentMetadata) {
            return (
                <div className="absolute inset-0 flex flex-col">
                    {/* Metadata Panel */}
                    <div className="p-6 border-b border-white/10 bg-white/5">
                        <div className="space-y-4">
                            {agentMetadata.description && (
                                <div>
                                    <div className="flex items-center gap-2 mb-2 text-sm font-semibold text-gray-400">
                                        <Info className="w-4 h-4" />
                                        Description
                                    </div>
                                    <p className="text-gray-300 text-sm leading-relaxed">{agentMetadata.description}</p>
                                </div>
                            )}
                            <div className="grid grid-cols-2 gap-4">
                                {agentMetadata.model && (
                                    <div>
                                        <div className="flex items-center gap-2 mb-2 text-sm font-semibold text-gray-400">
                                            <Cpu className="w-4 h-4" />
                                            Model
                                        </div>
                                        <p className="text-gray-300 text-sm font-mono">{agentMetadata.model}</p>
                                    </div>
                                )}
                                <div>
                                    <div className="flex items-center gap-2 mb-2 text-sm font-semibold text-gray-400">
                                        <Server className="w-4 h-4" />
                                        Server
                                    </div>
                                    <p className={`text-sm ${agentMetadata.has_server ? 'text-green-400' : 'text-gray-500'}`}>
                                        {agentMetadata.has_server ? 'Available' : 'Not Available'}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                    {/* Config Code Viewer */}
                    <div className="flex-1 overflow-auto">
                        <SyntaxHighlighter
                            language="python"
                            style={atomOneDark}
                            customStyle={{ margin: 0, height: '100%', padding: '1.5rem', background: 'transparent' }}
                        >
                            {content}
                        </SyntaxHighlighter>
                    </div>
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
                                        <AgentListItem
                                            key={`${agent.domain}-${agent.name}`}
                                            agent={agent}
                                            isSelected={selectedAgent?.name === agent.name}
                                            onClick={() => setSelectedAgent({ domain: agent.domain, name: agent.name })}
                                        />
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

// Agent List Item Component with metadata preview
function AgentListItem({ 
    agent, 
    isSelected, 
    onClick 
}: { 
    agent: AgentInfo; 
    isSelected: boolean; 
    onClick: () => void;
}) {
    // Fetch metadata for preview (lightweight query)
    const { data: metadata } = useQuery({
        queryKey: ['agent-metadata-preview', agent.name],
        queryFn: () => apiClient.getAgentMetadata(agent.name),
        staleTime: 5 * 60 * 1000, // Cache for 5 minutes
    });

    return (
        <button
            onClick={onClick}
            className={`w-full text-left px-4 py-3 rounded-lg transition-all duration-200 group ${
                isSelected
                    ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                    : 'text-gray-400 hover:bg-white/5 hover:text-gray-200'
            }`}
        >
            <div className="flex items-start gap-3">
                <Bot className="w-4 h-4 opacity-70 mt-0.5 flex-shrink-0" />
                <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between gap-2 mb-1">
                        <span className="font-mono text-sm font-semibold">{agent.name}</span>
                        {metadata?.has_server && (
                            <Server className="w-3 h-3 text-green-400 opacity-70 flex-shrink-0" title="Server available" />
                        )}
                    </div>
                    {metadata?.description && (
                        <p className="text-xs text-gray-500 line-clamp-2 leading-relaxed">
                            {metadata.description}
                        </p>
                    )}
                    {metadata?.model && (
                        <p className="text-xs text-gray-600 mt-1 font-mono">
                            {metadata.model}
                        </p>
                    )}
                </div>
            </div>
        </button>
    );
}
