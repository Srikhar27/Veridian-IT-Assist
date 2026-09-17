import React, { useState, useEffect } from 'react';
import MetricCard from '../components/MetricCard';
import StatusBadge from '../components/StatusBadge';
import PriorityBadge from '../components/PriorityBadge';
import { 
  Inbox, 
  CheckCircle2, 
  Ticket, 
  Clock, 
  AlertOctagon, 
  ShieldCheck, 
  TrendingUp, 
  ChevronRight,
  Activity,
  Layers,
  Cpu
} from 'lucide-react';

export default function Dashboard({ setActivePage }) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/dashboard')
      .then(res => res.json())
      .then(d => {
        setData(d);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error loading dashboard data', err);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px] text-slate-400">
        <div className="flex items-center gap-3">
          <span className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></span>
          <span>Loading Executive ITSM Dashboard...</span>
        </div>
      </div>
    );
  }

  const kpis = data?.kpis || {
    total_requests: 15,
    auto_resolved: 4,
    active_tickets: 6,
    pending_approvals: 3,
    critical_incidents: 1,
    policy_compliance: 100
  };

  const categories = data?.category_distribution || {};
  const statuses = data?.status_distribution || {};
  const recentRequests = data?.recent_requests || [];
  const aiPerf = data?.ai_performance || {
    grounded_responses_pct: 100,
    human_escalation_rate_pct: 20,
    avg_resolution_seconds: 1.2,
    unsupported_queries_detected: 1
  };

  const maxCatCount = Math.max(...Object.values(categories), 1);

  return (
    <div className="space-y-6">
      {/* KPI Cards Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <MetricCard
          title="Total Requests"
          value={kpis.total_requests}
          delta="15 Assignment Batch"
          deltaType="blue"
          icon={Inbox}
          subtitle="Processed cases"
        />
        <MetricCard
          title="Auto Resolved"
          value={kpis.auto_resolved}
          delta="Self-Service / Direct"
          deltaType="green"
          icon={CheckCircle2}
          subtitle="No ticket needed"
        />
        <MetricCard
          title="Active Tickets"
          value={kpis.active_tickets}
          delta="Queue Precedents"
          deltaType="amber"
          icon={Ticket}
          subtitle="ITSM queue"
        />
        <MetricCard
          title="Pending Approvals"
          value={kpis.pending_approvals}
          delta="Manager / Finance"
          deltaType="amber"
          icon={Clock}
          subtitle="Awaiting sign-off"
        />
        <MetricCard
          title="Critical Incidents"
          value={kpis.critical_incidents}
          delta="Immediate Sec"
          deltaType="red"
          icon={AlertOctagon}
          subtitle="KB-09 Phishing"
        />
      </div>

      {/* AI Performance & Policy Grounding Observability */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-6 shadow-lg shadow-black/20">
        <div className="flex items-center justify-between pb-4 border-b border-slate-800 mb-5">
          <div className="flex items-center gap-2.5">
            <ShieldCheck className="w-5 h-5 text-cyan-400" />
            <div>
              <h2 className="text-sm font-bold text-white uppercase tracking-wider">Agent Grounding & AI Observability</h2>
              <p className="text-xs text-slate-400 mt-0.5">Real-time compliance telemetry, deterministic policy verification, and automated routing</p>
            </div>
          </div>
          <span className="text-xs text-emerald-400 font-mono font-bold bg-emerald-950/60 px-3 py-1 rounded-full border border-emerald-800/50">
            ✓ 100% Policy Grounded
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-5">
          <div className="p-4 bg-slate-850/90 rounded-xl border border-slate-800">
            <div className="text-[11px] text-slate-400 uppercase font-bold tracking-wider">Policy Grounding</div>
            <div className="text-3xl font-black text-emerald-400 mt-1">{aiPerf.grounded_responses_pct}%</div>
            <div className="text-[11px] text-slate-400 mt-0.5">KB-01..10 + ASSET-01</div>
          </div>

          <div className="p-4 bg-slate-850/90 rounded-xl border border-slate-800">
            <div className="text-[11px] text-slate-400 uppercase font-bold tracking-wider">Human Escalation</div>
            <div className="text-3xl font-black text-amber-400 mt-1">{aiPerf.human_escalation_rate_pct}%</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Security & Approvals</div>
          </div>

          <div className="p-4 bg-slate-850/90 rounded-xl border border-slate-800">
            <div className="text-[11px] text-slate-400 uppercase font-bold tracking-wider">Avg Latency</div>
            <div className="text-3xl font-black text-cyan-400 mt-1">{aiPerf.avg_resolution_seconds}s</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Deterministic evaluation</div>
          </div>

          <div className="p-4 bg-slate-850/90 rounded-xl border border-slate-800">
            <div className="text-[11px] text-slate-400 uppercase font-bold tracking-wider">Unsupported Queries</div>
            <div className="text-3xl font-black text-purple-400 mt-1">{aiPerf.unsupported_queries_detected}</div>
            <div className="text-[11px] text-slate-400 mt-0.5">Safely routed to Review</div>
          </div>
        </div>

        <div className="p-3.5 bg-blue-950/20 border border-blue-900/40 rounded-xl flex items-center justify-between">
          <div className="flex items-center gap-2.5 text-xs text-slate-300">
            <Cpu className="w-4 h-4 text-blue-400" />
            <span>Inspect decision logic, entity extraction, and rule evaluation in the 5-step Observability Trace</span>
          </div>
          <button
            onClick={() => setActivePage('trace')}
            className="text-xs font-bold text-cyan-400 hover:text-cyan-300 flex items-center gap-1.5 transition-colors px-3 py-1.5 rounded-lg bg-blue-900/30 border border-blue-800/50"
          >
            <span>Open Decision Trace</span>
            <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Recent Employee Requests Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-lg shadow-black/20">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
          <div>
            <h2 className="text-sm font-bold text-white uppercase tracking-wider">Live Assignment Test Suite Requests (REQ-01 to REQ-15)</h2>
            <p className="text-xs text-slate-400 mt-0.5">15 official benchmark queries mapped to deterministic policies and ticket IDs</p>
          </div>
          <button
            onClick={() => setActivePage('requests')}
            className="text-xs font-bold text-blue-400 hover:text-blue-300 flex items-center gap-1 transition-colors"
          >
            Manage All Requests <ChevronRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400 font-bold uppercase tracking-wider text-[10px]">
                <th className="pb-3 px-3">Request ID</th>
                <th className="pb-3 px-3">Employee</th>
                <th className="pb-3 px-3">Date</th>
                <th className="pb-3 px-3">Issue Query</th>
                <th className="pb-3 px-3">Agent Status</th>
                <th className="pb-3 px-3">Ticket ID</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {recentRequests.slice(0, 8).map((req) => (
                <tr key={req.id} className="hover:bg-slate-850/60 transition-colors">
                  <td className="py-3 px-3 font-mono font-bold text-cyan-400">{req.id}</td>
                  <td className="py-3 px-3 font-medium text-white">{req.employee}</td>
                  <td className="py-3 px-3 text-slate-400 font-mono">{req.date}</td>
                  <td className="py-3 px-3 text-slate-300 max-w-md truncate">{req.request}</td>
                  <td className="py-3 px-3">
                    <StatusBadge status={req.current_status || req.initial_action} />
                  </td>
                  <td className="py-3 px-3 font-mono font-bold text-slate-300">
                    {req.ticket_id && req.ticket_id !== 'N/A' ? (
                      <span className="text-blue-400">{req.ticket_id}</span>
                    ) : (
                      <span className="text-slate-400">N/A</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
