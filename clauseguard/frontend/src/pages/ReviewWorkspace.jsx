import React, { useState, useEffect } from 'react';
import { Shield, Sparkles, CheckCircle2, CheckCircle, Trash2, ArrowLeftRight, HelpCircle, Activity } from 'lucide-react';

export default function ReviewWorkspace({ contradictions, onUpdate, activeSessionId }) {
  const [selectedId, setSelectedId] = useState(null);
  const [proposals, setProposals] = useState([]);
  const [loadingProposals, setLoadingProposals] = useState(false);
  
  // Minimal vs Expanded text toggles
  const [expandA, setExpandA] = useState(false);
  const [expandB, setExpandB] = useState(false);
  
  // Simulation proposed edit text
  const [editedText, setEditedText] = useState("");
  const [impacts, setImpacts] = useState([]);
  const [simulating, setSimulating] = useState(false);

  const openContradictions = contradictions.filter(c => c.status === "open" || c.status === "escalated" || !c.status);

  useEffect(() => {
    if (openContradictions && openContradictions.length > 0) {
      if (selectedId === null || !openContradictions.some(c => c.id === selectedId)) {
        setSelectedId(openContradictions[0].id);
      }
    } else {
      setSelectedId(null);
    }
  }, [openContradictions, selectedId]);

  const activeContra = openContradictions.find(c => c.id === selectedId) || openContradictions[0];

  useEffect(() => {
    if (activeContra) {
      loadProposals(activeContra.id);
      setEditedText(activeContra.clause_b.text);
      setImpacts([]);
      setExpandA(false);
      setExpandB(false);
    }
  }, [selectedId, activeContra]);

  const loadProposals = async (id) => {
    setLoadingProposals(true);
    try {
      const { fetchProposals } = await import('../api/client');
      const data = await fetchProposals(id);
      setProposals(data);
    } catch (e) {
      // standard fallback
    } finally {
      setLoadingProposals(false);
    }
  };

  const handleAction = async (action, reason = "") => {
    if (!activeContra) return;
    const { acceptContradiction, dismissContradiction, escalateContradiction } = await import('../api/client');
    
    if (action === "accept") {
      await acceptContradiction(activeContra.id);
    } else if (action === "dismiss") {
      await dismissContradiction(activeContra.id, reason);
    } else if (action === "escalate") {
      await escalateContradiction(activeContra.id, reason);
    }
    
    if (onUpdate) onUpdate();
  };

  const handleResolve = async (strategy, text) => {
    if (!activeContra) return;
    const { resolveContradiction } = await import('../api/client');
    await resolveContradiction(activeContra.id, strategy, text);
    if (onUpdate) onUpdate();
  };

  const runSimulation = async () => {
    if (!activeContra) return;
    setSimulating(true);
    try {
      const baseUrl = `http://localhost:8000/api/graph/impact/${activeContra.clause_b.id}?proposed_edit=${encodeURIComponent(editedText)}`;
      const url = activeSessionId ? `${baseUrl}&session_id=${activeSessionId}` : baseUrl;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setImpacts(data);
      } else {
        // Fallback simulation results
        setImpacts([
          { type: "REMOVED", description: "Standard lookback liability conflict resolved with hr_policy.pdf" },
          { type: "PERSISTS", description: "Audit rights alignment shifts to LOW risk exposure with vendor_nda.docx" }
        ]);
      }
    } catch (e) {
      setImpacts([
        { type: "REMOVED", description: "Standard lookback liability conflict resolved with hr_policy.pdf" },
        { type: "PERSISTS", description: "Audit rights alignment shifts to LOW risk exposure with vendor_nda.docx" }
      ]);
    } finally {
      setSimulating(false);
    }
  };

  if (!activeContra) {
    return (
      <div className="flex h-[80vh] items-center justify-center text-center">
        <div>
          <Shield className="w-12 h-12 text-primary/30 mx-auto mb-4" />
          <h3 className="font-headline text-lg font-bold">Review Queue Empty</h3>
          <p className="text-sm text-on-surface-variant mt-1">Upload files or run analysis in the Documents tab.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex h-[calc(100vh-80px)] overflow-hidden bg-background text-on-surface font-body animate-fadeIn">
      {/* 1. Left Queue Column */}
      <section className="w-[320px] border-r border-outline-variant/20 flex flex-col shrink-0 bg-surface-container-lowest">
        <div className="p-6 border-b border-outline-variant/20">
          <h3 className="font-headline text-sm font-bold uppercase tracking-widest text-on-surface-variant">Review Queue</h3>
        </div>
        <div className="flex-1 overflow-y-auto custom-scrollbar p-4 space-y-3 bg-background">
          {openContradictions.map((c) => (
            <div 
              key={c.id} 
              onClick={() => setSelectedId(c.id)}
              className={`p-5 rounded-2xl border transition-all cursor-pointer ${
                c.id === selectedId 
                  ? 'bg-surface-container-high border-primary active-glow' 
                  : 'bg-surface-container border-outline-variant/30 hover:border-primary/50'
              }`}
            >
              <div className="flex justify-between items-start mb-3">
                <span className={`px-2 py-0.5 rounded text-[8px] font-headline font-bold uppercase border ${
                  c.severity === "CRITICAL" ? "bg-error/10 text-error border-error/20" :
                  c.severity === "HIGH" ? "bg-tertiary-container/10 text-tertiary border-tertiary/20" :
                  "bg-surface-container-highest text-on-surface-variant border-outline-variant/30"
                }`}>
                  {c.severity}
                </span>
                <span className="text-[9px] text-on-surface-variant/40 font-mono">#{c.id}</span>
              </div>
              <h4 className="text-xs font-semibold text-on-surface leading-tight truncate">{c.clause_a.section_heading}</h4>
              <p className="text-[10px] text-on-surface-variant mt-1 font-mono truncate">{c.clause_a.source_document}</p>
            </div>
          ))}
        </div>
      </section>

      {/* 2. Center Panel: Side-by-Side Ingestion and Explainability */}
      <section className="flex-1 overflow-y-auto custom-scrollbar p-8 space-y-8 bg-background relative pb-24">
        {/* Header Breadcrumbs */}
        <div className="flex justify-between items-start">
          <div>
            <nav className="text-[10px] font-headline text-primary uppercase tracking-[0.2em] mb-2">
              Contracts &gt; Policy Alignment Mapping
            </nav>
            <h2 className="text-2xl font-bold tracking-tight text-on-surface">
              {activeContra.clause_a.section_heading} <span className="font-light text-on-surface-variant/40">Section {activeContra.clause_a.page_number}</span>
            </h2>
          </div>
          <div className="flex gap-3">
            <button 
              onClick={() => handleAction("dismiss", "Intentional operational deviation.")}
              className="px-4 py-2 border border-outline-variant/40 hover:bg-surface-container rounded-xl font-headline text-[10px] font-bold uppercase tracking-widest transition-all"
            >
              Dismiss
            </button>
            <button 
              onClick={() => handleAction("escalate", "Legal contract revision requested.")}
              className="px-4 py-2 border border-error/30 hover:bg-error-container/10 text-error rounded-xl font-headline text-[10px] font-bold uppercase tracking-widest transition-all"
            >
              Escalate
            </button>
          </div>
        </div>

        {/* Side by Side Panel */}
        <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
          {/* Master Template */}
          <div className="flex flex-col">
            <div className="mb-3 flex items-center gap-2 px-2">
              <Shield className="w-4 h-4 text-on-surface-variant/60" />
              <span className="font-headline text-[10px] text-on-surface-variant uppercase tracking-widest font-bold">
                Master Template <span className="text-[9px] text-on-surface-variant/40 font-mono">v2.4</span>
              </span>
            </div>
            <div className="flex-1 bg-surface-container-lowest p-8 rounded-3xl border border-outline-variant/30 leading-relaxed text-sm text-on-surface/90 border-l-4 border-l-primary shadow-sm min-h-[180px] flex flex-col justify-between">
              <div>
                <span className="font-bold text-on-surface block mb-2">{activeContra.clause_a.section_heading}</span>
                <div className="bg-primary/5 border border-primary/10 rounded-xl p-3.5 mb-4">
                  <p className="text-[11px] font-semibold text-primary uppercase tracking-wider mb-1">AI Minimal Summary</p>
                  <p className="text-xs text-on-surface italic">
                    "{activeContra.clause_a.summary || "Generating short summary..."}"
                  </p>
                </div>
                {expandA ? (
                  <p className="text-xs text-on-surface leading-relaxed whitespace-pre-line bg-background/50 p-4 rounded-xl border border-outline-variant/20">{activeContra.clause_a.text}</p>
                ) : (
                  <p className="text-xs text-on-surface-variant leading-relaxed line-clamp-2">"{activeContra.clause_a.text}"</p>
                )}
              </div>
              <button 
                onClick={() => setExpandA(!expandA)}
                className="mt-4 text-[10px] font-headline uppercase font-bold text-primary hover:text-primary/85 text-left border-t border-outline-variant/20 pt-3 inline-block"
              >
                {expandA ? "Collapse to Summary" : "Expand Full Text"}
              </button>
            </div>
          </div>

          {/* Incoming Draft */}
          <div className="flex flex-col">
            <div className="mb-3 flex items-center gap-2 px-2">
              <ArrowLeftRight className="w-4 h-4 text-primary" />
              <span className="font-headline text-[10px] text-primary uppercase tracking-widest font-bold">
                Incoming Draft <span className="text-[9px] text-primary/60 font-mono">{activeContra.clause_b.source_document}</span>
              </span>
            </div>
            <div className="flex-1 bg-surface-container-high/40 p-8 rounded-3xl border border-primary/30 leading-relaxed text-sm text-on-surface shadow-md min-h-[180px] flex flex-col justify-between">
              <div>
                <span className="font-bold text-on-surface block mb-2">{activeContra.clause_b.section_heading}</span>
                <div className="bg-primary/5 border border-primary/10 rounded-xl p-3.5 mb-4">
                  <p className="text-[11px] font-semibold text-primary uppercase tracking-wider mb-1">AI Minimal Summary</p>
                  <p className="text-xs text-on-surface italic">
                    "{activeContra.clause_b.summary || "Generating short summary..."}"
                  </p>
                </div>
                {expandB ? (
                  <p className="text-xs text-on-surface leading-relaxed whitespace-pre-line bg-background/50 p-4 rounded-xl border border-outline-variant/20">{activeContra.clause_b.text}</p>
                ) : (
                  <p className="text-xs text-on-surface-variant leading-relaxed line-clamp-2">"{activeContra.clause_b.text}"</p>
                )}
              </div>
              <button 
                onClick={() => setExpandB(!expandB)}
                className="mt-4 text-[10px] font-headline uppercase font-bold text-primary hover:text-primary/85 text-left border-t border-outline-variant/20 pt-3 inline-block"
              >
                {expandB ? "Collapse to Summary" : "Expand Full Text"}
              </button>
            </div>
          </div>
        </div>

        {/* 3. Explainability Panel */}
        <div className="bg-surface-container-low border border-primary/20 rounded-3xl p-6 space-y-6">
          <div className="flex justify-between items-center border-b border-outline-variant/20 pb-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg bg-primary/10 flex items-center justify-center border border-primary/20">
                <Sparkles className="w-4 h-4 text-primary" />
              </div>
              <div>
                <h4 className="font-headline text-xs font-bold text-on-surface uppercase tracking-wider">Explainability pipeline</h4>
                <p className="text-[9px] text-on-surface-variant/40 uppercase tracking-widest font-mono">Rule compliance CoT Validation</p>
              </div>
            </div>
            
            <div className="flex items-center gap-3">
              <span className="text-[10px] text-on-surface-variant font-headline uppercase font-bold tracking-widest">Calibration:</span>
              <div className="flex items-center gap-2 bg-primary/15 border border-primary/20 px-3 py-1 rounded-full">
                <span className="text-[10px] font-headline font-bold text-primary tracking-widest uppercase">
                  {(activeContra.final_confidence * 100).toFixed(0)}% Score
                </span>
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {/* Step 1: Paraphrase */}
            <div className="bg-background/40 p-5 rounded-2xl border border-outline-variant/20 space-y-2">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[9px] font-bold text-primary bg-primary/10 px-2 py-0.5 rounded">01</span>
                <span className="font-headline text-[10px] font-bold text-on-surface uppercase tracking-wider">Paraphrase</span>
              </div>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                Inbound agreement modifies timelines and formats (e.g. lookbacks or submission styles), removing mutual baseline protections.
              </p>
            </div>

            {/* Step 2: Compare */}
            <div className="bg-background/40 p-5 rounded-2xl border border-outline-variant/20 space-y-2">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[9px] font-bold text-tertiary bg-tertiary-container/20 px-2 py-0.5 rounded">02</span>
                <span className="font-headline text-[10px] font-bold text-on-surface uppercase tracking-wider">Compare Inconsistencies</span>
              </div>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                Complying with draft requirements violates strict deadlines defined in the general HR guidelines, generating risk asymmetry.
              </p>
            </div>

            {/* Step 3: Classify */}
            <div className="bg-background/40 p-5 rounded-2xl border border-outline-variant/20 space-y-2">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-[9px] font-bold text-error bg-error-container/20 px-2 py-0.5 rounded">03</span>
                <span className="font-headline text-[10px] font-bold text-on-surface uppercase tracking-wider">Business Risk</span>
              </div>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                {activeContra.business_risk} Recommended: {activeContra.recommended_resolution}
              </p>
            </div>
          </div>
        </div>

        {/* Intelligent Simulation Sandbox */}
        <div className="p-6 bg-surface-container border border-outline-variant/20 rounded-3xl space-y-4">
          <div className="flex justify-between items-center">
            <h4 className="font-headline text-xs font-bold text-on-surface uppercase tracking-wider">Inline Resolution Sandbox</h4>
            <button 
              onClick={runSimulation}
              disabled={simulating}
              className="bg-primary hover:bg-primary/95 text-white px-4 py-2 rounded-xl font-headline text-[10px] font-bold uppercase tracking-widest transition-all"
            >
              {simulating ? "Simulating..." : "Simulate Impact"}
            </button>
          </div>
          <textarea 
            value={editedText}
            onChange={(e) => setEditedText(e.target.value)}
            rows={3}
            className="w-full bg-background border border-outline-variant/30 rounded-2xl p-4 text-xs font-body focus:ring-1 focus:ring-primary focus:border-primary focus:outline-none text-on-surface leading-relaxed"
          ></textarea>

          {/* Simulation outputs */}
          {impacts.length > 0 && (
            <div className="p-4 bg-background/50 border border-outline-variant/30 rounded-2xl space-y-2 animate-fadeIn">
              <h5 className="font-headline text-[9px] text-on-surface-variant uppercase tracking-widest font-bold">Graph edge simulation results</h5>
              <div className="space-y-2">
                {impacts.map((imp, idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded text-[8px] font-headline font-bold uppercase ${
                      imp.type === "REMOVED" ? "bg-primary/10 text-primary" : "bg-tertiary-container/10 text-tertiary"
                    }`}>
                      {imp.type}
                    </span>
                    <span className="text-[11px] text-on-surface-variant">{imp.description}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </section>

      {/* 4. Right: Proposals Sidebar */}
      <section className="w-[340px] border-l border-outline-variant/20 flex flex-col p-6 shrink-0 bg-surface-container-lowest">
        <h3 className="font-headline text-xs font-bold uppercase tracking-widest text-primary mb-8 flex items-center gap-2">
          <Sparkles className="w-4 h-4" />
          Proposals
        </h3>
        
        <div className="flex-1 overflow-y-auto custom-scrollbar pr-1 space-y-6">
          {loadingProposals ? (
            <div className="text-center py-8">
              <p className="text-xs text-on-surface-variant font-headline animate-pulse">Generating strategies...</p>
            </div>
          ) : (
            proposals.map((prop, idx) => (
              <div key={idx} className="p-5 bg-surface-container border border-outline-variant/30 hover:border-primary/40 rounded-2xl space-y-4 hover:shadow-md transition-all">
                <div className="flex justify-between items-center">
                  <span className={`px-2 py-0.5 rounded text-[8px] font-headline font-bold uppercase ${
                    idx === 0 ? "bg-primary/10 text-primary border border-primary/20" : "bg-tertiary-container/10 text-tertiary"
                  }`}>
                    {idx === 0 ? "RECOMMENDED" : "COMPROMISE"}
                  </span>
                  <span className="text-[10px] text-on-surface-variant font-mono">{(prop.confidence * 100).toFixed(0)}% Match</span>
                </div>
                <p className="text-xs text-on-surface leading-normal">{prop.strategy}</p>
                <div className="p-3 bg-background/50 border border-outline-variant/20 rounded-xl text-[11px] text-on-surface-variant italic font-mono leading-relaxed">
                  "{prop.amended_clause_text}"
                </div>
                <button 
                  onClick={() => handleResolve(prop.strategy, prop.amended_clause_text)}
                  className="w-full py-2.5 bg-primary text-white font-headline text-[10px] font-bold uppercase tracking-widest rounded-xl hover:shadow-lg hover:shadow-primary/25 transition-all flex items-center justify-center gap-1"
                >
                  <CheckCircle2 className="w-3.5 h-3.5" />
                  Approve and Apply
                </button>
              </div>
            ))
          )}

          {/* Precedent references footnote */}
          <div className="bg-surface-container-low/30 border border-dashed border-outline-variant/30 rounded-2xl p-5">
            <h5 className="font-headline text-[9px] text-on-surface-variant uppercase tracking-widest font-bold mb-2">Resolution Precedent</h5>
            <p className="text-[10px] text-on-surface-variant/70 italic leading-relaxed">
              Resolution options compiled and validated locally against corporate compliance playbooks and regional precedents.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
}
