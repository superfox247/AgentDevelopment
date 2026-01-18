import React, { useState } from 'react';
import { Radio, Cpu, FileOutput, BarChart3, Activity, Book, Users, Terminal } from 'lucide-react';
import { ModelsView } from './components/ModelsView';
import { GeneratorView } from './components/GeneratorView';
import { ArtifactsView } from './components/ArtifactsView';
import BenchmarkRunner from './components/BenchmarkRunner';
import { SystemOperations } from './components/SystemOperations';
import { AgentsView } from './components/AgentsView';
import { SkillsView } from './components/SkillsView';
import { LogsView } from './components/LogsView';

function App() {
  const [activeTab, setActiveTab] = useState('system');

  const renderContent = () => {
    switch (activeTab) {
      case 'models': return <ModelsView />;
      case 'generator': return <GeneratorView />;
      case 'artifacts': return <ArtifactsView />;
      case 'benchmarks': return <BenchmarkRunner />;
      case 'system': return <SystemOperations />;
      case 'agents': return <AgentsView />;
      case 'skills': return <SkillsView />;
      case 'logs': return <LogsView />;
      default: return <ModelsView />;
    }
  };

  return (
    <div className="flex h-screen overflow-hidden font-display">
      {/* Sidebar */}
      <aside className="w-64 glass-panel border-r border-cyan-500/20 flex flex-col z-10 relative">
        <div className="absolute inset-0 bg-linear-to-b from-cyan-900/10 to-transparent pointer-events-none"></div>
        <div className="p-6 relative">
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-linear-to-r from-cyan-400 to-violet-500 animate-pulse">
            Agent Central
          </h1>
          <p className="text-xs text-cyan-400/70 mt-1 uppercase tracking-wider font-mono">Operations Command</p>
        </div>

        <nav className="flex-1 px-4 space-y-2 relative">
          <MenuSection title="Development">
            <NavButton
              active={activeTab === 'system'}
              onClick={() => setActiveTab('system')}
              icon={<Activity className="w-5 h-5" />}
              label="Overview"
            />
            <NavButton
              active={activeTab === 'models'}
              onClick={() => setActiveTab('models')}
              icon={<Cpu className="w-5 h-5" />}
              label="Models"
            />
            <NavButton
              active={activeTab === 'agents'}
              onClick={() => setActiveTab('agents')}
              icon={<Users className="w-5 h-5" />}
              label="Agents"
            />
            <NavButton
              active={activeTab === 'skills'}
              onClick={() => setActiveTab('skills')}
              icon={<Book className="w-5 h-5" />}
              label="Skills"
            />
          </MenuSection>

          <MenuSection title="Tools">
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

          <MenuSection title="Operations">
            <NavButton
              active={activeTab === 'benchmarks'}
              onClick={() => setActiveTab('benchmarks')}
              icon={<BarChart3 className="w-5 h-5" />}
              label="Benchmarks"
            />

            <NavButton
              active={activeTab === 'logs'}
              onClick={() => setActiveTab('logs')}
              icon={<Terminal className="w-5 h-5" />}
              label="Logs"
            />
          </MenuSection>
        </nav>

        <div className="p-4 border-t border-cyan-500/20 relative">
          <div className="glass-card p-3 rounded-lg border border-cyan-500/30">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full bg-cyan-400 shadow-[0_0_10px_#22d3ee] animate-pulse"></div>
              <span className="text-xs text-cyan-100/70 font-mono">System Online</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto relative bg-[url('https://grainy-gradients.vercel.app/noise.svg')] bg-opacity-20">
        <div className="absolute inset-0 bg-linear-to-br from-indigo-950/40 to-cyan-950/20 pointer-events-none"></div>
        <div className="relative p-8 max-w-7xl mx-auto font-body">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}

function MenuSection({ title, children }) {
  return (
    <div className="mb-4">
      <h3 className="px-4 text-[10px] font-bold text-cyan-500/50 uppercase tracking-[0.2em] mb-2 font-display">{title}</h3>
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
      className={`w-full flex items-center space-x-3 px-4 py-2.5 rounded-none skew-x-[-10deg] border-l-2 transition-all duration-200 group ${active
        ? 'bg-cyan-950/40 text-cyan-300 border-cyan-400 shadow-[0_0_15px_rgba(34,211,238,0.1)]'
        : 'border-transparent text-gray-500 hover:text-cyan-400 hover:bg-cyan-950/20 hover:border-cyan-500/50'
        }`}
    >
      <div className="skew-x-10 flex items-center space-x-3 w-full">
        {React.cloneElement(icon, { className: `w-5 h-5 transition-colors ${active ? "text-cyan-400 drop-shadow-[0_0_5px_rgba(34,211,238,0.8)]" : "group-hover:text-cyan-400"}` })}
        <span className="font-medium tracking-wide">{label}</span>
      </div>
      {active && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_currentColor] skew-x-10"></div>}
    </button>
  );
}

export default App;

