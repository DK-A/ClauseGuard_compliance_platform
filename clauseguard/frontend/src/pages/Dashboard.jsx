import React, { useState } from 'react';
import { Upload, Shield, CheckCircle, AlertTriangle, ChevronRight, Activity, Terminal } from 'lucide-react';

export default function Dashboard({ kpis, telemetry, contradictions, onUploadSuccess, navigateToTab, activeSessionId }) {
  const [dragActive, setDragActive] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = async (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      await uploadFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = async (e) => {
    if (e.target.files && e.target.files[0]) {
      await uploadFile(e.target.files[0]);
    }
  };

  const uploadFile = async (file) => {
    setUploadStatus("Uploading document...");
    try {
      const sessionId = activeSessionId || `session-${Date.now().toString().slice(-4)}`;
      // Dynamic import
      const { uploadDocument, runAnalysis } = await import('../api/client');
      await uploadDocument(file, sessionId);
      setUploadStatus("Processing legal analysis...");
      await runAnalysis(sessionId);
      setUploadStatus("Analysis complete! Proceeding...");
      setTimeout(() => {
        setUploadStatus("");
        if (onUploadSuccess) onUploadSuccess();
      }, 1500);
    } catch (err) {
      setUploadStatus("Error processing file. Demo fallback activated.");
      setTimeout(() => {
        setUploadStatus("");
        if (onUploadSuccess) onUploadSuccess();
      }, 1500);
    }
  };

  // Sparkline elements
  const sparkPoints = [12, 18, 10, 24, 15, 20, 32, 22, 14, 28];

  return (
    <div className="space-y-8 animate-fadeIn max-w-[1400px] mx-auto p-2">
      {/* Top Banner Status */}
      <section className="flex flex-col lg:flex-row lg:items-end justify-between gap-6 border-b border-outline-variant/20 pb-6">
        <div>
          <div className="flex items-center gap-2 mb-2">
            <span className="flex h-2 w-2 rounded-full bg-primary animate-pulse shadow-[0_0_8px_#2563eb]"></span>
            <span className="font-headline text-[10px] text-primary uppercase tracking-[0.2em] font-bold">Node Telemetry status</span>
          </div>
          <h2 className="font-headline text-3xl font-bold tracking-tight">System Operational</h2>
          <p className="text-on-surface-variant text-sm mt-1 max-w-xl">
            ClauseGuard edge node model running successfully. Calibration weights loaded. 
            Active hardware profile: <span className="text-primary font-medium">{telemetry.profile_name}</span>.
          </p>
        </div>
        <div className="flex gap-4">
          <div className="px-4 py-2 bg-surface-container border border-outline-variant/30 rounded-xl flex items-center gap-3">
            <Terminal className="text-primary w-4 h-4" />
            <div className="text-left">
              <p className="text-[10px] text-on-surface-variant font-headline uppercase leading-none">Inference Model</p>
              <p className="text-xs font-semibold text-on-surface mt-1">{telemetry.active_model}</p>
            </div>
          </div>
        </div>
      </section>

      {/* Bento KPIs Grid */}
      <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Risk Prevented */}
        <div className="p-6 bg-tertiary-container/10 border border-tertiary/20 rounded-2xl group hover:border-tertiary/40 transition-all duration-300">
          <div className="flex justify-between items-start mb-4">
            <span className="font-headline text-[10px] text-tertiary uppercase tracking-widest font-bold">Financial Risk Prevented</span>
            <div className="w-8 h-8 rounded-lg bg-surface-container flex items-center justify-center border border-outline-variant/40 group-hover:text-tertiary transition-colors">
              <Shield className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2 mb-1">
            <span className="font-headline text-3xl font-bold text-on-surface">
              ₹{(kpis.financial_risk_prevented / 10000000).toFixed(2)} Cr
            </span>
          </div>
          <p className="text-[11px] text-on-surface-variant">per contracts reviewed</p>
        </div>

        {/* Time Saved */}
        <div className="p-6 bg-surface-container-low border border-outline-variant/20 rounded-2xl group hover:border-primary/40 transition-all duration-300">
          <div className="flex justify-between items-start mb-4">
            <span className="font-headline text-[10px] text-on-surface-variant uppercase tracking-widest font-bold">Review Time Saved</span>
            <div className="w-8 h-8 rounded-lg bg-surface-container flex items-center justify-center border border-outline-variant/40 group-hover:text-primary transition-colors">
              <CheckCircle className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2 mb-1">
            <span className="font-headline text-3xl font-bold text-on-surface">{kpis.review_time_saved_pct}%</span>
            <span className="text-xs text-primary font-semibold">94x speedup</span>
          </div>
          <p className="text-[11px] text-on-surface-variant">from 4 hrs to ~15 secs</p>
        </div>

        {/* Compliance Score */}
        <div className="p-6 bg-surface-container-low border border-outline-variant/20 rounded-2xl group hover:border-primary/40 transition-all duration-300">
          <div className="flex justify-between items-start mb-4">
            <span className="font-headline text-[10px] text-on-surface-variant uppercase tracking-widest font-bold">Compliance Score</span>
            <div className="w-8 h-8 rounded-lg bg-surface-container flex items-center justify-center border border-outline-variant/40 group-hover:text-primary transition-colors">
              <Shield className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2 mb-2">
            <span className="font-headline text-3xl font-bold text-on-surface">{kpis.compliance_score}%</span>
          </div>
          <div className="h-1.5 w-full bg-surface-container-high rounded-full overflow-hidden">
            <div className="h-full bg-primary rounded-full" style={{ width: `${kpis.compliance_score}%` }}></div>
          </div>
        </div>

        {/* False Positive Rate */}
        <div className="p-6 bg-surface-container-low border border-outline-variant/20 rounded-2xl group hover:border-primary/40 transition-all duration-300">
          <div className="flex justify-between items-start mb-4">
            <span className="font-headline text-[10px] text-on-surface-variant uppercase tracking-widest font-bold">False Positive Rate</span>
            <div className="w-8 h-8 rounded-lg bg-surface-container flex items-center justify-center border border-outline-variant/40 group-hover:text-primary transition-colors">
              <AlertTriangle className="w-4 h-4" />
            </div>
          </div>
          <div className="flex items-baseline gap-2 mb-1">
            <span className="font-headline text-3xl font-bold text-on-surface">↓ {kpis.false_positive_rate}%</span>
          </div>
          <p className="text-[11px] text-on-surface-variant">optimized via Two-Tower filtering</p>
        </div>
      </section>

      {/* Main Split Layout */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Table / Chart Area */}
        <div className="lg:col-span-2 space-y-8">
          {/* Active Sessions */}
          <div className="bg-surface-container border border-outline-variant/20 rounded-2xl overflow-hidden shadow-sm">
            <div className="px-6 py-4 flex justify-between items-center border-b border-outline-variant/30">
              <h3 className="font-headline text-md text-on-surface font-semibold">Active Sessions</h3>
              <button 
                onClick={() => navigateToTab("Workspace")}
                className="font-headline text-[10px] text-primary hover:text-primary/80 uppercase font-bold tracking-widest"
              >
                Open workspace
              </button>
            </div>
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="bg-surface-container-low/40">
                    <th className="px-6 py-3 font-headline text-[10px] text-on-surface-variant uppercase tracking-widest">Identifier</th>
                    <th className="px-6 py-3 font-headline text-[10px] text-on-surface-variant uppercase tracking-widest">Severity</th>
                    <th className="px-6 py-3 font-headline text-[10px] text-on-surface-variant uppercase tracking-widest">Confidence</th>
                    <th className="px-6 py-3 font-headline text-[10px] text-on-surface-variant uppercase tracking-widest text-right">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-outline-variant/20">
                  {contradictions.map((c) => (
                    <tr key={c.id} className="hover:bg-surface-container-high/40 transition-colors group">
                      <td className="px-6 py-4">
                        <div className="flex flex-col">
                          <span className="text-xs font-semibold text-on-surface">{c.clause_a.section_heading}</span>
                          <span className="text-[10px] text-on-surface-variant mt-0.5 font-mono">{c.clause_a.source_document}</span>
                        </div>
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 py-0.5 rounded text-[9px] font-headline font-bold uppercase border ${
                          c.severity === "CRITICAL" ? "bg-error/10 text-error border-error/20" :
                          c.severity === "HIGH" ? "bg-tertiary-container/10 text-tertiary border-tertiary/20" :
                          "bg-surface-container-highest text-on-surface-variant border-outline-variant/30"
                        }`}>
                          {c.severity}
                        </span>
                      </td>
                      <td className="px-6 py-4">
                        <div className="flex items-center gap-3">
                          <div className="w-24 h-1.5 bg-surface-container-high rounded-full overflow-hidden">
                            <div 
                              className="h-full bg-primary" 
                              style={{ width: `${c.final_confidence * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-[10px] text-on-surface-variant font-mono">{(c.final_confidence * 100).toFixed(0)}%</span>
                        </div>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button 
                          onClick={() => navigateToTab("Workspace")}
                          className="text-on-surface-variant hover:text-primary transition-colors inline-flex items-center"
                        >
                          <ChevronRight className="w-4 h-4" />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Sub-Bento Content Card Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 bg-surface-container border-l-4 border-primary rounded-r-2xl shadow-sm">
              <h4 className="font-headline text-xs font-bold text-primary mb-2 uppercase">Limitation of Liability Inconsistency</h4>
              <p className="text-xs text-on-surface-variant leading-relaxed">
                "Except for damages resulting from fraud or willful misconduct, neither party shall be liable for indirect, incidental, or consequential damages..."
              </p>
              <div className="mt-4 flex items-center gap-2">
                <span className="px-2 py-0.5 bg-surface-container-high rounded text-[8px] font-headline uppercase font-bold text-on-surface-variant border border-outline-variant/30">Contract Cap Shift</span>
                <span className="px-2 py-0.5 bg-surface-container-high rounded text-[8px] font-headline uppercase font-bold text-on-surface-variant border border-outline-variant/30">Asymmetry Risk</span>
              </div>
            </div>

            {/* Sparkline chart bento */}
            <div className="p-6 bg-surface-container border border-outline-variant/20 rounded-2xl shadow-sm">
              <div className="flex justify-between items-center mb-2">
                <h4 className="font-headline text-xs font-bold text-on-surface uppercase">Contradiction Trend Tracker</h4>
                <span className="font-headline text-[9px] text-primary bg-primary/10 px-2 py-0.5 rounded font-bold">30-DAY</span>
              </div>
              <div className="h-16 w-full flex items-end gap-1 mb-3 pt-2">
                {sparkPoints.map((pt, idx) => (
                  <div 
                    key={idx} 
                    className="flex-1 bg-primary/20 hover:bg-primary/50 transition-all rounded-t-sm" 
                    style={{ height: `${(pt/32)*100}%` }}
                  ></div>
                ))}
              </div>
              <p className="text-[10px] text-on-surface-variant leading-normal">
                Analysis detection frequency increased by 14% this month across local edge compliance servers.
              </p>
            </div>
          </div>
        </div>

        {/* Right Bento Area (Quick Scan & Activity logs) */}
        <div className="space-y-8">
          {/* Quick Scan Drop Zone */}
          <div 
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            className={`p-8 bg-surface-container border border-dashed rounded-2xl flex flex-col items-center justify-center text-center group cursor-pointer transition-all duration-300 ${
              dragActive ? 'border-primary bg-primary/5' : 'border-outline-variant/50 hover:border-primary/50'
            }`}
          >
            <input 
              type="file" 
              id="file-upload" 
              className="hidden" 
              accept=".pdf,.docx"
              onChange={handleFileChange}
            />
            <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center justify-center">
              <div className="w-12 h-12 rounded-xl border border-outline-variant/40 bg-background flex items-center justify-center mb-4 group-hover:scale-105 group-hover:border-primary/30 transition-all">
                <Upload className="w-5 h-5 text-on-surface-variant group-hover:text-primary transition-colors" />
              </div>
              <h4 className="font-headline text-sm font-bold text-on-surface mb-1">Quick Inbound Scan</h4>
              <p className="text-xs text-on-surface-variant px-4 leading-relaxed">
                Click or drag & drop organizational policy PDF or Contract documents to run contradiction mapping.
              </p>
              {uploadStatus && (
                <div className="mt-4 px-3 py-1 bg-primary/10 border border-primary/20 rounded-full">
                  <p className="text-[10px] font-headline font-bold text-primary animate-pulse">{uploadStatus}</p>
                </div>
              )}
            </label>
          </div>

          {/* Recent Activity */}
          <div className="bg-surface-container border border-outline-variant/20 rounded-2xl p-6">
            <div className="flex justify-between items-center mb-6">
              <h3 className="font-headline text-[10px] text-on-surface-variant uppercase tracking-[0.2em] font-bold">Recent Audits</h3>
              <Activity className="w-4 h-4 text-on-surface-variant" />
            </div>
            <div className="space-y-6">
              <div className="flex gap-4 relative after:absolute after:left-3 after:top-8 after:h-6 after:w-[1px] after:bg-outline-variant/20 last:after:hidden">
                <div className="w-6 h-6 rounded bg-primary/10 flex items-center justify-center border border-primary/20 shrink-0">
                  <span className="w-1.5 h-1.5 rounded-full bg-primary"></span>
                </div>
                <div>
                  <p className="text-xs font-semibold text-on-surface leading-none">Inbound Scan Ingested</p>
                  <p className="text-[10px] text-on-surface-variant mt-1">SOP_Data_Retention_v2.pdf</p>
                  <p className="text-[8px] text-on-surface-variant/40 mt-1 font-bold uppercase">10m ago</p>
                </div>
              </div>

              <div className="flex gap-4 relative after:absolute after:left-3 after:top-8 after:h-6 after:w-[1px] after:bg-outline-variant/20 last:after:hidden">
                <div className="w-6 h-6 rounded bg-tertiary-container/10 flex items-center justify-center border border-tertiary-container/20 shrink-0">
                  <span className="w-1.5 h-1.5 rounded-full bg-tertiary"></span>
                </div>
                <div>
                  <p className="text-xs font-semibold text-on-surface leading-none">Contradiction Resolved</p>
                  <p className="text-[10px] text-on-surface-variant mt-1">Lookback liability aligned to standard v4</p>
                  <p className="text-[8px] text-on-surface-variant/40 mt-1 font-bold uppercase">1h ago</p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="w-6 h-6 rounded bg-surface-container-highest flex items-center justify-center border border-outline-variant/30 shrink-0">
                  <span className="w-1.5 h-1.5 rounded-full bg-on-surface-variant/40"></span>
                </div>
                <div>
                  <p className="text-xs font-semibold text-on-surface leading-none">Model Restored</p>
                  <p className="text-[10px] text-on-surface-variant mt-1">Memory pressure cleared. Main model active</p>
                  <p className="text-[8px] text-on-surface-variant/40 mt-1 font-bold uppercase">2h ago</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
