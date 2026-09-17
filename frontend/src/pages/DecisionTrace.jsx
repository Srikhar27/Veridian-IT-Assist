import React, { useState, useEffect } from 'react';
import StatusBadge from '../components/StatusBadge';
import PriorityBadge from '../components/PriorityBadge';
import { 
  GitFork, 
  Cpu, 
  Play, 
  Sparkles, 
  CheckCircle2, 
  Layers, 
  ShieldCheck, 
  Ticket, 
  Code, 
  ChevronRight,
  Copy,
  Check,
  Search
} from 'lucide-react';

export default function DecisionTrace({ initialQuery = '' }) {
  const [query, setQuery] = useState(initialQuery || "The network is not coming in my laptop");
  const [traceData, setTraceData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showRawJson, setShowRawJson] = useState(false);
  const [copied, setCopied] = useState(false);
  const [testCases, setTestCases] = useState([]);

  useEffect(() => {
    fetch('/api/test-cases')
      .then(res => res.json())
      .then(data => setTestCases(data))
      .catch(err => console.error('Error loading test cases', err));

    // Run initial trace
    runTrace(query);
  }, []);

  const runTrace = async (queryToRun) => {
    const q = queryToRun || query;
    if (!q || !q.trim()) return;

    setLoading(true);
    try {
      const res = await fetch('/api/trace', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: q.trim() })
      });
      const data = await res.json();
      setTraceData(data);
    } catch (err) {
      console.error('Error running decision trace:', err);
    } finally {
      setLoading(false);
    }
  };

  const copyJson = () => {
    if (!traceData) return;
    navigator.clipboard.writeText(JSON.stringify(traceData, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Signature Banner */}
      <div className="bg-gradient-to-r from-slate-900 via-slate-850 to-blue-950/40 border border-slate-800 rounded-2xl p-6 shadow-xl relative overflow-hidden">
        <div className="relative z-10 space-y-3">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-blue-600/30 border border-blue-500/50 flex items-center justify-center text-blue-400">
              <GitFork className="w-4 h-4" />
            </div>
            <h2 className="text-lg font-black text-white tracking-tight">Agent Decision Trace & AI Observability</h2>
            <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-cyan-950 text-cyan-300 border border-cyan-800">
              Signature Feature
            </span>
          </div>
          <p className="text-xs text-slate-300 max-w-3xl leading-relaxed">
            Inspect the full execution path from raw natural language input to entity extraction, policy grounding, ticket history matching, deterministic rule evaluation, and ticket creation.
          </p>

          {/* Test Cases Pill Bar */}
          <div className="pt-2">
            <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider block mb-2">
              All 12 Mandatory Benchmark Test Cases:
            </span>
            <div className="flex flex-wrap gap-1.5">
              {testCases.map((tc) => (
                <button
                  key={tc.id}
                  onClick={() => {
                    setQuery(tc.query);
                    runTrace(tc.query);
                  }}
                  className={`text-[11px] px-2.5 py-1 rounded-lg border font-medium transition-all ${
                    query === tc.query
                      ? 'bg-blue-600 text-white border-blue-500 shadow-md'
                      : 'bg-slate-900/90 border-slate-800 text-slate-300 hover:text-white hover:bg-slate-800'
                  }`}
                  title={tc.description}
                >
                  <span className="text-cyan-400 font-mono font-bold mr-1">#{tc.id}</span>
                  {tc.expected_intent}
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Query Input Box */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 shadow-lg flex gap-3">
        <div className="flex-1 relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3.5" />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && runTrace(query)}
            placeholder="Type any employee support query or policy question to inspect trace..."
            className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-10 pr-4 py-3 text-sm text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
          />
        </div>
        <button
          onClick={() => runTrace(query)}
          disabled={loading || !query.trim()}
          className="px-6 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-bold text-xs flex items-center gap-2 shadow-lg shadow-blue-600/30 transition-all disabled:opacity-50 whitespace-nowrap"
        >
          <Play className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : 'fill-current'}`} />
          <span>{loading ? 'Tracing Pipeline...' : 'Run Decision Trace'}</span>
        </button>
      </div>

      {/* Trace Stepper Container */}
      {traceData && (
        <div className="space-y-4">
          <div className="flex items-center justify-between px-1">
            <div className="text-xs font-bold text-slate-400 uppercase tracking-wider flex items-center gap-2">
              <Cpu className="w-4 h-4 text-cyan-400" />
              <span>5-Stage Execution Pipeline Result</span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setShowRawJson(!showRawJson)}
                className="text-xs font-semibold text-cyan-400 hover:text-cyan-300 flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800"
              >
                <Code className="w-3.5 h-3.5" />
                <span>{showRawJson ? 'Hide' : 'View'} Raw JSON</span>
              </button>
              <button
                onClick={copyJson}
                className="text-xs font-semibold text-slate-300 hover:text-white flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-800"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copied ? 'Copied' : 'Copy Trace'}</span>
              </button>
            </div>
          </div>

          {/* Raw JSON viewer if enabled */}
          {showRawJson && (
            <div className="p-4 bg-[#070A11] border border-slate-800 rounded-xl font-mono text-xs text-slate-300 overflow-x-auto">
              <pre>{JSON.stringify(traceData, null, 2)}</pre>
            </div>
          )}

          {/* 5 Distinct Stages as Structured Cards */}
          <div className="space-y-4">
            {traceData.stages.map((stage) => (
              <div 
                key={stage.step}
                className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 shadow-lg space-y-3"
              >
                {/* Stage Header */}
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div className="flex items-center gap-3">
                    <div className="w-7 h-7 rounded-lg bg-blue-600 flex items-center justify-center text-white font-mono font-bold text-xs shadow-md">
                      {stage.step}
                    </div>
                    <div>
                      <h3 className="text-sm font-bold text-white tracking-tight">{stage.name}</h3>
                      <p className="text-xs text-slate-400">{stage.summary}</p>
                    </div>
                  </div>
                  <span className="text-[11px] font-mono px-2.5 py-0.5 rounded-full bg-emerald-950/60 text-emerald-400 border border-emerald-800/50 font-semibold">
                    ✓ {stage.status}
                  </span>
                </div>

                {/* Stage Body Content */}
                <div className="text-xs">
                  {/* Stage 1: NLU */}
                  {stage.step === 1 && (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div className="p-3 bg-slate-850 rounded-lg border border-slate-750">
                        <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Detected Intent</span>
                        <span className="text-sm font-bold text-cyan-300 font-mono">{stage.data.intent}</span>
                      </div>
                      <div className="p-3 bg-slate-850 rounded-lg border border-slate-750">
                        <span className="text-[10px] uppercase font-bold text-slate-400 block mb-1">Extracted Entities</span>
                        <div className="space-y-1">
                          {Object.keys(stage.data.entities).length > 0 ? (
                            Object.entries(stage.data.entities).map(([k, v]) => (
                              <div key={k} className="text-slate-300 font-mono text-[11px]">
                                <span className="text-slate-400">{k}:</span> {String(v)}
                              </div>
                            ))
                          ) : (
                            <span className="text-slate-400 italic">No special entities extracted</span>
                          )}
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Stage 2: Policy Grounding */}
                  {stage.step === 2 && (
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <span className="text-slate-400 text-[11px]">Primary Source Citation:</span>
                        <span className="font-mono font-bold text-cyan-300 bg-blue-950 px-2 py-0.5 rounded border border-blue-900">
                          {stage.data.primary_source}
                        </span>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-3 pt-1">
                        {stage.data.retrieved_policies.length > 0 ? (
                          stage.data.retrieved_policies.map((p) => (
                            <div key={p.id} className="p-3 bg-slate-850 rounded-lg border border-slate-750 space-y-1.5">
                              <div className="flex items-center justify-between">
                                <span className="font-mono font-bold text-xs text-white">{p.id} — {p.title}</span>
                                <span className="text-[10px] text-cyan-400 font-mono">{p.category}</span>
                              </div>
                              <p className="text-[11px] text-slate-300">{p.description}</p>
                              <div className="text-[10px] text-amber-400 font-semibold pt-1">
                                Approval: {p.approval_required || 'None'}
                              </div>
                            </div>
                          ))
                        ) : (
                          <div className="col-span-2 p-3 bg-slate-850 rounded-lg border border-slate-750 text-slate-400 italic">
                            No matching policy found in current knowledge base (safe fallback invoked).
                          </div>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Stage 3: Ticket Precedent Matching */}
                  {stage.step === 3 && (
                    <div className="space-y-2">
                      {stage.data.matching_tickets.length > 0 ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                          {stage.data.matching_tickets.map((t) => (
                            <div key={t.id} className="p-3 bg-slate-850 rounded-lg border border-slate-750 space-y-1">
                              <div className="flex items-center justify-between">
                                <span className="font-mono font-bold text-blue-400">{t.id} ({t.employee})</span>
                                <span className="text-[10px] font-semibold text-slate-400">{t.active_status || t.status}</span>
                              </div>
                              <div className="text-slate-200 font-medium">"{t.issue}"</div>
                              <div className="text-[10px] text-cyan-400 font-mono">
                                Match Reason: {t.match_reason || 'Keyword precedent'}
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="p-3 bg-slate-850 rounded-lg border border-slate-750 text-slate-400 italic">
                          No prior ticket precedent found. Query is evaluated strictly against policy rules.
                        </div>
                      )}
                    </div>
                  )}

                  {/* Stage 4: Rule Engine */}
                  {stage.step === 4 && (
                    <div className="p-4 bg-slate-850 rounded-lg border border-slate-750 space-y-3">
                      <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-slate-750">
                        <div className="flex items-center gap-2">
                          <span className="text-slate-400 uppercase font-bold text-[10px]">Deterministic Decision:</span>
                          <StatusBadge status={stage.data.decision} />
                        </div>
                        <div className="flex items-center gap-2">
                          <PriorityBadge priority={stage.data.priority} />
                          <span className="text-[11px] font-mono text-slate-300">
                            Ticket Required: <b className={stage.data.requires_ticket ? 'text-amber-400' : 'text-emerald-400'}>{stage.data.requires_ticket ? 'TRUE' : 'FALSE'}</b>
                          </span>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-[11px]">
                        <div>
                          <span className="text-slate-400">Action: </span>
                          <span className="text-slate-200 font-medium">{stage.data.action}</span>
                        </div>
                        <div>
                          <span className="text-slate-400">Escalation Team: </span>
                          <span className="text-amber-400 font-semibold">{stage.data.escalation_team}</span>
                        </div>
                      </div>

                      <div className="text-[11px] text-slate-300 leading-relaxed bg-slate-900/80 p-2.5 rounded border border-slate-800">
                        <span className="text-slate-400 font-bold block mb-0.5">Policy Rationale:</span>
                        {stage.data.reason}
                      </div>
                    </div>
                  )}

                  {/* Stage 5: Final Output */}
                  {stage.step === 5 && (
                    <div className="p-4 bg-slate-850 rounded-lg border border-slate-750 space-y-3">
                      <div className="text-sm text-slate-100 font-medium leading-relaxed bg-slate-900 p-3 rounded-lg border border-slate-800">
                        {stage.data.final_answer}
                      </div>
                      <div className="flex flex-wrap items-center justify-between gap-2 text-xs pt-1">
                        <div className="flex items-center gap-2">
                          <span className="text-slate-400">Final Operational Status:</span>
                          <StatusBadge status={stage.data.final_status} />
                        </div>
                        <div className="flex items-center gap-2 font-mono">
                          <span className="text-slate-400">ITSM Ticket:</span>
                          <span className="font-bold text-blue-400">{stage.data.ticket_id}</span>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
