import React from 'react';

export default function StatusBadge({ status = '' }) {
  const s = status.toLowerCase();

  let style = 'bg-slate-800/80 text-slate-300 border-slate-700';

  if (s.includes('resolved') || s.includes('self-service') || s.includes('guidance')) {
    style = 'bg-emerald-950/40 text-emerald-400 border-emerald-800/50';
  } else if (s.includes('waiting') || s.includes('approval') || s.includes('pending manager') || s.includes('pending finance')) {
    style = 'bg-amber-950/40 text-amber-400 border-amber-800/50';
  } else if (s.includes('security review') || s.includes('pending it security')) {
    style = 'bg-cyan-950/40 text-cyan-400 border-cyan-800/50';
  } else if (s.includes('critical') || s.includes('escalated to security')) {
    style = 'bg-red-950/40 text-red-400 border-red-800/50 animate-pulse';
  } else if (s.includes('escalated') || s.includes('in progress') || s.includes('diagnostic')) {
    style = 'bg-blue-950/40 text-blue-400 border-blue-800/50';
  } else if (s.includes('human review')) {
    style = 'bg-purple-950/40 text-purple-400 border-purple-800/50';
  } else if (s.includes('rejected')) {
    style = 'bg-rose-950/40 text-rose-400 border-rose-800/50';
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-1 rounded-md text-[11px] font-bold tracking-tight border uppercase font-mono ${style}`}>
      {status}
    </span>
  );
}
