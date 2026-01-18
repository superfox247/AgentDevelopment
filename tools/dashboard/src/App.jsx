import React, { useState } from 'react';
import { Radio, Cpu, FileOutput, Book, Users, Server } from 'lucide-react';
import { ModelsView } from './components/ModelsView';
import { GeneratorView } from './components/GeneratorView';
import { ArtifactsView } from './components/ArtifactsView';
import { InfrastructureView } from './components/InfrastructureView';
import { AgentsView } from './components/AgentsView';
import { SkillsView } from './components/SkillsView';

function App() {
  const [activeTab, setActiveTab] = useState('infrastructure');

  const renderContent = () => {
    switch (activeTab) {
      case 'infrastructure': return <InfrastructureView />;
      case 'models': return <ModelsView />;
      case 'generator': return <GeneratorView />;
      case 'artifacts': return <ArtifactsView />;
      case 'agents': return <AgentsView />;
      case 'skills': return <SkillsView />;
      default: return <ModelsView />;
    }
  };

  return (
    <div className="flex h-screen overflow-hidden font-display bg-black text-white">
      {/* Sidebar */}
      <aside className="w-64 glass-panel border-r border-cyan-500/10 flex flex-col z-10 relative bg-black/60 backdrop-blur-md">
        <div className="p-6 relative">
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-linear-to-r from-cyan-400 to-violet-500">
            Agent Central
          </h1>
          <p className="text-xs text-zinc-500 mt-1 uppercase tracking-wider font-mono">Operations Command</p>
        </div>

        <nav className="flex-1 px-3 space-y-6 relative overflow-y-auto custom-scrollbar">
          <MenuSection title="Command">
            <NavButton
              active={activeTab === 'infrastructure'}
              onClick={() => setActiveTab('infrastructure')}
              icon={<Server className="w-4 h-4" />}
              label="Infrastructure"
            />
          </MenuSection>

          <MenuSection title="Intelligence">
            <NavButton
              active={activeTab === 'agents'}
              onClick={() => setActiveTab('agents')}
              icon={<Users className="w-4 h-4" />}
              label="Agents"
            />
            <NavButton
              active={activeTab === 'models'}
              onClick={() => setActiveTab('models')}
              icon={<Cpu className="w-4 h-4" />}
              label="Models"
            />
            <NavButton
              active={activeTab === 'skills'}
              onClick={() => setActiveTab('skills')}
              icon={<Book className="w-4 h-4" />}
              label="Skills"
            />
          </MenuSection>

          <MenuSection title="Factory">
            <NavButton
              active={activeTab === 'generator'}
              onClick={() => setActiveTab('generator')}
              icon={<Radio className="w-4 h-4" />}
              label="Generator"
            />
            <NavButton
              active={activeTab === 'artifacts'}
              onClick={() => setActiveTab('artifacts')}
              icon={<FileOutput className="w-4 h-4" />}
              label="Artifacts"
            />
          </MenuSection>
        </nav>

        <div className="p-4 border-t border-cyan-500/10 relative bg-black/40">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981]"></div>
              <div className="absolute inset-0 rounded-full bg-emerald-500 animate-ping opacity-20"></div>
            </div>
            <div className="flex flex-col">
              <span className="text-xs text-zinc-300 font-medium">System Online</span>
              <span className="text-[10px] text-zinc-500 font-mono">v2.1.0 Stable</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto relative bg-[url('https://grainy-gradients.vercel.app/noise.svg')] bg-opacity-20 bg-zinc-950">
        <div className="absolute inset-0 bg-linear-to-br from-indigo-950/20 to-cyan-950/20 pointer-events-none"></div>
        <div className="relative p-6 max-w-7xl mx-auto font-body">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}

function MenuSection({ title, children }) {
  return (
    <div className="mb-2">
      <h3 className="px-3 text-[10px] font-bold text-zinc-600 uppercase tracking-[0.2em] mb-2 font-display">{title}</h3>
      <div className="space-y-0.5">
        {children}
      </div>
    </div>
  );
}

function NavButton({ active, onClick, icon, label }) {
  return (
    <button
      onClick={onClick}
      className={`w-full flex items-center space-x-3 px-3 py-2 rounded-lg transition-all duration-200 group ${active
        ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/20'
        : 'border border-transparent text-zinc-500 hover:text-zinc-200 hover:bg-white/5'
        }`}
    >
      {React.cloneElement(icon, { className: `w-4 h-4 transition-colors ${active ? "text-cyan-400" : "group-hover:text-cyan-200"}` })}
      <span className="font-medium text-sm">{label}</span>
    </button>
  );
}

export default App;

