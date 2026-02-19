import { MessageSquare, Search, Brain, Database, GitBranch, ExternalLink } from 'lucide-react';

export type View = 'chat' | 'context-engine';

interface SidebarProps {
    activeView: View;
    onNavigate: (view: View) => void;
}

const NAV_ITEMS: { id: View; label: string; icon: typeof Brain }[] = [
    { id: 'chat', label: 'Chat', icon: MessageSquare },
    { id: 'context-engine', label: 'Context Engine', icon: Search },
];

const EXTERNAL_TOOLS: { href: string; label: string; icon: typeof Database; color: string }[] = [
    { href: 'http://localhost:6333/dashboard', label: 'Qdrant', icon: Database, color: 'var(--accent-cyan)' },
    { href: 'http://localhost:7474/browser/', label: 'Neo4j', icon: GitBranch, color: 'var(--accent-violet)' },
];

export function Sidebar({ activeView, onNavigate }: SidebarProps) {
    return (
        <aside className="flex h-full w-16 flex-col items-center border-r py-4 gap-1"
            style={{ borderColor: 'var(--border-subtle)', backgroundColor: 'var(--bg-surface)' }}>

            {/* Logo */}
            <div className="mb-6 flex h-9 w-9 items-center justify-center rounded-lg"
                style={{ background: 'linear-gradient(135deg, var(--accent-indigo), var(--accent-violet))' }}>
                <Brain className="h-5 w-5 text-white" />
            </div>

            {/* Nav items */}
            {NAV_ITEMS.map(({ id, label, icon: Icon }) => {
                const isActive = activeView === id;
                return (
                    <button
                        key={id}
                        onClick={() => onNavigate(id)}
                        title={label}
                        className={`group relative flex h-11 w-11 items-center justify-center rounded-lg transition-all duration-200 ${isActive
                                ? 'text-white'
                                : 'text-zinc-500 hover:text-zinc-300'
                            }`}
                        style={isActive ? {
                            backgroundColor: 'var(--accent-indigo-glow)',
                            boxShadow: '0 0 12px var(--accent-indigo-glow)',
                        } : {}}
                    >
                        <Icon className="h-5 w-5" />
                        {isActive && (
                            <span className="absolute left-0 top-1/2 -translate-y-1/2 h-5 w-[3px] rounded-r-full"
                                style={{ backgroundColor: 'var(--accent-indigo)' }} />
                        )}

                        {/* Tooltip */}
                        <span className="pointer-events-none absolute left-full ml-2 whitespace-nowrap rounded-md px-2 py-1 text-xs font-medium opacity-0 shadow-lg transition-opacity group-hover:opacity-100"
                            style={{ backgroundColor: 'var(--bg-card)', color: 'var(--text-main)', border: '1px solid var(--border-subtle)' }}>
                            {label}
                        </span>
                    </button>
                );
            })}

            {/* Divider */}
            <div className="my-3 h-px w-8" style={{ backgroundColor: 'var(--border-subtle)' }} />

            {/* External tool links */}
            {EXTERNAL_TOOLS.map(({ href, label, icon: Icon, color }) => (
                <a
                    key={href}
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    title={`Open ${label}`}
                    className="group relative flex h-11 w-11 items-center justify-center rounded-lg text-zinc-600 transition-all duration-200 hover:text-zinc-300"
                >
                    <Icon className="h-4.5 w-4.5" style={{ color }} />
                    <ExternalLink className="absolute right-0.5 top-0.5 h-2.5 w-2.5 opacity-0 transition-opacity group-hover:opacity-60" />

                    {/* Tooltip */}
                    <span className="pointer-events-none absolute left-full ml-2 whitespace-nowrap rounded-md px-2 py-1 text-xs font-medium opacity-0 shadow-lg transition-opacity group-hover:opacity-100"
                        style={{ backgroundColor: 'var(--bg-card)', color: 'var(--text-main)', border: '1px solid var(--border-subtle)' }}>
                        {label} ↗
                    </span>
                </a>
            ))}
        </aside>
    );
}
