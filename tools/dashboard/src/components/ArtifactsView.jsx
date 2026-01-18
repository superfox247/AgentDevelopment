import React, { useEffect, useState } from 'react';
import { FileText, Image as ImageIcon, ExternalLink } from 'lucide-react';

export function ArtifactsView() {
    const [artifacts, setArtifacts] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8010';
        fetch(`${API_URL}/api/artifacts`)
            .then(res => res.json())
            .then(data => {
                setArtifacts(data);
                setLoading(false);
            })
            .catch(() => setLoading(false));
    }, []);

    if (loading) return <div className="text-gray-400">Loading artifacts...</div>;
    if (!artifacts.length) return <div className="text-gray-500 italic">No artifacts generated yet.</div>;

    return (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {artifacts.map((art) => (
                <div key={art.path} className="glass-card rounded-xl overflow-hidden group relative">
                    <div className="aspect-square bg-black/20 flex items-center justify-center">
                        {art.type === 'image' ? (
                            <img
                                src={`${import.meta.env.VITE_API_URL || 'http://localhost:8010'}/api/artifacts/${art.path}`}
                                alt={art.name}
                                className="w-full h-full object-cover"
                            />
                        ) : (
                            <FileText className="w-12 h-12 text-indigo-400" />
                        )}
                    </div>

                    <div className="p-3">
                        <p className="text-sm font-medium text-gray-200 truncate" title={art.name}>{art.name}</p>
                        <p className="text-xs text-gray-500 mt-1 uppercase">{art.type}</p>
                    </div>

                    <a
                        href={`${import.meta.env.VITE_API_URL || 'http://localhost:8010'}/api/artifacts/${art.path}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="absolute top-2 right-2 p-2 bg-black/60 rounded-full text-white opacity-0 group-hover:opacity-100 transition-opacity hover:bg-indigo-600"
                    >
                        <ExternalLink className="w-4 h-4" />
                    </a>
                </div>
            ))}
        </div>
    );
}
