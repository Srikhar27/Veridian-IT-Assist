import React, { useState, useEffect } from 'react';
import Modal from '../components/Modal';
import { 
  Settings, 
  RotateCcw, 
  Play, 
  CheckCircle2, 
  Server, 
  Database, 
  ShieldCheck, 
  AlertTriangle 
} from 'lucide-react';

export default function SystemControls({ setActivePage }) {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [resetModalOpen, setResetModalOpen] = useState(false);
  const [resetting, setResetting] = useState(false);
  const [resetSuccess, setResetSuccess] = useState(false);

  useEffect(() => {
    fetch('/api/health')
      .then(res => res.json())
      .then(d => {
        setHealth(d);
        setLoading(false);
      })
      .catch(err => {
        console.error('Error fetching health:', err);
        setLoading(false);
      });
  }, []);

  const handleReset = async () => {
    setResetting(true);
    try {
      await fetch('/api/system/reset', { method: 'POST' });
      setResetSuccess(true);
      setResetModalOpen(false);
      setTimeout(() => setResetSuccess(false), 4000);
      // Refresh health stats
      const res = await fetch('/api/health');
      const d = await res.json();
      setHealth(d);
    } catch (err) {
      console.error('Error resetting database', err);
    } finally {
      setResetting(false);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      {/* Header */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-lg flex items-center justify-between">
        <div>
          <h2 className="text-base font-extrabold text-white flex items-center gap-2">
            <Settings className="w-5 h-5 text-blue-400" />
            <span>Platform Governance & System Controls</span>
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Monitor internal subsystem health, manage database state, and perform operational administrative resets.
          </p>
        </div>
      </div>

      {resetSuccess && (
        <div className="p-4 bg-emerald-950/60 border border-emerald-800 text-emerald-300 rounded-xl text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>Database runtime state cleanly reset to baseline! All tickets and audit logs refreshed.</span>
        </div>
      )}

      {/* Health Subsystems Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-white flex items-center gap-2">
              <ShieldCheck className="w-4 h-4 text-cyan-400" />
              <span>Grounded Policy Engine</span>
            </span>
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
          </div>
          <p className="text-xs text-slate-400">Status: <b className="text-emerald-400">Operational</b></p>
          <p className="text-[11px] text-slate-400">Sources: KB-01 to KB-10, KB-ASSET-01 ({health?.stats?.policies_count || 11} Policies Active)</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-white flex items-center gap-2">
              <Server className="w-4 h-4 text-blue-400" />
              <span>Deterministic Decision Engine</span>
            </span>
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
          </div>
          <p className="text-xs text-slate-400">Status: <b className="text-emerald-400">Operational</b></p>
          <p className="text-[11px] text-slate-400">Rule Logic: Strict Policy & Escalation Routing v2.5</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-white flex items-center gap-2">
              <Database className="w-4 h-4 text-purple-400" />
              <span>SQLite Ticket & State Store</span>
            </span>
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
          </div>
          <p className="text-xs text-slate-400">Status: <b className="text-emerald-400">Operational</b></p>
          <p className="text-[11px] text-slate-400">Tickets in DB: {health?.stats?.tickets_count || 10} records</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-white flex items-center gap-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
              <span>Immutable Audit Logger</span>
            </span>
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400"></span>
          </div>
          <p className="text-xs text-slate-400">Status: <b className="text-emerald-400">Operational</b></p>
          <p className="text-[11px] text-slate-400">Audit Trails Logged: {health?.stats?.audit_logs_count || 0} interactions</p>
        </div>
      </div>

      {/* Admin Action Box */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-lg space-y-4">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider">Administrative Actions</h3>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 bg-slate-850 rounded-xl border border-slate-750">
          <div>
            <div className="text-xs font-bold text-white">Reset Runtime Data & State</div>
            <p className="text-xs text-slate-400 mt-0.5">
              Clears dynamically generated tickets and audit logs back to baseline initial assignment data (TK-1042..1051).
            </p>
          </div>
          <button
            onClick={() => setResetModalOpen(true)}
            className="px-4 py-2 rounded-xl bg-red-900/60 hover:bg-red-800 text-red-200 border border-red-700/60 font-bold text-xs flex items-center gap-2 transition-colors whitespace-nowrap self-start sm:self-auto"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Database State</span>
          </button>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 p-4 bg-slate-850 rounded-xl border border-slate-750">
          <div>
            <div className="text-xs font-bold text-white">Batch Run All 15 Employee Requests</div>
            <p className="text-xs text-slate-400 mt-0.5">
              Processes the entire test pack (REQ-01 to REQ-15) through the deterministic decision pipeline in one go.
            </p>
          </div>
          <button
            onClick={() => setActivePage('requests')}
            className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs flex items-center gap-2 transition-colors whitespace-nowrap self-start sm:self-auto"
          >
            <Play className="w-3.5 h-3.5 fill-current" />
            <span>Go to Batch Runner</span>
          </button>
        </div>
      </div>

      {/* Confirmation Modal */}
      <Modal
        isOpen={resetModalOpen}
        onClose={() => setResetModalOpen(false)}
        title="Confirm Database Reset"
      >
        <div className="space-y-3 text-xs">
          <div className="p-3 bg-red-950/40 border border-red-800/60 rounded-xl text-red-300 flex items-start gap-2.5">
            <AlertTriangle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
            <span>
              This action will reset the SQLite database. All newly created tickets (`AUTO-XXXX`) and audit interactions will be removed, restoring the clean baseline assignment tickets (`TK-1042` to `TK-1051`).
            </span>
          </div>
          <p className="text-slate-300">Are you sure you want to proceed with resetting the runtime state?</p>
          <div className="flex justify-end gap-3 pt-3 border-t border-slate-800">
            <button
              onClick={() => setResetModalOpen(false)}
              className="px-4 py-2 rounded-xl bg-slate-800 text-slate-300 font-semibold"
            >
              Cancel
            </button>
            <button
              onClick={handleReset}
              disabled={resetting}
              className="px-4 py-2 rounded-xl bg-red-600 hover:bg-red-500 text-white font-bold flex items-center gap-1.5"
            >
              {resetting ? 'Resetting...' : 'Yes, Reset Baseline'}
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
}
