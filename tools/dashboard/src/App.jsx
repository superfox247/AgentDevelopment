import React, { useState } from 'react';
import { LayoutDashboard, Radio, Cpu, FileOutput, BarChart3, Activity, Book, Users } from 'lucide-react';
import { ModelsView } from './components/ModelsView';
import { GeneratorView } from './components/GeneratorView';
import { ArtifactsView } from './components/ArtifactsView';
import BenchmarkRunner from './components/BenchmarkRunner';
import { SystemOperations } from './components/SystemOperations';
import { AgentsView } from './components/AgentsView';
import { SkillsView } from './components/SkillsView';

function App() {
  const [activeTab, setActiveTab] = useState('models');

  const renderContent = () => {
    switch (activeTab) {
      case 'models': return <ModelsView />;
      case 'generator': return <GeneratorView />;
      case 'artifacts': return <ArtifactsView />;
      case 'benchmarks': return <BenchmarkRunner />;
      case 'system': return <SystemOperations />;
      case 'agents': return <AgentsView />;
      case 'skills': return <SkillsView />;
      default: return <ModelsView />;
    }
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 glass-panel border-r border-white/5 flex flex-col z-10">
        <div className="p-6">
          <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-pink-500">
            Antigravity
          </h1>
          <p className="text-xs text-gray-500 mt-1 uppercase tracking-wider">Course Creator</p>
        </div>

        <nav className="flex-1 px-4 space-y-2">
          <MenuSection title="Development">
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
              active={activeTab === 'system'}
              onClick={() => setActiveTab('system')}
              icon={<Activity className="w-5 h-5" />}
              label="System Status"
            />
          </MenuSection>
        </nav>

        <div className="p-4 border-t border-white/5">
          <div className="glass-card p-3 rounded-lg">
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
              <span className="text-xs text-gray-400">System Online</span>
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto relative">
        <div className="absolute inset-0 bg-gradient-to-br from-indigo-900/20 to-pink-900/20 pointer-events-none"></div>
        <div className="relative p-8 max-w-7xl mx-auto">
          {renderContent()}
        </div>
      </main>
    </div>
  );
}

function MenuSection({ title, children }) {
  return (
    <div className="mb-4">
      <h3 className="px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider mb-2">{title}</h3>
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
      className={`w-full flex items-center space-x-3 px-4 py-2.5 rounded-lg transition-all duration-200 ${active
        ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
        : 'text-gray-400 hover:bg-white/5 hover:text-gray-200'
        }`}
    >
      {icon}
      <span className="font-medium">{label}</span>
      {active && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-indigo-400 shadow-[0_0_8px_currentColor]"></div>}
    </button>
  );
}

export default App;

