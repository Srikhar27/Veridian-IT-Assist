import React from 'react';

export default function PriorityBadge({ priority = 'Low' }) {
  const p = priority.toLowerCase();

  let style = 'bg-emerald-950/30 text-emerald-400 border-emerald-800/40';
  if (p === 'critical') {
    style = 'bg-red-950/50 text-red-300 border-red-800/60 font-black';
  } else if (p === 'high') {
    style = 'bg-amber-950/40 text-amber-300 border-amber-800/50 font-bold';
  } else if (p === 'medium') {
    style = 'bg-blue-950/40 text-blue-300 border-blue-800/50 font-semibold';
  }

  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] uppercase font-mono tracking-wider border ${style}`}>
      {priority}
    </span>
  );
}
