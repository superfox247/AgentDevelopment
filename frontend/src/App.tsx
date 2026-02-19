import { useState } from 'react';
import { ChatView } from './components/ChatView';
import { ContextEngine } from './components/ContextEngine';
import { Sidebar, type View } from './components/Sidebar';

function App() {
    const [activeView, setActiveView] = useState<View>('context-engine');

    return (
        <div className="flex h-screen" style={{ backgroundColor: 'var(--bg-deep)', color: 'var(--text-main)' }}>
            <Sidebar activeView={activeView} onNavigate={setActiveView} />
            <div className="flex-1 flex flex-col min-w-0">
                {activeView === 'chat' && (
                    <>
                        <header className="shrink-0 border-b px-6 py-4" style={{ borderColor: 'var(--border-subtle)' }}>
                            <h1 className="text-lg font-semibold tracking-tight">Chat</h1>
                            <p className="text-xs" style={{ color: 'var(--text-muted)' }}>
                                Talk with Researcher or Customer Service agent
                            </p>
                        </header>
                        <main className="flex-1 overflow-auto p-6">
                            <ChatView />
                        </main>
                    </>
                )}
                {activeView === 'context-engine' && <ContextEngine />}
            </div>
        </div>
    );
}

export default App;
