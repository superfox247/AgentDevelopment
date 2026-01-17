import React, { useEffect, useState } from 'react';

export function ModelsView() {
    const [models, setModels] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetch('http://localhost:8010/api/models')
            .then(res => res.json())
            .then(data => {
                if (data.error) throw new Error(data.error);
                setModels(data);
                setLoading(false);
            })
            .catch(err => {
                setError(err.message);
                setLoading(false);
            });
    }, []);

    if (loading) return <div className="p-8 text-center text-gray-400">Loading models...</div>;
    if (error) return <div className="p-8 text-center text-red-400">Error: {error}</div>;

    return (
        <div className="space-y-6">
            <header>
                <h2 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-pink-500">
                    Available Models
                </h2>
                <p className="text-gray-400 mt-2">
                    Discover the Gemini models available for your agents.
                </p>
            </header>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {models.map((model) => (
                    <div key={model.name} className="glass-card p-6 rounded-xl flex flex-col h-full">
                        <div className="flex justify-between items-start mb-4">
                            <h3 className="text-lg font-semibold text-white break-all">{model.display_name}</h3>
                            <span className="text-xs font-mono bg-indigo-500/20 text-indigo-300 px-2 py-1 rounded">
                                {model.name.split('/').pop()}
                            </span>
                        </div>

                        <p className="text-sm text-gray-400 flex-grow mb-6 line-clamp-3">
                            {model.description}
                        </p>

                        <div className="space-y-3 pt-4 border-t border-white/5 text-sm">
                            <div className="flex justify-between">
                                <span className="text-gray-500">Input Limit</span>
                                <span className="font-mono text-gray-300">{model.input_token_limit.toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-500">Output Limit</span>
                                <span className="font-mono text-gray-300">{model.output_token_limit.toLocaleString()}</span>
                            </div>
                            <div className="flex justify-between">
                                <span className="text-gray-500">Temperature</span>
                                <span className="font-mono text-gray-300">{model.temperature || 'N/A'}</span>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
