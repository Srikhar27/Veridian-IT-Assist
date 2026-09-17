import React from 'react';

export default function MetricCard({ title, value, delta, deltaType = 'blue', icon: Icon, subtitle }) {
  const deltaColors = {
    green: 'bg-emerald-950/40 text-emerald-400 border-emerald-800/40',
    blue: 'bg-blue-950/40 text-blue-400 border-blue-800/40',
    amber: 'bg-amber-950/40 text-amber-400 border-amber-800/40',
    red: 'bg-red-950/40 text-red-400 border-red-800/40',
  };

  return (
    <div className="bg-slate-900/90 border border-slate-800 hover:border-slate-700/90 rounded-xl p-5 shadow-lg shadow-black/20 transition-all hover:translate-y-[-2px] duration-200">
      <div className="flex items-center justify-between text-slate-400 mb-3">
        <span className="text-xs font-bold uppercase tracking-wider text-slate-400">{title}</span>
        {Icon && (
          <div className="w-8 h-8 rounded-lg bg-slate-800 border border-slate-700/50 flex items-center justify-center text-slate-300">
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>
      <div className="text-3xl font-extrabold text-white tracking-tight mb-2 font-sans">
        {value}
      </div>
      {(delta || subtitle) && (
        <div className="flex items-center gap-2">
          {delta && (
            <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border ${deltaColors[deltaType] || deltaColors.blue}`}>
              {delta}
            </span>
          )}
          {subtitle && <span className="text-xs text-slate-400">{subtitle}</span>}
        </div>
      )}
    </div>
  );
}
