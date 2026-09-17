import React from 'react';
import { 
  Shield, 
  LayoutDashboard, 
  MessageSquare, 
  ListTodo, 
  Ticket, 
  BookOpen, 
  FileCheck, 
  GitFork, 
  Settings,
  Server,
  Activity
} from 'lucide-react';

export default function Sidebar({ activePage, setActivePage, isOnline = true }) {
  const navItems = [
    { id: 'dashboard', label: 'Overview Dashboard', icon: LayoutDashboard },
    { id: 'chat', label: 'AI Support Chat', icon: MessageSquare },
    { id: 'requests', label: 'Employee Requests', icon: ListTodo, badge: '15' },
    { id: 'tickets', label: 'Ticket Queue', icon: Ticket },
    { id: 'knowledge', label: 'Knowledge Base', icon: BookOpen, badge: '11' },
    { id: 'audit', label: 'Audit Trail', icon: FileCheck },
    { id: 'trace', label: 'Agent Decision Trace', icon: GitFork, highlight: true },
    { id: 'controls', label: 'System Controls', icon: Settings },
  ];

  return (
    <aside className="w-64 bg-[#0B0F19] border-r border-slate-800 flex flex-col justify-between flex-shrink-0 h-screen sticky top-0 select-none z-30">
      {/* Brand Header */}
      <div>
        <div className="p-5 border-b border-slate-800/80 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-600 via-blue-500 to-cyan-400 flex items-center justify-center shadow-lg shadow-blue-500/20 ring-1 ring-blue-400/30">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <div>
            <div className="font-extrabold text-white text-base tracking-tight leading-tight">VERIDIAN</div>
            <div className="text-[11px] font-semibold text-cyan-400 tracking-wider uppercase">IT Assist Enterprise</div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="p-3 space-y-1">
          <div className="px-3 pt-2 pb-1.5 text-[10px] font-bold tracking-wider text-slate-400 uppercase">
            Platform Operations
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activePage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActivePage(item.id)}
                className={`w-full flex items-center justify-between px-3 py-2.5 rounded-lg text-xs font-semibold transition-all duration-150 group ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-md shadow-blue-600/20'
                    : 'text-slate-300 hover:text-white hover:bg-slate-850/80'
                } ${item.highlight && !isActive ? 'border border-blue-500/30 bg-blue-950/20' : ''}`}
              >
                <div className="flex items-center gap-2.5">
                  <Icon className={`w-4 h-4 transition-colors ${isActive ? 'text-white' : item.highlight ? 'text-cyan-400' : 'text-slate-400 group-hover:text-slate-200'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className={`text-[10px] px-1.5 py-0.5 rounded-md font-mono font-bold ${
                    isActive ? 'bg-blue-700 text-white' : 'bg-slate-800 text-slate-400'
                  }`}>
                    {item.badge}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* System Footer & Operational Status */}
      <div className="p-3.5 m-3 rounded-xl bg-slate-900/90 border border-slate-800/90 space-y-2.5 text-xs shadow-inner">
        <div className="flex items-center justify-between">
          <span className="text-[11px] font-semibold text-slate-400">System Status</span>
          <div className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
            <span className="text-[11px] font-bold text-emerald-400">Operational</span>
          </div>
        </div>
        <div className="text-[11px] text-slate-400 leading-snug">
          Rule Engine: <span className="text-slate-200 font-semibold">Deterministic v2.5</span>
        </div>
        <div className="text-[11px] text-slate-400 leading-snug">
          Grounding: <span className="text-cyan-300 font-semibold">KB-01..10 + ASSET-01</span>
        </div>
        <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded-full bg-slate-800 border border-slate-700 flex items-center justify-center text-[10px] font-bold text-slate-300">
              IT
            </div>
            <div>
              <div className="text-[11px] font-bold text-slate-200 leading-none">IT Admin</div>
              <div className="text-[9px] text-slate-400">Operations Console</div>
            </div>
          </div>
          <Activity className="w-3.5 h-3.5 text-slate-400" />
        </div>
      </div>
    </aside>
  );
}
