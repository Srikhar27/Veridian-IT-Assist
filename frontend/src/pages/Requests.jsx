import React, { useState, useEffect } from 'react';
import StatusBadge from '../components/StatusBadge';
import PriorityBadge from '../components/PriorityBadge';
import Modal from '../components/Modal';
import { 
  Play, 
  Search, 
  Filter, 
  CheckCircle2, 
  Clock, 
  AlertCircle, 
  Layers, 
  ArrowRight,
  ExternalLink,
  ChevronRight
} from 'lucide-react';

export default function Requests({ setActivePage, setTraceQuery }) {
  const [requests, setRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [selectedReq, setSelectedReq] = useState(null);
  const [processingAll, setProcessingAll] = useState(false);
  const [processingSingle, setProcessingSingle] = useState(false);

  const fetchRequests = () => {
    fetch('/api/requests')
      .then(res => res.json())
      .then(data => {
        setRequests(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching requests:', err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchRequests();
  }, []);

  const handleProcessAll = async () => {
    setProcessingAll(true);
    try {
      await fetch('/api/requests/process-all', { method: 'POST' });
      fetchRequests();
    } catch (err) {
      console.error('Error batch processing requests', err);
    } finally {
      setProcessingAll(false);
    }
  };

  const handleProcessSingle = async (reqId) => {
    setProcessingSingle(true);
    try {
      const res = await fetch(`/api/requests/${reqId}/process`, { method: 'POST' });
      const d = await res.json();
      if (d.request) {
        setSelectedReq(d.request);
      }
      fetchRequests();
    } catch (err) {
      console.error('Error processing single request:', err);
    } finally {
      setProcessingSingle(false);
    }
  };

  const filtered = requests.filter(r => {
    const matchesSearch = !search || 
      r.request.toLowerCase().includes(search.toLowerCase()) || 
      r.employee.toLowerCase().includes(search.toLowerCase()) || 
      r.id.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === 'All' || (r.current_status && r.current_status === statusFilter);
    return matchesSearch && matchesStatus;
  });

  const uniqueStatuses = Array.from(new Set(requests.map(r => r.current_status).filter(Boolean)));

  return (
    <div className="space-y-5">
      {/* Header Actions & Batch Runner */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-lg flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h2 className="text-base font-extrabold text-white">Employee Support Requests (REQ-01 to REQ-15)</h2>
          <p className="text-xs text-slate-400 mt-0.5">
            Official benchmark dataset from Assignment Section 2. Process all requests to trigger automated NLU, rule validation, and ticket generation.
          </p>
        </div>

        <button
          onClick={handleProcessAll}
          disabled={processingAll}
          className="px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-blue-600/25 transition-all disabled:opacity-50 whitespace-nowrap self-start md:self-auto"
        >
          <Play className={`w-3.5 h-3.5 ${processingAll ? 'animate-spin' : 'fill-current'}`} />
          <span>{processingAll ? 'Processing 15 Requests...' : 'Run All 15 Batch'}</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex-1 relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by Request ID, Employee, or Issue text..."
            className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-10 pr-4 py-2 text-xs text-white placeholder-slate-400 focus:outline-none focus:border-blue-500"
          />
        </div>

        <div className="flex items-center gap-2">
          <Filter className="w-4 h-4 text-slate-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
          >
            <option value="All">All Statuses</option>
            {uniqueStatuses.map(st => (
              <option key={st} value={st}>{st}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Requests Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-950/60 border-b border-slate-800 text-slate-400 font-bold uppercase tracking-wider text-[10px]">
                <th className="py-3 px-4">Request ID</th>
                <th className="py-3 px-4">Employee</th>
                <th className="py-3 px-4">Date</th>
                <th className="py-3 px-4">Request Query</th>
                <th className="py-3 px-4">Initial State</th>
                <th className="py-3 px-4">Agent Status</th>
                <th className="py-3 px-4">Ticket ID</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {loading ? (
                <tr>
                  <td colSpan="8" className="py-12 text-center text-slate-400">Loading benchmark requests...</td>
                </tr>
              ) : filtered.length === 0 ? (
                <tr>
                  <td colSpan="8" className="py-12 text-center text-slate-400">No requests match your filter.</td>
                </tr>
              ) : (
                filtered.map((r) => (
                  <tr 
                    key={r.id} 
                    onClick={() => setSelectedReq(r)}
                    className="hover:bg-slate-850/80 transition-colors cursor-pointer group"
                  >
                    <td className="py-3 px-4 font-mono font-bold text-cyan-400">{r.id}</td>
                    <td className="py-3 px-4 font-medium text-white">
                      <div>{r.employee}</div>
                      <div className="text-[10px] text-slate-400 font-normal">{r.email}</div>
                    </td>
                    <td className="py-3 px-4 text-slate-400 font-mono text-[11px] whitespace-nowrap">{r.date}</td>
                    <td className="py-3 px-4 text-slate-200 max-w-sm font-normal truncate" title={r.request}>
                      {r.request}
                    </td>
                    <td className="py-3 px-4 text-slate-400 text-[11px]">{r.initial_action}</td>
                    <td className="py-3 px-4">
                      <StatusBadge status={r.current_status || r.initial_action} />
                    </td>
                    <td className="py-3 px-4 font-mono font-bold text-slate-300">
                      {r.ticket_id && r.ticket_id !== 'N/A' ? (
                        <span className="text-blue-400 bg-blue-950/40 px-2 py-0.5 rounded border border-blue-900/60">
                          {r.ticket_id}
                        </span>
                      ) : (
                        <span className="text-slate-400">N/A</span>
                      )}
                    </td>
                    <td className="py-3 px-4 text-right">
                      <button 
                        className="px-2.5 py-1 rounded bg-slate-800 group-hover:bg-blue-600 text-slate-300 group-hover:text-white font-semibold transition-colors"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedReq(r);
                        }}
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Detail Modal for Selected Request */}
      {selectedReq && (
        <Modal
          isOpen={Boolean(selectedReq)}
          onClose={() => setSelectedReq(null)}
          title={`Request Inspector: ${selectedReq.id} — ${selectedReq.employee}`}
        >
          <div className="space-y-4 text-xs">
            <div className="p-4 bg-slate-850 rounded-xl border border-slate-750 space-y-2">
              <div className="text-[11px] text-slate-400 font-bold uppercase tracking-wider">Employee Query</div>
              <p className="text-sm font-medium text-white italic">"{selectedReq.request}"</p>
              <div className="text-slate-400 flex items-center gap-4 text-[11px] pt-1">
                <span>Employee: <b className="text-slate-200">{selectedReq.employee}</b></span>
                <span>Email: <b className="text-slate-200">{selectedReq.email}</b></span>
                <span>Date: <b className="text-slate-200">{selectedReq.date}</b></span>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div className="p-3.5 bg-slate-850 rounded-xl border border-slate-750">
                <span className="text-slate-400 block mb-1">Decision Status:</span>
                <StatusBadge status={selectedReq.current_status} />
              </div>
              <div className="p-3.5 bg-slate-850 rounded-xl border border-slate-750">
                <span className="text-slate-400 block mb-1">Associated Ticket ID:</span>
                <span className="font-mono font-bold text-sm text-blue-400">{selectedReq.ticket_id || 'N/A'}</span>
              </div>
            </div>

            {selectedReq.decision && (
              <div className="p-4 bg-slate-850 rounded-xl border border-slate-750 space-y-1">
                <span className="text-slate-400 font-bold uppercase text-[10px] tracking-wider">Operational Decision:</span>
                <p className="text-slate-200 font-medium">{selectedReq.decision}</p>
              </div>
            )}

            <div className="flex items-center justify-between pt-4 border-t border-slate-800">
              <button
                onClick={() => handleProcessSingle(selectedReq.id)}
                disabled={processingSingle}
                className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold flex items-center gap-2 disabled:opacity-50"
              >
                <Play className="w-3.5 h-3.5 fill-current" />
                <span>{processingSingle ? 'Evaluating...' : 'Re-Run Decision Engine'}</span>
              </button>

              <button
                onClick={() => {
                  setTraceQuery(selectedReq.request);
                  setActivePage('trace');
                }}
                className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-750 text-cyan-300 font-semibold flex items-center gap-2 border border-cyan-500/30"
              >
                <span>View 5-Stage Decision Trace</span>
                <ExternalLink className="w-3.5 h-3.5" />
              </button>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
