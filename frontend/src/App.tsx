import { ChatView } from './components/ChatView';

function App() {
    return (
        <div className="flex h-screen flex-col bg-[var(--bg-deep)] text-white">
            <header className="shrink-0 border-b border-white/10 px-6 py-4">
                <h1 className="text-xl font-semibold tracking-wide">Dashboard</h1>
                <p className="text-sm text-zinc-400">Chat with Researcher or Customer Service agent</p>
            </header>
            <main className="flex-1 overflow-auto p-6">
                <ChatView />
            </main>
        </div>
    );
}

export default App;
