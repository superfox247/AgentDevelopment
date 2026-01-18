import React, { useState } from 'react';
import { Radio, Cpu, FileOutput, Book, Users, Server, Hexagon } from 'lucide-react';
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
    <div className="flex h-screen overflow-hidden p-6 gap-6 relative">
      {/* Background Decor */}
      <div className="absolute top-0 left-0 w-full h-full pointer-events-none overflow-hidden z-0">
        <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-primary/5 blur-[120px] rounded-full mix-blend-screen animate-pulse-glow" />
        <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-secondary/10 blur-[120px] rounded-full mix-blend-screen" />
      </div>

      {/* Floating Sidebar / Dock */}
      <aside className="w-72 glass-panel-prime rounded-3xl flex flex-col z-10 relative shadow-2xl">
        <div className="p-8">
          <div className="flex items-center space-x-3 mb-1">
            <div className="relative">
              <Hexagon className="w-8 h-8 text-cyan-bright" strokeWidth={1.5} />
              <div className="absolute inset-0 bg-cyan-bright blur-lg opacity-40" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-widest font-display text-gradient-cyan">
                Agent Central
              </h1>
              <p className="text-[10px] text-zinc-400 uppercase tracking-[0.3em] pl-0.5">Antigravity Prime</p>
            </div>
          </div>
        </div>

        <nav className="flex-1 px-4 space-y-8 overflow-y-auto custom-scrollbar">
          <MenuSection title="Command">
            <NavButton
              active={activeTab === 'infrastructure'}
              onClick={() => setActiveTab('infrastructure')}
              icon={<Server className="w-5 h-5" />}
              label="Infrastructure"
            />
          </MenuSection>

          <MenuSection title="Intelligence">
            <NavButton
              active={activeTab === 'agents'}
              onClick={() => setActiveTab('agents')}
              icon={<Users className="w-5 h-5" />}
              label="Agents"
            />
            <NavButton
              active={activeTab === 'models'}
              onClick={() => setActiveTab('models')}
              icon={<Cpu className="w-5 h-5" />}
              label="Models"
            />
            <NavButton
              active={activeTab === 'skills'}
              onClick={() => setActiveTab('skills')}
              icon={<Book className="w-5 h-5" />}
              label="Skills"
            />
          </MenuSection>

          <MenuSection title="Factory">
            <NavButton
              active={activeTab === 'generator'}
              onClick={() => setActiveTab('generator')}
              icon={<Radio className="w-5 h-5" />}
              label="Generator"
            />
            <NavButton
              active={activeTab === 'artifacts'}
              onClick={() => setActiveTab('artifacts')}
              icon={<FileOutput className="w-5 h-5" />}
              label="Artifacts"
            />
          </MenuSection>
        </nav>

        <div className="p-4 mx-4 mb-4 rounded-xl bg-white/5 border border-white/5">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <div className="w-2.5 h-2.5 rounded-full bg-success shadow-[0_0_8px_var(--success)]"></div>
              <div className="absolute inset-0 rounded-full bg-success animate-ping opacity-40"></div>
            </div>
            <div className="flex flex-col">
              <span className="text-xs text-zinc-300 font-medium">System Online</span>
              <span className="text-[10px] text-zinc-500 font-mono">Connected</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content Area */}
      <main className="flex-1 glass-panel-prime rounded-3xl relative overflow-hidden z-10 shadow-2xl flex flex-col">
        {/* Top bar decor */}
        <div className="h-1 w-full bg-white/5 absolute top-0 left-0" />

        <div className="flex-1 overflow-y-auto p-8 font-body custom-scrollbar">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}

function MenuSection({ title, children }) {
  return (
    <div className="mb-2">
      <h3 className="px-4 text-[11px] font-bold text-zinc-500 uppercase tracking-[0.2em] mb-3 font-display opacity-80">{title}</h3>
      <div className="space-y-1">
        {children}
      </div>
    </div>
  );
}

function NavButton({ active, onClick, icon, label }) {
  return (
    <button
      onClick={onClick}
      className={`relative w-full flex items-center space-x-3 px-4 py-3 rounded-xl transition-all duration-300 group overflow-hidden ${active
        ? 'text-white shadow-[0_0_20px_rgba(0,240,255,0.1)]'
        : 'text-zinc-500 hover:text-white hover:bg-white/5'
        }`}
    >
      {/* Active BG */}
      {active && (
        <div className="absolute inset-0 bg-linear-to-r from-primary/10 to-transparent border-l-2 border-primary opacity-100" />
      )}

      <div className={`relative z-10 transition-transform duration-300 group-hover:translate-x-1 ${active ? 'translate-x-1' : ''}`}>
        {React.cloneElement(icon, {
          className: `w-5 h-5 transition-colors duration-300 ${active ? "text-primary drop-shadow-[0_0_5px_rgba(0,240,255,0.8)]" : "group-hover:text-primary/70"}`
        })}
      </div>
      <span className={`relative z-10 font-medium text-sm tracking-wide ${active ? 'font-semibold' : ''}`}>{label}</span>
    </button>
  );
}

export default App;


