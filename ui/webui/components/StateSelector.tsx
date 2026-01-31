
import React from 'react';
import { SwarmState } from '../types';

interface StateSelectorProps {
  currentState: SwarmState;
  onSelect: (state: SwarmState) => void;
}

const StateSelector: React.FC<StateSelectorProps> = ({ currentState, onSelect }) => {
  const states = [
    { id: SwarmState.SLEEPING, label: 'Sleeping', desc: 'The Nebula', color: 'bg-indigo-900/40 border-indigo-500' },
    { id: SwarmState.LEARNING, label: 'Learning', desc: 'Neural Path', color: 'bg-cyan-900/40 border-cyan-500' },
    { id: SwarmState.INTERACTING, label: 'Interacting', desc: 'Solar Flare', color: 'bg-orange-900/40 border-orange-500' }
  ];

  return (
    <div className="flex flex-col gap-4">
      {states.map((s) => (
        <button
          key={s.id}
          onClick={() => onSelect(s.id)}
          className={`
            group relative flex flex-col items-start p-4 w-64 rounded-xl border-2 transition-all duration-500
            ${currentState === s.id ? `${s.color} scale-105 shadow-lg shadow-white/5` : 'bg-black/40 border-white/10 opacity-60 hover:opacity-100'}
          `}
        >
          <span className="text-xs uppercase tracking-widest opacity-60 group-hover:opacity-100 font-bold">{s.label}</span>
          <span className="text-lg font-display tracking-wider mt-1">{s.desc}</span>
          {currentState === s.id && (
            <div className={`absolute -right-1 top-1/2 -translate-y-1/2 w-1 h-8 rounded-full ${s.color.split(' ')[1]}`}></div>
          )}
        </button>
      ))}
    </div>
  );
};

export default StateSelector;
