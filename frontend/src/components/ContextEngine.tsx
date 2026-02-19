import { useState, useEffect, useCallback } from 'react';
import { Search, Database, GitBranch, FileText, Layers, Loader2, ChevronDown, ChevronRight } from 'lucide-react';
import { apiClient } from '../api/client';

// Types matching backend response
interface SearchResult {
    id: string;
    name: string | null;
    description: string | null;
    score: number | null;
    rerank_score: number | null;
    graph_props: Record<string, unknown>;
}

interface Stats {
    graph: { total_nodes?: number; breakdown?: Record<string, number>; error?: string };
    vector: { total_vectors?: number; status?: string; vector_size?: number; error?: string };
}

interface IndexedFile {
    path: string;
    hash: string | null;
    updated_at: number | null;
}

// Stat Card
function StatCard({ icon: Icon, label, value, color }: {
    icon: typeof Database; label: string; value: string | number; color: string;
}) {
    return (
        <div className="glass-card flex items-center gap-4 px-5 py-4">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg"
                style={{ backgroundColor: `${color}15` }}>
                <Icon className="h-5 w-5" style={{ color }} />
            </div>
            <div>
                <p className="text-2xl font-bold tracking-tight" style={{ color: 'var(--text-main)' }}>
                    {typeof value === 'number' ? value.toLocaleString() : value}
                </p>
                <p className="text-xs font-medium" style={{ color: 'var(--text-muted)' }}>{label}</p>
            </div>
        </div>
    );
}

// Score indicator
function ScoreBar({ score }: { score: number }) {
    const pct = Math.min(score * 100, 100);
    const hue = score > 0.3 ? 'var(--accent-emerald)' : score > 0.1 ? 'var(--accent-amber)' : 'var(--accent-rose)';
    return (
        <div className="score-bar" style={{ backgroundColor: hue, opacity: 0.3 + pct / 140 }} />
    );
}

// Result Card
function ResultCard({ result, rank }: { result: SearchResult; rank: number }) {
    const [expanded, setExpanded] = useState(false);
    // Prefer rerank score if meaningful (>0.001), otherwise fall back to vector score
    const rerankScore = result.rerank_score ?? 0;
    const vectorScore = result.score ?? 0;
    const score = rerankScore > 0.001 ? rerankScore : vectorScore;
    const desc = result.description ?? '';
    const preview = desc.length > 300 ? desc.slice(0, 300) + '…' : desc;

    return (
        <div className="glass-card flex gap-0 overflow-hidden">
            <ScoreBar score={score} />
            <div className="flex-1 p-4">
                <div className="flex items-start justify-between gap-3">
                    <div className="min-w-0 flex-1">
                        <div className="flex items-center gap-2 mb-1">
                            <span className="inline-flex h-5 w-5 shrink-0 items-center justify-center rounded text-[10px] font-bold"
                                style={{ backgroundColor: 'var(--accent-indigo-glow)', color: 'var(--accent-indigo)' }}>
                                {rank}
                            </span>
                            <h3 className="truncate text-sm font-semibold" style={{ color: 'var(--text-main)' }}>
                                {result.name || 'Unnamed'}
                            </h3>
                        </div>
                    </div>
                    <span className="shrink-0 rounded-full px-2 py-0.5 text-[11px] font-mono font-semibold"
                        style={{
                            backgroundColor: score > 0.3 ? 'rgba(16,185,129,0.12)' : score > 0.1 ? 'rgba(245,158,11,0.12)' : 'rgba(244,63,94,0.12)',
                            color: score > 0.3 ? 'var(--accent-emerald)' : score > 0.1 ? 'var(--accent-amber)' : 'var(--accent-rose)',
                        }}>
                        {score.toFixed(4)}
                    </span>
                </div>
                <pre className="mt-2 whitespace-pre-wrap text-xs leading-relaxed overflow-hidden"
                    style={{ color: 'var(--text-muted)', fontFamily: 'ui-monospace, monospace', maxHeight: expanded ? 'none' : '100px' }}>
                    {expanded ? desc : preview}
                </pre>
                {desc.length > 300 && (
                    <button onClick={() => setExpanded(!expanded)}
                        className="mt-2 text-xs font-medium transition-colors"
                        style={{ color: 'var(--accent-indigo)' }}>
                        {expanded ? 'Show less' : 'Show more'}
                    </button>
                )}
            </div>
        </div>
    );
}

