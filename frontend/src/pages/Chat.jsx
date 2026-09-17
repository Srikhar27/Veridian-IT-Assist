import React, { useState, useRef, useEffect } from 'react';
import StatusBadge from '../components/StatusBadge';
import PriorityBadge from '../components/PriorityBadge';
import { 
  Send, 
  Bot, 
  User, 
  Sparkles, 
  ChevronDown, 
  ChevronUp, 
  ExternalLink, 
  ShieldAlert, 
  HelpCircle,
  Copy,
  Check,
  RotateCcw
} from 'lucide-react';

export default function Chat({ setActivePage, setTraceQuery }) {
  const [messages, setMessages] = useState([
    {
      id: 'welcome',
      sender: 'assistant',
      text: "Hello! I am Veridian IT Assist, your enterprise AI support and decision intelligence assistant. You can ask me about password resets, VPN credentials, hardware replacements, software catalog approvals, email quotas, remote work equipment, or report security incidents.",
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      result: null
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [expandedTrace, setExpandedTrace] = useState({});
  const [copiedId, setCopiedId] = useState(null);
  const chatEndRef = useRef(null);

  const quickPrompts = [
    { label: "🔑 Reset Password", query: "I forgot my password" },
    { label: "🌐 Network Issue", query: "The network is not coming in my laptop" },
    { label: "🚨 Phishing Email", query: "I suspect this email is phishing" },
    { label: "💻 Dead Laptop 3.5y", query: "My laptop is 3.5 years old and completely dead" },
    { label: "🔒 Contractor VPN", query: "I'm a contractor and need VPN access" },
    { label: "📦 Non-Catalog Software", query: "Install software not in catalog" },
    { label: "🖥️ Screen Flickering", query: "My laptop screen is flickering" },
    { label: "💼 Remote Monitor", query: "I work from home 4 days and need a monitor" },
  ];

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (queryText) => {
    const text = queryText || input;
    if (!text || !text.trim() || loading) return;

    const userMsg = {
      id: 'user-' + Date.now(),
      sender: 'user',
      text: text.trim(),
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: text.trim() })
      });
      const data = await res.json();

      const aiMsg = {
        id: 'ai-' + Date.now(),
        sender: 'assistant',
        text: data.answer,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        result: data
      };
      setMessages(prev => [...prev, aiMsg]);
    } catch (err) {
      console.error('Chat error:', err);
      const errMsg = {
        id: 'err-' + Date.now(),
        sender: 'assistant',
        text: "Error communicating with decision engine. Please verify the backend server is operational.",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        result: null
      };
      setMessages(prev => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text, id) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const toggleTrace = (id) => {
    setExpandedTrace(prev => ({ ...prev, [id]: !prev[id] }));
  };

  return (
    <div className="flex flex-col h-[calc(100vh-145px)] max-w-5xl mx-auto">
      {/* Quick Prompts Bar */}
      <div className="mb-3">
        <div className="text-[11px] font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center gap-1.5">
          <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
          <span>Quick Benchmark Test Cases (Click to Test)</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {quickPrompts.map((p, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(p.query)}
              disabled={loading}
              className="text-xs px-3 py-1.5 rounded-lg bg-slate-900 border border-slate-700/70 hover:border-blue-500/60 hover:bg-slate-800 text-slate-300 hover:text-white transition-all duration-150 font-medium disabled:opacity-50"
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      {/* Chat Messages Container */}
      <div className="flex-1 bg-slate-900/90 border border-slate-800 rounded-2xl p-6 overflow-y-auto space-y-6 shadow-xl">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-3.5 ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            {msg.sender === 'assistant' && (
              <div className="w-8 h-8 rounded-xl bg-gradient-to-br from-blue-600 to-cyan-500 flex items-center justify-center flex-shrink-0 shadow-md">
                <Bot className="w-4 h-4 text-white" />
              </div>
            )}

            <div className={`max-w-2xl ${msg.sender === 'user' ? 'order-1' : 'order-2'}`}>
              {/* User Bubble */}
              {msg.sender === 'user' ? (
                <div className="bg-blue-600 text-white rounded-2xl rounded-tr-sm px-4 py-3 text-sm font-medium shadow-md">
                  {msg.text}
                </div>
              ) : (
                /* Assistant Bubble */
                <div className="space-y-3">
                  {/* Text Header */}
                  <div className="bg-slate-850 border border-slate-750 rounded-2xl rounded-tl-sm p-4 text-sm text-slate-100 shadow-md space-y-3">
                    <p className="leading-relaxed whitespace-pre-line">{msg.text}</p>

                    {/* Result Card if structured response */}
                    {msg.result && (
                      <div className="mt-3 pt-3 border-t border-slate-750 bg-slate-900/80 rounded-xl p-3.5 border border-slate-800 space-y-3 text-xs">
                        <div className="flex flex-wrap items-center justify-between gap-2 pb-2 border-b border-slate-800">
                          <div className="flex items-center gap-2">
                            <span className="text-slate-400 font-bold uppercase text-[10px]">Intent:</span>
                            <span className="font-semibold text-cyan-300 font-mono">{msg.result.intent}</span>
                          </div>
                          <div className="flex items-center gap-2">
                            <StatusBadge status={msg.result.status} />
                            <PriorityBadge priority={msg.result.priority} />
                          </div>
                        </div>

                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[11px]">
                          <div>
                            <span className="text-slate-400">Required Action: </span>
                            <span className="text-slate-200 font-medium">{msg.result.action}</span>
                          </div>
                          <div>
                            <span className="text-slate-400">Escalation Team: </span>
                            <span className="text-amber-400 font-semibold">{msg.result.escalation_team}</span>
                          </div>
                          <div>
                            <span className="text-slate-400">Source Policy: </span>
                            <span className="font-mono bg-blue-950 text-cyan-300 px-1.5 py-0.5 rounded border border-blue-900">
                              {msg.result.source}
                            </span>
                          </div>
                          <div>
                            <span className="text-slate-400">Generated Ticket: </span>
                            <span className="font-mono font-bold text-blue-400">
                              {msg.result.ticket_id}
                            </span>
                          </div>
                        </div>

                        {/* Actions bar for Assistant Answer */}
                        <div className="pt-2 border-t border-slate-800 flex items-center justify-between text-[11px]">
                          <button
                            onClick={() => toggleTrace(msg.id)}
                            className="text-cyan-400 hover:text-cyan-300 font-semibold flex items-center gap-1 transition-colors"
                          >
                            {expandedTrace[msg.id] ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
                            <span>{expandedTrace[msg.id] ? 'Hide' : 'Inspect'} Decision Trace JSON</span>
                          </button>

                          {setTraceQuery && (
                            <button
                              onClick={() => {
                                setTraceQuery(messages.find(m => m.sender === 'user')?.text || '');
                                setActivePage('trace');
                              }}
                              className="text-slate-400 hover:text-white flex items-center gap-1 transition-colors"
                            >
                              <span>Open in Observability</span>
                              <ExternalLink className="w-3 h-3" />
                            </button>
                          )}
                        </div>

                        {/* Collapsible Trace JSON */}
                        {expandedTrace[msg.id] && (
                          <div className="mt-2 p-3 bg-[#070A11] border border-slate-800 rounded-lg text-[11px] font-mono text-slate-300 overflow-x-auto relative">
                            <button
                              onClick={() => copyToClipboard(JSON.stringify(msg.result, null, 2), msg.id)}
                              className="absolute top-2 right-2 p-1.5 rounded bg-slate-800 text-slate-400 hover:text-white"
                              title="Copy JSON"
                            >
                              {copiedId === msg.id ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                            </button>
                            <pre>{JSON.stringify(msg.result, null, 2)}</pre>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}
              <span className="text-[10px] text-slate-400 px-1 mt-1 block">
                {msg.time}
              </span>
            </div>

            {msg.sender === 'user' && (
              <div className="w-8 h-8 rounded-xl bg-slate-800 border border-slate-700 flex items-center justify-center flex-shrink-0">
                <User className="w-4 h-4 text-slate-300" />
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div className="flex gap-3.5 justify-start items-center text-slate-400 text-xs">
            <div className="w-8 h-8 rounded-xl bg-blue-600 flex items-center justify-center animate-pulse">
              <Bot className="w-4 h-4 text-white" />
            </div>
            <div className="bg-slate-850 border border-slate-750 rounded-2xl px-4 py-2.5 flex items-center gap-2">
              <span className="w-3 h-3 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></span>
              <span>Evaluating Knowledge Base & Deterministic Rules...</span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Input Bar */}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          handleSend();
        }}
        className="mt-3 flex gap-2"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Describe your IT issue or question (e.g., 'The network is not coming in my laptop')..."
          className="flex-1 bg-slate-900 border border-slate-700/80 rounded-xl px-4 py-3 text-sm text-white placeholder-slate-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 shadow-inner"
        />
        <button
          type="submit"
          disabled={!input.trim() || loading}
          className="px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-500 text-white font-semibold text-sm flex items-center gap-2 shadow-lg shadow-blue-600/30 transition-all disabled:opacity-50"
        >
          <Send className="w-4 h-4" />
          <span>Send</span>
        </button>
      </form>
    </div>
  );
}
