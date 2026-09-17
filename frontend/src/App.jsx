import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import Chat from './pages/Chat';
import Requests from './pages/Requests';
import Tickets from './pages/Tickets';
import KnowledgeBase from './pages/KnowledgeBase';
import AuditTrail from './pages/AuditTrail';
import DecisionTrace from './pages/DecisionTrace';
import SystemControls from './pages/SystemControls';

export default function App() {
  const [activePage, setActivePage] = useState('dashboard');
  const [traceQuery, setTraceQuery] = useState('');
  const [refreshKey, setRefreshKey] = useState(0);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const handleRefresh = () => {
    setIsRefreshing(true);
    setRefreshKey(prev => prev + 1);
    setTimeout(() => setIsRefreshing(false), 600);
  };

  const getPageMeta = () => {
    switch (activePage) {
      case 'dashboard':
        return {
          title: 'Executive ITSM Operations & Compliance Dashboard',
          subtitle: 'Real-time telemetry on AI support requests, policy adherence, and ticket resolutions'
        };
      case 'chat':
        return {
          title: 'Veridian AI Support Assistant',
          subtitle: 'Grounded enterprise support assistant with strict deterministic policy enforcement'
        };
      case 'requests':
        return {
          title: 'Official Benchmark Support Requests (REQ-01 to REQ-15)',
          subtitle: 'Assignment dataset management, batch evaluation, and ticket synchronization'
        };
      case 'tickets':
        return {
          title: 'ITSM Service Management Ticket Queue',
          subtitle: 'Active support tickets, manager/finance approvals, and historical precedents'
        };
      case 'knowledge':
        return {
          title: 'Enterprise Knowledge Base & Policy Repository',
          subtitle: 'Source of truth: KB-01 to KB-10 and KB-ASSET-01 Asset Management Policy Extract'
        };
      case 'audit':
        return {
          title: 'Immutable Compliance Audit Trail',
          subtitle: 'End-to-end operational log of employee inputs, NLU extractions, and rule engine outcomes'
        };
      case 'trace':
        return {
          title: 'Agent Decision Trace & AI Observability',
          subtitle: 'Inspect the 5-step deterministic decision pipeline from query to ticket creation'
        };
      case 'controls':
        return {
          title: 'System Health & Administrative Governance',
          subtitle: 'Subsystem telemetry, database maintenance, and runtime state reset'
        };
      default:
        return {
          title: 'Veridian IT Assist',
          subtitle: 'Enterprise AI Support'
        };
    }
  };

  const meta = getPageMeta();

  return (
    <div className="flex min-h-screen bg-[#070A11] text-slate-100 font-sans">
      {/* Fixed Enterprise Sidebar */}
      <Sidebar 
        activePage={activePage} 
        setActivePage={setActivePage} 
        isOnline={true}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        <Header 
          title={meta.title}
          subtitle={meta.subtitle}
          onRefresh={handleRefresh}
          isRefreshing={isRefreshing}
        />

        <main className="flex-1 p-6 md:p-8 overflow-y-auto" key={refreshKey}>
          {activePage === 'dashboard' && <Dashboard setActivePage={setActivePage} />}
          {activePage === 'chat' && <Chat setActivePage={setActivePage} setTraceQuery={setTraceQuery} />}
          {activePage === 'requests' && <Requests setActivePage={setActivePage} setTraceQuery={setTraceQuery} />}
          {activePage === 'tickets' && <Tickets />}
          {activePage === 'knowledge' && <KnowledgeBase />}
          {activePage === 'audit' && <AuditTrail />}
          {activePage === 'trace' && <DecisionTrace initialQuery={traceQuery} />}
          {activePage === 'controls' && <SystemControls setActivePage={setActivePage} />}
        </main>
      </div>
    </div>
  );
}
