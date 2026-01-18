import React, { useEffect, useState } from 'react';
import { Book, Code, AlertCircle } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export function SkillsView() {
    const [skills, setSkills] = useState([]);
    const [selectedSkill, setSelectedSkill] = useState(null);
    const [content, setContent] = useState('');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetch('http://localhost:8010/api/skills')
            .then(res => res.json())
            .then(data => {
                setSkills(data);
                setLoading(false);
            })
            .catch(err => {
                setError(err.message);
                setLoading(false);
            });
    }, []);

    const fetchSkillContent = (name) => {
        setLoading(true);
        fetch(`http://localhost:8010/api/skills/${name}`)
            .then(res => res.text())
            .then(text => {
                setContent(text);
                setSelectedSkill(name);
                setLoading(false);
            })
            .catch(err => {
                setError(err.message);
                setLoading(false);
            });
    };

    if (error) return (
        <div className="flex items-center justify-center h-full text-red-400 gap-2">
            <AlertCircle className="w-5 h-5" />
            <span>Error: {error}</span>
        </div>
    );

    return (
        <div className="h-[calc(100vh-8rem)] flex gap-6">
            {/* Skills List */}
            <div className="w-1/3 glass-panel rounded-xl overflow-hidden flex flex-col">
                <div className="p-4 border-b border-white/5 bg-white/5">
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                        <Book className="w-5 h-5 text-indigo-400" />
                        Skills Library
                    </h2>
                </div>
                <div className="flex-1 overflow-y-auto p-2 space-y-2">
                    {loading && !skills.length ? (
                        <div className="text-center text-gray-500 py-8">Loading skills...</div>
                    ) : (
                        skills.map(skill => (
                            <button
                                key={skill.name}
                                onClick={() => fetchSkillContent(skill.name)}
                                className={`w-full text-left px-4 py-3 rounded-lg transition-all duration-200 flex items-center justify-between group ${selectedSkill === skill.name
                                        ? 'bg-indigo-600/20 text-indigo-300 border border-indigo-500/30'
                                        : 'text-gray-400 hover:bg-white/5 hover:text-gray-200'
                                    }`}
                            >
                                <span className="font-mono text-sm">{skill.name}</span>
                            </button>
                        ))
                    )}
                </div>
            </div>

            {/* Content Viewer */}
            <div className="flex-1 glass-panel rounded-xl overflow-hidden flex flex-col">
                <div className="p-4 border-b border-white/5 bg-white/5 flex justify-between items-center">
                    <h2 className="text-xl font-bold text-white flex items-center gap-2">
                        <Code className="w-5 h-5 text-pink-400" />
                        {selectedSkill ? selectedSkill : 'Select a Skill'}
                    </h2>
                </div>
                <div className="flex-1 overflow-y-auto p-6 bg-black/20">
                    {selectedSkill ? (
                        <div className="prose prose-invert max-w-none prose-pre:bg-black/50 prose-pre:border prose-pre:border-white/10">
                            <ReactMarkdown>{content}</ReactMarkdown>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col items-center justify-center text-gray-500 gap-4">
                            <Book className="w-16 h-16 opacity-20" />
                            <p>Select a skill from the list to view its documentation.</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
