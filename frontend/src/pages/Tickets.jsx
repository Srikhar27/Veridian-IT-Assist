import React, { useState, useEffect } from 'react';
import StatusBadge from '../components/StatusBadge';
import PriorityBadge from '../components/PriorityBadge';
import Modal from '../components/Modal';
import { 
  Ticket, 
  Search, 
  Filter, 
  AlertTriangle, 
  Clock, 
  CheckCircle2, 
  User, 
  Building2, 
  ChevronRight,
  ShieldAlert
} from 'lucide-react';

export default function Tickets() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');
  const [priorityFilter, setPriorityFilter] = useState('All');
  const [selectedTicket, setSelectedTicket] = useState(null);

  const fetchTickets = () => {
    fetch('/api/tickets')
      .then(res => res.json())
      .then(data => {
        setTickets(data);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching tickets', err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchTickets();
  }, []);

  const openTicketsCount = tickets.filter(t => t.is_active).length;
  const pendingApprovalCount = tickets.filter(t => t.status && t.status.toLowerCase().includes('pending')).length;
  const criticalCount = tickets.filter(t => t.priority === 'Critical').length;
  const resolvedCount = tickets.filter(t => t.status && t.status.toLowerCase().includes('resolved')).length;

  const filteredTickets = tickets.filter(t => {
    const matchesSearch = !search || 
      t.id.toLowerCase().includes(search.toLowerCase()) || 
      t.employee.toLowerCase().includes(search.toLowerCase()) || 
      t.issue.toLowerCase().includes(search.toLowerCase());
    const matchesStatus = statusFilter === 'All' || (t.status && t.status.toLowerCase().includes(statusFilter.toLowerCase()));
    const matchesPriority = priorityFilter === 'All' || t.priority.toLowerCase() === priorityFilter.toLowerCase();
    return matchesSearch && matchesStatus && matchesPriority;
  });

  return (
    <div className="space-y-5">
      {/* ITSM Queue Summary Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
          <div>
            <span className="text-xs font-bold uppercase text-slate-400">Open Tickets</span>
            <div className="text-2xl font-black text-white mt-0.5">{openTicketsCount}</div>
          </div>
          <div className="w-10 h-10 rounded-lg bg-blue-950/40 text-blue-400 border border-blue-800/40 flex items-center justify-center">
            <Ticket className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
          <div>
            <span className="text-xs font-bold uppercase text-slate-400">Pending Approval</span>
            <div className="text-2xl font-black text-amber-400 mt-0.5">{pendingApprovalCount}</div>
          </div>
          <div className="w-10 h-10 rounded-lg bg-amber-950/40 text-amber-400 border border-amber-800/40 flex items-center justify-center">
            <Clock className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
          <div>
            <span className="text-xs font-bold uppercase text-slate-400">Critical Incidents</span>
            <div className="text-2xl font-black text-red-400 mt-0.5">{criticalCount}</div>
          </div>
          <div className="w-10 h-10 rounded-lg bg-red-950/40 text-red-400 border border-red-800/40 flex items-center justify-center">
            <ShieldAlert className="w-5 h-5" />
          </div>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex items-center justify-between">
          <div>
            <span className="text-xs font-bold uppercase text-slate-400">Resolved / Closed</span>
            <div className="text-2xl font-black text-emerald-400 mt-0.5">{resolvedCount}</div>
          </div>
          <div className="w-10 h-10 rounded-lg bg-emerald-950/40 text-emerald-400 border border-emerald-800/40 flex items-center justify-center">
            <CheckCircle2 className="w-5 h-5" />
          </div>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex-1 relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search tickets by ID, employee, or issue summary..."
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
            <option value="Active">Active Cases</option>
            <option value="Resolved">Resolved / Closed</option>
            <option value="Pending">Pending Approvals</option>
          </select>

          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-xl px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-blue-500"
          >
            <option value="All">All Priorities</option>
            <option value="Critical">Critical</option>
            <option value="High">High</option>
            <option value="Medium">Medium</option>
            <option value="Low">Low</option>
          </select>
        </div>
      </div>

      {/* Tickets Queue Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden shadow-lg">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="bg-slate-950/60 border-b border-slate-800 text-slate-400 font-bold uppercase tracking-wider text-[10px]">
                <th className="py-3 px-4">Ticket ID</th>
                <th className="py-3 px-4">Employee</th>
                <th className="py-3 px-4">Issue Summary</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Assigned Team</th>
                <th className="py-3 px-4">Priority</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-sans">
              {loading ? (
                <tr>
                  <td colSpan="8" className="py-12 text-center text-slate-400">Loading tickets queue...</td>
                </tr>
              ) : filteredTickets.length === 0 ? (
                <tr>
                  <td colSpan="8" className="py-12 text-center text-slate-400">No tickets found matching filters.</td>
                </tr>
              ) : (
                filteredTickets.map((t) => (
                  <tr 
                    key={t.id}
                    onClick={() => setSelectedTicket(t)}
                    className="hover:bg-slate-850/80 transition-colors cursor-pointer group"
                  >
                    <td className="py-3 px-4 font-mono font-bold text-cyan-400 whitespace-nowrap">{t.id}</td>
                    <td className="py-3 px-4 font-medium text-white">{t.employee}</td>
                    <td className="py-3 px-4 text-slate-200 max-w-sm truncate" title={t.issue}>{t.issue}</td>
                    <td className="py-3 px-4 text-slate-400 whitespace-nowrap">{t.category}</td>
                    <td className="py-3 px-4 font-medium text-slate-300 whitespace-nowrap">{t.assigned_team}</td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      <PriorityBadge priority={t.priority} />
                    </td>
                    <td className="py-3 px-4 whitespace-nowrap">
                      <StatusBadge status={t.status} />
                    </td>
                    <td className="py-3 px-4 text-right whitespace-nowrap">
                      <button 
                        className="px-2.5 py-1 rounded bg-slate-800 group-hover:bg-blue-600 text-slate-300 group-hover:text-white font-semibold transition-colors"
                        onClick={(e) => {
                          e.stopPropagation();
                          setSelectedTicket(t);
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

      {/* Ticket Details Modal */}
      {selectedTicket && (
        <Modal
          isOpen={Boolean(selectedTicket)}
          onClose={() => setSelectedTicket(null)}
          title={`Ticket Inspector: ${selectedTicket.id}`}
        >
          <div className="space-y-4 text-xs">
            <div className="p-4 bg-slate-850 rounded-xl border border-slate-750 space-y-2">
              <div className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Issue Description</div>
              <p className="text-sm font-semibold text-white">{selectedTicket.issue}</p>
              <div className="flex items-center gap-4 text-slate-400 text-[11px] pt-1">
                <span>Employee: <b className="text-slate-200">{selectedTicket.employee}</b></span>
                <span>Category: <b className="text-slate-200">{selectedTicket.category}</b></span>
                <span>Team: <b className="text-amber-400">{selectedTicket.assigned_team}</b></span>
              </div>
            </div>

            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="p-3 bg-slate-850 rounded-xl border border-slate-750">
                <span className="text-[10px] text-slate-400 block mb-1">Status</span>
                <StatusBadge status={selectedTicket.status} />
              </div>
              <div className="p-3 bg-slate-850 rounded-xl border border-slate-750">
                <span className="text-[10px] text-slate-400 block mb-1">Priority</span>
                <PriorityBadge priority={selectedTicket.priority} />
              </div>
              <div className="p-3 bg-slate-850 rounded-xl border border-slate-750">
                <span className="text-[10px] text-slate-400 block mb-1">Active State</span>
                <span className={`font-semibold ${selectedTicket.is_active ? 'text-emerald-400' : 'text-slate-400'}`}>
                  {selectedTicket.is_active ? '● Active Case' : '○ Closed Case'}
                </span>
              </div>
              <div className="p-3 bg-slate-850 rounded-xl border border-slate-750">
                <span className="text-[10px] text-slate-400 block mb-1">Source Policy</span>
                <span className="font-mono font-bold text-cyan-300">{selectedTicket.source_policy || 'N/A'}</span>
              </div>
            </div>

            {selectedTicket.escalation_reason && (
              <div className="p-4 bg-slate-850 rounded-xl border border-slate-750 space-y-1">
                <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Reason / Grounding Note</span>
                <p className="text-slate-200 font-medium leading-relaxed">{selectedTicket.escalation_reason}</p>
              </div>
            )}
          </div>
        </Modal>
      )}
    </div>
  );
}
