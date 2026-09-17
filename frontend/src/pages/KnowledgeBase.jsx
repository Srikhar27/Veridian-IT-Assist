import React, { useState, useEffect } from 'react';
import { 
  BookOpen, 
  Search, 
  Filter, 
  CheckCircle, 
  Clock, 
  ShieldAlert, 
  Info, 
  Tag, 
  FileText,
  ExternalLink
} from 'lucide-react';

export default function KnowledgeBase() {
  const [policies, setPolicies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [activeCategory, setActiveCategory] = useState('All');

  useEffect(() => {
    fetch('/api/policies')
      .then(res => res.json())
      .then(data => {
        setPolicies(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching policies', err);
        setLoading(false);
      });
  }, []);

  const categories = [
    'All',
    'Identity & Access',
    'Network & Access',
    'Hardware & Devices',
    'Software & Applications',
    'Hardware & Peripherals',
    'Email & Collaboration',
    'Security & Incident Response',
    'Hardware & Remote Work',
    'Hardware & Lifecycle'
  ];

  const getApprovalBadge = (approval) => {
    const a = (approval || '').toLowerCase();
    if (a === 'none' || a.includes('none')) {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-emerald-950/50 text-emerald-400 border border-emerald-800/50">
          <CheckCircle className="w-3 h-3" /> No Approval Required
        </span>
      );
    } else if (a.includes('security')) {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-red-950/50 text-red-400 border border-red-800/50">
          <ShieldAlert className="w-3 h-3" /> Security Review Required
        </span>
      );
    } else if (a.includes('manager') || a.includes('finance') || a.includes('verification')) {
      return (
        <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-amber-950/50 text-amber-400 border border-amber-800/50">
          <Clock className="w-3 h-3" /> Approval Required
        </span>
      );
    }
    return (
      <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-[11px] font-bold bg-blue-950/50 text-blue-400 border border-blue-800/50">
        <Info className="w-3 h-3" /> Informational Policy
      </span>
    );
  };

  const filtered = policies.filter(p => {
    const matchesSearch = !search || 
      p.id.toLowerCase().includes(search.toLowerCase()) || 
      p.title.toLowerCase().includes(search.toLowerCase()) || 
      p.description.toLowerCase().includes(search.toLowerCase());
    const matchesCat = activeCategory === 'All' || (p.category && p.category.toLowerCase() === activeCategory.toLowerCase());
    return matchesSearch && matchesCat;
  });

  return (
    <div className="space-y-6">
      {/* Header Info */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-extrabold text-white flex items-center gap-2">
            <BookOpen className="w-5 h-5 text-blue-400" />
            <span>Veridian Corp Knowledge Base Policies (KB-01 to KB-10 + KB-ASSET-01)</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Authoritative source of truth for all deterministic AI decisions. All agent actions are strictly grounded in these policies.
          </p>
        </div>
        <div className="px-3 py-1.5 rounded-lg bg-blue-950/40 border border-blue-900/60 text-xs text-cyan-300 font-mono font-bold whitespace-nowrap self-start md:self-auto">
          11 Grounded Policies Active
        </div>
      </div>

      {/* Category Pills & Search */}
      <div className="space-y-3">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search policies by ID (e.g., KB-01), title, or keywords..."
            className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="flex flex-wrap gap-1.5 overflow-x-auto pb-1">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setActiveCategory(cat)}
              className={`text-xs px-3 py-1.5 rounded-lg font-medium transition-all ${
                activeCategory === cat
                  ? 'bg-blue-600 text-white shadow-md shadow-blue-600/25'
                  : 'bg-slate-900 border border-slate-800 text-slate-400 hover:text-white hover:bg-slate-800'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Policy Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {loading ? (
          <div className="col-span-2 py-12 text-center text-slate-400">Loading grounded knowledge base...</div>
        ) : filtered.length === 0 ? (
          <div className="col-span-2 py-12 text-center text-slate-400">No policies match your search.</div>
        ) : (
          filtered.map((p) => (
            <div 
              key={p.id}
              className="bg-slate-900/90 border border-slate-800 hover:border-slate-700 rounded-xl p-5 shadow-lg flex flex-col justify-between transition-all hover:translate-y-[-2px] duration-150"
            >
              <div className="space-y-3">
                <div className="flex items-center justify-between gap-2 border-b border-slate-800 pb-3">
                  <div className="flex items-center gap-2">
                    <span className="px-2.5 py-1 rounded bg-blue-600 font-mono font-black text-xs text-white shadow-sm">
                      {p.id}
                    </span>
                    <span className="text-xs text-slate-400 font-medium">{p.category}</span>
                  </div>
                  {getApprovalBadge(p.approval_required)}
                </div>

                <h3 className="text-sm font-bold text-white tracking-tight">{p.title}</h3>
                <p className="text-xs text-slate-300 leading-relaxed font-normal">{p.description}</p>

                {/* Allowed actions or troubleshooting steps */}
                {p.allowed_actions && (
                  <div className="space-y-1 pt-1">
                    <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Permitted Actions:</span>
                    <div className="flex flex-wrap gap-1.5">
                      {p.allowed_actions.map((act, idx) => (
                        <span key={idx} className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700/60 font-medium">
                          {act}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {p.troubleshooting_steps && (
                  <div className="space-y-1 pt-1">
                    <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">Troubleshooting Protocol:</span>
                    <ol className="list-decimal list-inside text-xs text-slate-300 space-y-0.5">
                      {p.troubleshooting_steps.map((st, idx) => (
                        <li key={idx}>{st}</li>
                      ))}
                    </ol>
                  </div>
                )}
              </div>

              {/* Source Reference Footer */}
              <div className="mt-4 pt-3 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400 font-mono">
                <span>Approval: <b className="text-slate-200">{p.approval_required || 'None'}</b></span>
                <span className="text-cyan-400">Veridian IT Grounding</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
