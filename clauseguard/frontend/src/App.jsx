import React, { useState, useEffect } from 'react';
import { LayoutDashboard, FileText, BarChart2, ShieldAlert, GitFork, Cpu, Settings as SettingsIcon, Bell, Terminal, CheckCircle } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import Documents from './pages/Documents';
import Analysis from './pages/Analysis';
import ReviewWorkspace from './pages/ReviewWorkspace';
import KnowledgeGraph from './pages/KnowledgeGraph';
import EdgeNode from './pages/EdgeNode';
import Settings from './pages/Settings';

function ShareReportModal({ sessionId, onClose }) {
  const [email, setEmail] = useState("general.counsel@company.corp");
  const [channel, setChannel] = useState("Email");
  const [report, setReport] = useState("");
  const [loading, setLoading] = useState(false);
  const [sharing, setSharing] = useState(false);
  const [shareSuccess, setShareSuccess] = useState(false);

  useEffect(() => {
    const loadPreview = async () => {
      setLoading(true);
      try {
        const { shareReport } = await import('./api/client');
        const res = await shareReport(sessionId, email, channel);
        setReport(res.report || "");
      } catch (e) {
        setReport("Error generating report preview.");
      } finally {
        setLoading(false);
      }
    };
    loadPreview();
  }, [sessionId, channel]);

  const handleShareSubmit = async (e) => {
    e.preventDefault();
    setSharing(true);
    try {
      const { shareReport } = await import('./api/client');
      await shareReport(sessionId, email, channel);
      setShareSuccess(true);
      setTimeout(() => {
        onClose();
      }, 2000);
    } catch (err) {
      console.error(err);
    } finally {
      setSharing(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center">
      <div className="bg-surface-container border border-outline-variant/30 rounded-3xl p-8 max-w-2xl w-full mx-4 shadow-2xl relative animate-fadeIn flex flex-col max-h-[85vh]">
        <div className="flex justify-between items-start mb-6">
          <div>
            <h3 className="font-headline text-lg font-bold text-on-surface">Share Compliance Report</h3>
            <p className="text-xs text-on-surface-variant mt-1">Send a compiled inconsistency analysis report to officials.</p>
          </div>
          <button 
            onClick={onClose} 
            className="text-on-surface-variant hover:text-on-surface text-sm font-headline font-bold uppercase tracking-wider px-2.5 py-1.5 rounded-lg border border-outline-variant/20 hover:bg-surface-container-high transition-all"
          >
            Close
          </button>
        </div>

        {shareSuccess ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center py-12 space-y-4">
            <div className="w-16 h-16 bg-primary/10 border border-primary/20 rounded-full flex items-center justify-center text-primary animate-bounce">
              <CheckCircle className="w-8 h-8" />
            </div>
            <h4 className="font-headline text-md font-bold text-on-surface">Report Dispatched Successfully!</h4>
            <p className="text-xs text-on-surface-variant max-w-xs leading-relaxed">
              Compliance report has been generated and sent to <span className="text-primary font-semibold">{email}</span> via {channel}.
            </p>
          </div>
        ) : (
          <form onSubmit={handleShareSubmit} className="flex-1 flex flex-col overflow-hidden">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
              <div>
                <label className="block text-[10px] uppercase font-headline tracking-wider text-on-surface-variant mb-2">Recipient Email</label>
                <input 
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full bg-background border border-outline-variant/40 rounded-xl px-4 py-2.5 text-xs text-on-surface focus:outline-none focus:border-primary"
                  placeholder="e.g. counsel@corp.com"
                />
              </div>
              <div>
                <label className="block text-[10px] uppercase font-headline tracking-wider text-on-surface-variant mb-2">Dispatch Channel</label>
                <select
                  value={channel}
                  onChange={(e) => setChannel(e.target.value)}
                  className="w-full bg-background border border-outline-variant/40 rounded-xl px-4 py-2.5 text-xs text-on-surface focus:outline-none focus:border-primary"
                >
                  <option value="Email">Email Channel</option>
                  <option value="Slack">Slack Webhook Link</option>
                  <option value="Teams">Microsoft Teams Hook</option>
                  <option value="Audit Vault">Secure Audit Vault</option>
                </select>
              </div>
            </div>

            <label className="block text-[10px] uppercase font-headline tracking-wider text-on-surface-variant mb-2">Report Markdown Preview</label>
            <div className="flex-1 bg-background border border-outline-variant/20 rounded-2xl p-4 font-mono text-xs overflow-y-auto max-h-[40vh] custom-scrollbar text-on-surface-variant whitespace-pre-wrap select-text leading-relaxed">
              {loading ? (
                <div className="flex items-center justify-center h-32 text-primary animate-pulse font-headline">
                  Compiling markdown data...
                </div>
              ) : (
                report || "No records generated."
              )}
            </div>

            <div className="mt-6 flex justify-end gap-3 pt-4 border-t border-outline-variant/20">
              <button 
                type="button" 
                onClick={onClose}
                className="px-5 py-2.5 rounded-xl border border-outline-variant/30 hover:bg-surface-container-high text-xs font-headline font-bold uppercase tracking-wider transition-all"
              >
                Cancel
              </button>
              <button 
                type="submit" 
                disabled={sharing || loading}
                className="bg-primary hover:bg-primary/90 text-white px-6 py-2.5 rounded-xl text-xs font-headline font-bold uppercase tracking-widest disabled:opacity-50 transition-all flex items-center gap-2"
              >
                {sharing ? "Sending..." : "Confirm & Send"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}

export default function App() {
  const [activeTab, setActiveTab] = useState("Dashboard");
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('theme') || 'dark';
  });

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }, [theme]);

  const [kpis, setKpis] = useState({
    financial_risk_prevented: 0.0,
    review_time_saved_pct: 94.0,
    compliance_score: 98.2,
    false_positive_rate: 0.0,
    model_accuracy: 94.7,
    active_profile: "RPI5 (Balanced Edge)",
    primary_model: "llama3.1:8b-q4",
    fallback_active: false
  });
  const [telemetry, setTelemetry] = useState({
    cpu_pct: 0,
    ram_pct: 0,
    temperature_c: 42.0,
    current_tps: 28.4,
    active_model: "llama3.1:8b-q4",
    fallback_model: "qwen2.5:3b",
    profile_name: "RPI5 (Balanced Edge)",
    fallback_active: false,
    hardware_integrity: { nvme: "Verified", ethernet: "1.0 Gbps", power: "5.1V" },
    deployed_models: []
  });
  const [contradictions, setContradictions] = useState([]);
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(() => {
    return localStorage.getItem('activeSessionId') || '';
  });
  const [showShareModal, setShowShareModal] = useState(false);

  const loadSessionsList = async () => {
    try {
      const { fetchSessions } = await import('./api/client');
      const list = await fetchSessions();
      setSessions(list);
      return list;
    } catch (e) {
      return [];
    }
  };

  const loadData = async (sid = activeSessionId) => {
    try {
      const { fetchKPIs, fetchTelemetry, fetchContradictions } = await import('./api/client');
      const kpiData = await fetchKPIs(sid);
      const teleData = await fetchTelemetry(sid);
      const contraData = await fetchContradictions(sid);
      
      setKpis(kpiData);
      setTelemetry(teleData);
      setContradictions(contraData);
    } catch (e) {
      // fallback
    }
  };

  useEffect(() => {
    const init = async () => {
      const list = await loadSessionsList();
      let active = localStorage.getItem('activeSessionId');
      if (!active || !list.includes(active)) {
        active = list.length > 0 ? list[0] : `session-${Date.now().toString().slice(-4)}`;
      }
      setActiveSessionId(active);
      loadData(active);
    };
    init();
  }, []);

  useEffect(() => {
    if (!activeSessionId) return;
    localStorage.setItem('activeSessionId', activeSessionId);
    loadData(activeSessionId);
    
    const interval = setInterval(() => loadData(activeSessionId), 4000);
    
    // Connect WebSocket
    let socket;
    try {
      socket = new WebSocket("ws://localhost:8000/api/ws");
      socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("WebSocket event: ", data);
        if (data.event === "MODEL_SWITCHED" || data.event === "MODEL_RESTORED") {
          loadData(activeSessionId); // Force refresh metrics
        }
      };
    } catch (err) {
      console.log("WebSocket connection skipped in offline mode.");
    }
    
    return () => {
      clearInterval(interval);
      if (socket) socket.close();
    };
  }, [activeSessionId]);

  const handleSessionChange = (sid) => {
    setActiveSessionId(sid);
  };

  const handleNewSession = () => {
    const newId = `session-${Date.now().toString().slice(-4)}`;
    setActiveSessionId(newId);
    setContradictions([]);
    setKpis(prev => ({
      ...prev,
      financial_risk_prevented: 0.0,
      compliance_score: 100.0,
      false_positive_rate: 0.0,
    }));
    if (!sessions.includes(newId)) {
      setSessions([...sessions, newId]);
    }
  };

  const handleDeleteSession = async () => {
    if (!activeSessionId) return;
    if (!window.confirm(`Are you sure you want to delete session "${activeSessionId}"? This will permanently wipe all uploaded documents and resolved conflicts in this session.`)) {
      return;
    }
    try {
      const { deleteSession } = await import('./api/client');
      await deleteSession(activeSessionId);
      const updatedList = await loadSessionsList();
      const nextActive = updatedList.length > 0 ? updatedList[0] : `session-${Date.now().toString().slice(-4)}`;
      setActiveSessionId(nextActive);
    } catch (e) {
      console.error("Failed to delete session", e);
    }
  };

  const renderContent = () => {
    switch (activeTab) {
      case "Dashboard":
        return <Dashboard kpis={kpis} telemetry={telemetry} contradictions={contradictions} onUploadSuccess={() => { loadSessionsList(); loadData(activeSessionId); }} navigateToTab={setActiveTab} activeSessionId={activeSessionId} />;
      case "Documents":
        return <Documents navigateToTab={setActiveTab} activeSessionId={activeSessionId} onUploadSuccess={() => { loadSessionsList(); loadData(activeSessionId); }} />;
      case "Analysis":
        return <Analysis navigateToTab={setActiveTab} activeSessionId={activeSessionId} />;
      case "Workspace":
        return <ReviewWorkspace contradictions={contradictions} onUpdate={() => loadData(activeSessionId)} activeSessionId={activeSessionId} />;
      case "Graph":
        return <KnowledgeGraph activeSessionId={activeSessionId} />;
      case "EdgeNode":
        return <EdgeNode />;
      case "Settings":
        return <Settings theme={theme} setTheme={setTheme} />;
      default:
        return <Dashboard kpis={kpis} telemetry={telemetry} contradictions={contradictions} onUploadSuccess={() => { loadSessionsList(); loadData(activeSessionId); }} navigateToTab={setActiveTab} activeSessionId={activeSessionId} />;
    }
  };

  return (
    <div className="flex h-screen bg-background text-on-surface overflow-hidden select-none">
      {/* 1. Global Navigation Sidebar */}
      <aside className="w-[260px] border-r border-outline-variant/30 bg-surface flex flex-col py-8 z-40 shrink-0">
        <div className="px-8 mb-12 flex items-center gap-3">
          <div className="w-8 h-8 bg-primary rounded flex items-center justify-center text-white shrink-0">
            <ShieldAlert className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="font-headline text-lg font-bold text-primary leading-none">ClauseGuard</h1>
            <p className="text-[9px] uppercase tracking-widest text-on-surface-variant font-headline mt-1.5 opacity-60">Governance v4.0</p>
          </div>
        </div>

        <nav className="flex-1 px-4 space-y-1">
          {[
            { name: "Dashboard", icon: LayoutDashboard },
            { name: "Documents", icon: FileText },
            { name: "Analysis", icon: BarChart2 },
            { name: "Workspace", icon: ShieldAlert },
            { name: "Graph", icon: GitFork },
            { name: "EdgeNode", icon: Cpu },
            { name: "Settings", icon: SettingsIcon }
          ].map((tab) => {
            const Icon = tab.icon;
            const isActive = activeTab === tab.name;
            return (
              <button
                key={tab.name}
                onClick={() => setActiveTab(tab.name)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
                  isActive 
                    ? "bg-primary text-white font-headline font-bold text-xs uppercase border border-primary/20 shadow-md shadow-primary/10" 
                    : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container/50 text-xs font-headline uppercase font-semibold"
                }`}
              >
                <Icon className={`w-4 h-4 shrink-0 ${isActive ? "text-white" : "text-on-surface-variant"}`} />
                <span>{tab.name === "Workspace" ? "Review Workspace" : tab.name === "Graph" ? "Knowledge Graph" : tab.name === "EdgeNode" ? "Edge Node" : tab.name}</span>
              </button>
            );
          })}
        </nav>

        <div className="px-6 mt-auto">
          <div className="p-4 rounded-2xl border border-outline-variant/30 bg-surface-container-low flex items-center gap-3">
            <span className="flex h-2 w-2 rounded-full bg-primary animate-pulse"></span>
            <span className="text-[10px] font-headline font-bold uppercase tracking-widest text-on-surface-variant">RPi5: Active</span>
          </div>
        </div>
      </aside>

      {/* 2. Main Content Wrapper */}
      <div className="flex-1 flex flex-col overflow-hidden bg-background">
        {/* Header toolbar */}
        <header className="h-16 border-b border-outline-variant/20 flex items-center justify-between px-8 bg-surface/80 backdrop-blur-md shrink-0 z-30">
          <div className="flex items-center gap-3 flex-wrap">
            <span className="text-[10px] uppercase font-headline tracking-wider text-on-surface-variant/85 font-bold">Active Session:</span>
            <select
              value={activeSessionId}
              onChange={(e) => handleSessionChange(e.target.value)}
              className="bg-surface-container-high border border-outline-variant/30 rounded-xl px-3 py-1.5 text-xs text-on-surface font-semibold focus:outline-none focus:border-primary hover:border-primary/50 cursor-pointer transition-colors"
            >
              {sessions.map(s => (
                <option key={s} value={s}>{s}</option>
              ))}
              {!sessions.includes(activeSessionId) && activeSessionId && (
                <option value={activeSessionId}>{activeSessionId}</option>
              )}
            </select>
            <button
              onClick={handleNewSession}
              className="bg-primary/10 hover:bg-primary/20 text-primary border border-primary/20 text-[10px] font-headline font-bold uppercase tracking-wider px-3.5 py-1.5 rounded-xl transition-all"
              title="Start a new ingestion session"
            >
              + New Session
            </button>
            <button
              onClick={handleDeleteSession}
              className="border border-error/20 hover:bg-error/10 text-error text-[10px] font-headline font-bold uppercase tracking-wider px-3.5 py-1.5 rounded-xl transition-all"
              title="Delete current session and vectors"
            >
              Delete Session
            </button>
            <button
              onClick={() => setShowShareModal(true)}
              className="border border-outline-variant/40 hover:bg-surface-container text-on-surface-variant hover:text-on-surface text-[10px] font-headline font-bold uppercase tracking-wider px-3.5 py-1.5 rounded-xl transition-all"
              title="Share report with officials"
            >
              Share Report
            </button>
          </div>
          
          <div className="flex items-center gap-4">
            <button className="p-2 hover:bg-surface-container rounded-lg text-on-surface-variant hover:text-primary transition-colors">
              <Bell className="w-4 h-4" />
            </button>
            <div className="h-4 w-px bg-outline-variant/30"></div>
            <div className="flex items-center gap-3">
              <div className="text-right">
                <p className="text-xs font-semibold text-on-surface">Cambridge Admin</p>
                <p className="text-[9px] text-on-surface-variant uppercase font-headline">Compliance Portal</p>
              </div>
              <div className="w-8 h-8 rounded-full bg-surface-container border border-outline-variant/30 flex items-center justify-center font-bold text-xs text-primary">
                C
              </div>
            </div>
          </div>
        </header>

        {/* Scrollable Canvas Section */}
        <main className="flex-1 overflow-y-auto custom-scrollbar p-8 bg-background">
          {renderContent()}
        </main>
      </div>

      {showShareModal && (
        <ShareReportModal 
          sessionId={activeSessionId} 
          onClose={() => setShowShareModal(false)} 
        />
      )}
    </div>
  );
}