// Skeleton loader for stats
function StatSkeleton() {
    return (
        <div className="glass-card flex items-center gap-4 px-5 py-4">
            <div className="skeleton h-10 w-10 rounded-lg" />
            <div className="flex-1 space-y-2">
                <div className="skeleton h-6 w-16 rounded" />
                <div className="skeleton h-3 w-24 rounded" />
            </div>
        </div>
    );
}

export function ContextEngine() {
    // State
    const [query, setQuery] = useState('');
    const [results, setResults] = useState<SearchResult[]>([]);
    const [stats, setStats] = useState<Stats | null>(null);
    const [files, setFiles] = useState<IndexedFile[]>([]);
    const [isSearching, setIsSearching] = useState(false);
    const [isLoadingStats, setIsLoadingStats] = useState(true);
    const [isLoadingFiles, setIsLoadingFiles] = useState(false);
    const [filesLoaded, setFilesLoaded] = useState(false);
    const [showFiles, setShowFiles] = useState(false);
    const [searchError, setSearchError] = useState<string | null>(null);
    const [hasSearched, setHasSearched] = useState(false);

    // Load stats + files on mount
    useEffect(() => {
        apiClient.getContextEngineStats()
            .then(setStats)
            .catch(err => console.error('Stats error:', err))
            .finally(() => setIsLoadingStats(false));

        setIsLoadingFiles(true);
        apiClient.getContextEngineFiles()
            .then(data => {
                setFiles(data.files);
                setFilesLoaded(true);
            })
            .catch(err => console.error('Files error:', err))
            .finally(() => setIsLoadingFiles(false));
    }, []);

    const toggleFiles = useCallback(() => {
        setShowFiles(prev => !prev);
    }, []);

    // Search handler
    const handleSearch = useCallback(async () => {
        if (!query.trim()) return;
        setIsSearching(true);
        setSearchError(null);
        setHasSearched(true);
        try {
            const data = await apiClient.searchContextEngine(query.trim());
            setResults(data.results);
        } catch (err) {
            setSearchError(err instanceof Error ? err.message : 'Search failed');
            setResults([]);
        } finally {
            setIsSearching(false);
        }
    }, [query]);

    const vectorCount = stats?.vector?.total_vectors ?? '—';
    const nodeCount = stats?.graph?.total_nodes ?? '—';
    const fileCount = (stats?.graph?.breakdown as Record<string, number> | undefined)?.["['File']"] ?? '—';
    const vectorSize = stats?.vector?.vector_size ?? '—';
    const collectionStatus = stats?.vector?.status ?? 'unknown';

    return (
        <div className="flex h-full flex-col overflow-hidden">
            {/* Header */}
            <header className="shrink-0 border-b px-6 py-4" style={{ borderColor: 'var(--border-subtle)' }}>
                <div className="flex items-center gap-3">
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg"
                        style={{ background: 'linear-gradient(135deg, var(--accent-indigo), var(--accent-cyan))' }}>
                        <Search className="h-4 w-4 text-white" />
                    </div>
                    <div>
                        <h1 className="text-lg font-semibold tracking-tight">Context Engine</h1>
                        <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                            Hybrid semantic search across {typeof fileCount === 'number' ? fileCount : '…'} indexed files
                        </p>
                    </div>
                    {collectionStatus === 'green' && (
                        <span className="ml-auto inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-[11px] font-medium"
                            style={{ backgroundColor: 'rgba(16,185,129,0.1)', color: 'var(--accent-emerald)' }}>
                            <span className="h-1.5 w-1.5 rounded-full" style={{ backgroundColor: 'var(--accent-emerald)' }} />
                            Online
                        </span>
                    )}
                </div>
            </header>

            <main className="flex-1 overflow-y-auto p-6 space-y-6">
                {/* Stats Cards */}
                <div className="grid grid-cols-2 gap-3 lg:grid-cols-4">
                    {isLoadingStats ? (
                        Array.from({ length: 4 }).map((_, i) => <StatSkeleton key={i} />)
                    ) : (
                        <>
                            <StatCard icon={Database} label="Vectors" value={vectorCount} color="var(--accent-cyan)" />
                            <StatCard icon={GitBranch} label="Graph Nodes" value={nodeCount} color="var(--accent-violet)" />
                            <StatCard icon={FileText} label="Files Indexed" value={fileCount} color="var(--accent-emerald)" />
                            <StatCard icon={Layers} label="Dimensions" value={vectorSize} color="var(--accent-amber)" />
                        </>
                    )}
                </div>

                {/* Search Bar */}
                <div className="glass-card flex items-center gap-3 px-4 py-3">
                    <Search className="h-4 w-4 shrink-0" style={{ color: 'var(--text-dim)' }} />
                    <input
                        type="text"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                        placeholder="Search your codebase... (e.g. 'authentication flow', 'rate limiting middleware')"
                        className="glow-focus flex-1 bg-transparent text-sm font-medium placeholder-zinc-600 outline-none"
                        style={{ color: 'var(--text-main)' }}
                    />
                    <button
                        onClick={handleSearch}
                        disabled={isSearching || !query.trim()}
                        className="flex items-center gap-2 rounded-lg px-4 py-2 text-xs font-semibold text-white transition-all disabled:opacity-40"
                        style={{ backgroundColor: 'var(--accent-indigo)' }}
                    >
                        {isSearching ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Search className="h-3.5 w-3.5" />}
                        Search
                    </button>
                </div>

                {/* Search Results */}
                {searchError && (
                    <div className="glass-card px-4 py-3 text-sm" style={{ borderColor: 'var(--accent-rose)', color: 'var(--accent-rose)' }}>
                        {searchError}
                    </div>
                )}

                {results.length > 0 && (
                    <div className="space-y-2">
                        <p className="text-xs font-medium" style={{ color: 'var(--text-muted)' }}>
                            {results.length} results — reranked by FlashRank
                        </p>
                        {results.map((r, i) => <ResultCard key={r.id} result={r} rank={i + 1} />)}
                    </div>
                )}

                {hasSearched && !isSearching && results.length === 0 && !searchError && (
                    <div className="flex flex-col items-center justify-center py-12 text-center">
                        <Search className="h-10 w-10 mb-3" style={{ color: 'var(--text-dim)' }} />
                        <p className="text-sm font-medium" style={{ color: 'var(--text-muted)' }}>No results found</p>
                        <p className="text-xs mt-1" style={{ color: 'var(--text-dim)' }}>Try a different query</p>
                    </div>
                )}

                {/* Indexed Files */}
                <div className="glass-card overflow-hidden">
                    <button
                        onClick={toggleFiles}
                        className="flex w-full items-center gap-2 px-4 py-3 text-sm font-semibold transition-colors hover:bg-white/2"
                        style={{ color: 'var(--text-main)' }}
                    >
                        {showFiles ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
                        <FileText className="h-4 w-4" style={{ color: 'var(--accent-emerald)' }} />
                        Indexed Files ({filesLoaded ? files.length : (typeof fileCount === 'number' ? fileCount : '…')})
                    </button>
                    {showFiles && (
                        <div className="border-t max-h-64 overflow-y-auto" style={{ borderColor: 'var(--border-subtle)' }}>
                            {isLoadingFiles ? (
                                <div className="flex items-center justify-center gap-2 py-8">
                                    <Loader2 className="h-4 w-4 animate-spin" style={{ color: 'var(--accent-indigo)' }} />
                                    <span className="text-xs" style={{ color: 'var(--text-muted)' }}>Loading files…</span>
                                </div>
                            ) : (
                                <table className="w-full text-xs">
                                    <thead>
                                        <tr style={{ backgroundColor: 'rgba(255,255,255,0.02)' }}>
                                            <th className="px-4 py-2 text-left font-medium" style={{ color: 'var(--text-muted)' }}>Path</th>
                                            <th className="px-4 py-2 text-right font-medium" style={{ color: 'var(--text-muted)' }}>Hash</th>
                                            <th className="px-4 py-2 text-right font-medium" style={{ color: 'var(--text-muted)' }}>Last Updated</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {files.map((f) => (
                                            <tr key={f.path} className="border-t hover:bg-white/2" style={{ borderColor: 'var(--border-subtle)' }}>
                                                <td className="px-4 py-2 font-mono" style={{ color: 'var(--text-main)' }}>{f.path}</td>
                                                <td className="px-4 py-2 font-mono text-right" style={{ color: 'var(--text-dim)' }}>
                                                    {f.hash ? f.hash.slice(0, 8) + '…' : '—'}
                                                </td>
                                                <td className="px-4 py-2 text-right whitespace-nowrap" style={{ color: 'var(--text-dim)' }}>
                                                    {f.updated_at
                                                        ? new Date(f.updated_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
                                                        : '—'}
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </div>
                    )}
                </div>
            </main>
        </div>
    );
}
