import React from 'react';
import { RefreshCw, Clock, CheckCircle2, ShieldCheck, User } from 'lucide-react';

export default function Header({ title, subtitle, onRefresh, isRefreshing = false }) {
  const now = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  return (
    <header className="bg-slate-900/80 backdrop-blur-md border-b border-slate-800/80 px-8 py-4 flex flex-col md:flex-row md:items-center justify-between gap-4 sticky top-0 z-20">
      <div>
        <h1 className="text-xl font-extrabold text-white tracking-tight flex items-center gap-2.5">
          {title}
        </h1>
        {subtitle && <p className="text-xs text-slate-400 mt-0.5 font-normal">{subtitle}</p>}
      </div>

      <div className="flex items-center gap-3 self-end md:self-auto">
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs text-slate-300">
          <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
          <span>Engine: <b className="text-white font-semibold">Deterministic Policy Grounding</b></span>
        </div>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs text-slate-300 font-mono">
          <Clock className="w-3.5 h-3.5 text-slate-400" />
          <span>Synced {now}</span>
        </div>

        {onRefresh && (
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-white border border-slate-700/60 transition-colors disabled:opacity-50"
            title="Refresh Data"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-blue-400' : ''}`} />
          </button>
        )}
      </div>
    </header>
  );
}
