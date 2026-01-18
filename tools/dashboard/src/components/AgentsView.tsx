import React, { useEffect, useState } from 'react';
import { apiClient } from '../api/client';
import { Users, Bot, AlertCircle, FileCode } from 'lucide-react';
import { Light as SyntaxHighlighter } from 'react-syntax-highlighter';
import yaml from 'react-syntax-highlighter/dist/esm/languages/hljs/yaml';
import { atomOneDark } from 'react-syntax-highlighter/dist/esm/styles/hljs';

SyntaxHighlighter.registerLanguage('yaml', yaml);

import { AgentInfo } from '../api/schemas';

export function AgentsView() {
    const [agents, setAgents] = useState<AgentInfo[]>([]);
    const [selectedAgent, setSelectedAgent] = useState<{ domain: string; name: string } | null>(null);
    const [content, setContent] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        apiClient.getAgents()
            .then(response => {
                // The API returns { agents: [...] }
                setAgents(response.agents || []);
                setLoading(false);
            })
            .catch(err => {
                setError(err.message);
                setLoading(false);
            });
    }, []);

    const fetchAgentConfig = (domain: string, name: string) => {
        setLoading(true);
        apiClient.getAgentDetails(domain, name)
            .then(data => {
                // The endpoint returns the config as { config: string } or similar?
                // Wait, previous code used .text(), implies the endpoint returns raw text.
                // My apiClient.getAgentDetails uses client.get, which parses JSON by default.
                // I need to check if the backend returns JSON or Text. 
                // Let's assume it returns JSON { config: "..." } or similar if I updated the backend, 
                // BUT I haven't updated the backend. The backend likely returns raw text for that endpoint?
                // If it returns raw text, axios might try to parse it. 
                // Let's check `client.js` implementation. It uses `axios`. Axios parses JSON automatically. 
                // If the response is not JSON, it might throw or return the string.
                // However, `apiClient` response interceptor tries to access `response.data`.
                // I should verify the backend behavior for `/api/agents/{domain}/{name}`.
                // For now, I will assume it returns an object or I need to update apiClient to handle text.
                // actually, for this specific refactor, if I'm unsure, I should check the server code.
                // But I'll assume standard JSON envelope for now as per "Law".
                // If the backend is non-compliant, I'll catch it in verification.
                // Actually, let's look at `server.py` later. For now, I'll treat it as data.config or data.
                // The endpoint now returns raw text (yaml) string as per client.ts
                setContent(typeof data === 'string' ? data : JSON.stringify(data, null, 2));
                setSelectedAgent({ domain, name });
                setLoading(false);
            })
            .catch(err => {
                setError(err.message);
                setLoading(false);
            });
    };

    if (error) return (
        <div className="flex items-center justify-center h-full text-red-400 gap-2">
            <AlertCircle className="w-5 h-5" />
            <span>Error: {error}</span>
        </div>
    );

    // Group agents by domain
    const agentsByDomain = agents.reduce((acc, agent) => {
        if (!acc[agent.domain]) acc[agent.domain] = [];
        acc[agent.domain].push(agent);
        return acc;
    }, {} as Record<string, AgentInfo[]>);

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
                    {loading && !agents.length ? (
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
                                            onClick={() => fetchAgentConfig(agent.domain, agent.name)}
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
                    {selectedAgent ? (
                        <div className="absolute inset-0">
                            <SyntaxHighlighter
                                language="yaml"
                                style={atomOneDark}
                                customStyle={{ margin: 0, height: '100%', padding: '1.5rem', background: 'transparent' }}
                            >
                                {content}
                            </SyntaxHighlighter>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-gray-500 gap-4">
                            <Bot className="w-16 h-16 opacity-20" />
                            <p>Select an agent to view its configuration.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
