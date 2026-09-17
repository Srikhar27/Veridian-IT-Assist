import React, { useState, useEffect } from 'react';
import StatusBadge from '../components/StatusBadge';
import PriorityBadge from '../components/PriorityBadge';
import Modal from '../components/Modal';
import { 
  FileCheck, 
  Search, 
  ShieldCheck, 
  AlertTriangle, 
  UserCheck, 
  Layers, 
  ChevronRight,
  Code,
  Copy,
  Check
} from 'lucide-react';

export default function AuditTrail() {
  const [auditData, setAuditData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedLog, setSelectedLog] = useState(null);
  const [showJson, setShowJson] = useState(false);
  const [copied, setCopied] = useState(false);

  const fetchAudit = () => {
    fetch('/api/audit')
      .then(res => res.json())
      .then(data => {
        setAuditData(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching audit trail', err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchAudit();
  }, []);

  const logs = auditData?.logs || [];
  const metrics = auditData?.metrics || {
    total_records: 0,
    grounded_count: 0,
    escalated_count: 0,
    human_reviews: 0
  };

  const filteredLogs = logs.filter(l => {
    if (!search) return true;
    const s = search.toLowerCase();
    return (
      (l.user_input && l.user_input.toLowerCase().includes(s)) ||
      (l.employee && l.employee.toLowerCase().includes(s)) ||
      (l.request_id && l.request_id.toLowerCase().includes(s)) ||
      (l.detected_intent && l.detected_intent.toLowerCase().includes(s)) ||
      (l.retrieved_policy && l.retrieved_policy.toLowerCase().includes(s)) ||
      (l.generated_ticket_id && l.generated_ticket_id.toLowerCase().includes(s))
    );
  });

  const copyJson = (obj) => {
    navigator.clipboard.writeText(JSON.stringify(obj, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-5">
      {/* Compliance Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
          <div>
            <span className="text-xs font-bold uppercase text-slate-400">Total Interactions Logged</span>
            <div className="text-2xl font-black text-white mt-0.5">{metrics.total_records}</div>
          </div>
          <div className="w-10 h-10 rounded-lg bg-blue-950/40 text-blue-400 border border-blue-800/40 flex items-center justify-center">
            <FileCheck className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
          <div>
            <span className="text-xs font-bold uppercase text-slate-400">Policy-Grounded Decisions</span>
            <div className="text-2xl font-black text-emerald-400 mt-0.5">{metrics.grounded_count}</div>
          </div>
          <div className="w-10 h-10 rounded-lg bg-emerald-950/40 text-emerald-400 border border-emerald-800/40 flex items-center justify-center">
            <ShieldCheck className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
          <div>
            <span className="text-xs font-bold uppercase text-slate-400">Escalations Logged</span>
            <div className="text-2xl font-black text-amber-400 mt-0.5">{metrics.escalated_count}</div>
          </div>
          <div className="w-10 h-10 rounded-lg bg-amber-950/40 text-amber-400 border border-amber-800/40 flex items-center justify-center">
            <AlertTriangle className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
          <div>
            <span className="text-xs font-bold uppercase text-slate-400">Human Reviews Required</span>
            <div className="text-2xl font-black text-purple-400 mt-0.5">{metrics.human_reviews}</div>
          </div>
          <div className="w-10 h-10 rounded-lg bg-purple-950/40 text-purple-400 border border-purple-800/40 flex items-center justify-center">
            <UserCheck className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="relative">
        <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Filter audit records by Employee, Query, Intent, Policy citation, or Ticket ID..."
          className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-10 pr-4 py-2.5 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
        />
      </div>

      {/* Audit Log Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-950/60 border-b border-slate-800 text-slate-400 font-bold uppercase tracking-wider text-[10px]">
                <th className="py-3 px-4">Audit ID</th>
                <th className="py-3 px-4">Timestamp</th>
                <th className="py-3 px-4">Request ID</th>
                <th className="py-3 px-4">Employee</th>
                <th className="py-3 px-4">User Query</th>
                <th className="py-3 px-4">Intent</th>
                <th className="py-3 px-4">Policy</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4">Ticket</th>
                <th className="py-3 px-4 text-right">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {loading ? (
                <tr>
                  <td colSpan="10" className="py-12 text-center text-slate-400">Loading audit trail...</td>
                </tr>
              ) : filteredLogs.length === 0 ? (
                <tr>
                  <td colSpan="10" className="py-12 text-center text-slate-400">No audit records found.</td>
                </tr>
              ) : (
                filteredLogs.map((l) => (
                  <tr 
                    key={l.id}
                    onClick={() => setSelectedLog(l)}
                    className="hover:bg-slate-850/80 transition-colors cursor-pointer group"
                  >
                    <td className="py-3 px-4 font-mono text-[11px] font-bold text-slate-400">{l.audit_id_formatted}</td>
                    <td className="py-3 px-4 text-slate-400 font-mono text-[11px] whitespace-nowrap">{l.timestamp}</td>
                    <td className="py-3 px-4 font-mono font-bold text-cyan-400">{l.request_id}</td>
                    <td className="py-3 px-4 text-white font-medium whitespace-nowrap">{l.employee}</td>
                    <td className="py-3 px-4 text-slate-300 max-w-xs truncate" title={l.user_input}>{l.user_input}</td>
                    <td className="py-3 px-4 text-slate-200 font-medium whitespace-nowrap">{l.detected_intent}</td>
                    <td className="py-3 px-4 font-mono text-cyan-300 whitespace-nowrap">{l.retrieved_policy}</td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      <StatusBadge status={l.final_status} />
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-slate-300 whitespace-nowrap">
                      {l.generated_ticket_id && l.generated_ticket_id !== 'N/A' ? (
                        <span className="text-blue-400">{l.generated_ticket_id}</span>
                      ) : (
                        <span className="text-slate-400">N/A</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right whitespace-nowrap">
                      <button 
                        className="px-2.5 py-1 rounded bg-slate-800 group-hover:bg-blue-600 text-slate-300 group-hover:text-white font-semibold transition-colors"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedLog(l);
                        }}
                      >
                        Details
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Audit Detail Modal */}
      {selectedLog && (
        <Modal
          isOpen={Boolean(selectedLog)}
          onClose={() => {
            setSelectedLog(null);
            setShowJson(false);
          }}
          title={`Audit Record: ${selectedLog.audit_id_formatted} (Request: ${selectedLog.request_id})`}
        >
          <div className="space-y-4 text-xs">
            <div className="p-4 bg-slate-850 rounded-xl border border-slate-750 space-y-2">
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Query & User Information</span>
              <p className="text-sm font-semibold text-white">"{selectedLog.user_input}"</p>
              <div className="flex flex-wrap gap-4 text-slate-400 text-[11px] pt-1">
                <span>Employee: <b className="text-slate-200">{selectedLog.employee}</b></span>
                <span>Timestamp: <b className="text-slate-200">{selectedLog.timestamp}</b></span>
                <span>Ticket ID: <b className="text-blue-400 font-mono">{selectedLog.generated_ticket_id}</b></span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-3.5 bg-slate-850 rounded-xl border border-slate-750 space-y-1">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Detected Intent</span>
                <span className="text-sm font-bold text-cyan-300 font-mono">{selectedLog.detected_intent}</span>
              </div>
              <div className="p-3.5 bg-slate-850 rounded-xl border border-slate-750 space-y-1">
                <span className="text-slate-400 block text-[10px] uppercase font-bold">Grounding Policy</span>
                <span className="text-sm font-bold text-blue-400 font-mono">{selectedLog.retrieved_policy}</span>
              </div>
            </div>

            <div className="p-3.5 bg-slate-850 rounded-xl border border-slate-750 space-y-1">
              <span className="text-slate-400 block text-[10px] uppercase font-bold">Action Taken</span>
              <p className="text-slate-200 font-medium">{selectedLog.action_taken}</p>
            </div>

            <div className="p-3.5 bg-slate-850 rounded-xl border border-slate-750 space-y-1">
              <span className="text-slate-400 block text-[10px] uppercase font-bold">Decision Rationale</span>
              <p className="text-slate-200 font-medium leading-relaxed">{selectedLog.decision}</p>
            </div>

            <div className="pt-2 flex items-center justify-between border-t border-slate-800">
              <button
                onClick={() => setShowJson(!showJson)}
                className="text-cyan-400 hover:text-cyan-300 font-semibold flex items-center gap-1.5 text-xs"
              >
                <Code className="w-3.5 h-3.5" />
                <span>{showJson ? 'Hide' : 'View'} Raw Structured JSON</span>
              </button>

              <button
                onClick={() => copyJson(selectedLog)}
                className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-750 text-slate-300 hover:text-white font-medium flex items-center gap-1.5 text-xs border border-slate-700"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Copied' : 'Copy Record JSON'}</span>
              </button>
            </div>

            {showJson && (
              <div className="p-4 bg-[#070A11] border border-slate-800 rounded-xl font-mono text-[11px] text-slate-300 overflow-x-auto max-h-60">
                <pre>{JSON.stringify(selectedLog, null, 2)}</pre>
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  );
}
