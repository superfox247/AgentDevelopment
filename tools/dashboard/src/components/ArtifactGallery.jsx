import { useState, useEffect } from 'react';
import { FileText, Image as ImageIcon, Download, ExternalLink, RefreshCw } from 'lucide-react';

export default function ArtifactGallery() {
    const [artifacts, setArtifacts] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchArtifacts = () => {
        setLoading(true);
        fetch('/api/artifacts')
            .then(res => res.json())
            .then(data => {
                setArtifacts(data);
                setLoading(false);
            })
            .catch(() => setLoading(false));
    };

    useEffect(() => {
        fetchArtifacts();
    }, []);

    return (
        <div className="glass-panel p-6 rounded-xl">
            <div className="flex justify-between items-center mb-6">
                <div className="flex items-center space-x-3">
                    <div className="p-2 bg-fuchsia-500/10 rounded-lg text-fuchsia-400">
                        <FileText size={20} />
                    </div>
                    <div>
                        <h2 className="font-semibold text-white">Data Artifacts</h2>
                        <p className="text-xs text-zinc-400 font-mono">STORAGE::LOCAL_ARTIFACTS</p>
                    </div>
                </div>
                <button
                    onClick={fetchArtifacts}
                    className="p-2 hover:bg-zinc-800 rounded-lg text-zinc-400 hover:text-white transition"
                    title="Refresh Data"
                >
                    <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
                </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                {artifacts.map((file, idx) => (
                    <div key={idx} className="group glass-card rounded-xl overflow-hidden flex flex-col hover:border-zinc-600 transition-all duration-300">
                        {file.type === 'image' ? (
                            <div className="relative h-48 bg-zinc-900/50 overflow-hidden">
                                <div className="absolute inset-0 bg-gradient-to-t from-zinc-900 to-transparent z-10 opacity-60"></div>
                                <img src={`/api/artifacts/${file.path}`} alt={file.name} className="object-cover w-full h-full group-hover:scale-105 transition-transform duration-500" />
                                <div className="absolute top-2 right-2 z-20 bg-black/60 backdrop-blur-md px-2 py-1 rounded text-xs font-mono text-fuchsia-300 border border-fuchsia-500/30">
                                    PNG
                                </div>
                            </div>
                        ) : (
                            <div className="h-48 bg-zinc-900/50 flex flex-col items-center justify-center border-b border-zinc-800 relative group-hover:bg-zinc-800/50 transition">
                                <FileText size={48} className="text-zinc-700 group-hover:text-indigo-400 transition-colors duration-300" />
                                <div className="absolute top-2 right-2 bg-black/60 backdrop-blur-md px-2 py-1 rounded text-xs font-mono text-indigo-300 border border-indigo-500/30">
                                    MD
                                </div>
                            </div>
                        )}

                        <div className="p-4 flex-1 flex flex-col">
                            <div className="flex-1">
                                <h4 className="text-sm font-medium text-zinc-200 truncate mb-1" title={file.name}>{file.name}</h4>
                                <p className="text-xs text-zinc-500 font-mono truncate">{file.path}</p>
                            </div>

                            <div className="mt-4 flex items-center justify-between pt-4 border-t border-zinc-800/50">
                                <span className="text-[10px] uppercase tracking-wider text-zinc-600 font-bold">
                                    {file.type === 'image' ? 'Visual Asset' : 'Text Document'}
                                </span>
                                <a
                                    href={`/api/artifacts/${file.path}`}
                                    target="_blank"
                                    rel="noreferrer"
                                    className="text-zinc-400 hover:text-white transition flex items-center space-x-1 text-xs"
                                >
                                    <span>OPEN</span>
                                    <ExternalLink size={12} />
                                </a>
                            </div>
                        </div>
                    </div>
                ))}

                {artifacts.length === 0 && !loading && (
                    <div className="col-span-full py-12 text-center border-2 border-dashed border-zinc-800 rounded-xl">
                        <FileText size={48} className="mx-auto text-zinc-800 mb-4" />
                        <p className="text-zinc-500">No artifacts generated yet.</p>
                        <p className="text-sm text-zinc-600 mt-2">Run the verification sequence to generate data.</p>
                    </div>
                )}
            </div>
        </div>
    );
}
