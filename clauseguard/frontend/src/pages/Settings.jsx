import React, { useState } from 'react';
import { Settings as SettingsIcon, Shield, Globe, Bell, Code, Key } from 'lucide-react';

export default function Settings({ theme, setTheme }) {
  const [activeSubTab, setActiveSubTab] = useState("general");
  const [llmUrl, setLlmUrl] = useState("http://localhost:11434");
  const [embedPath, setEmbedPath] = useState("nlpaueb/legal-bert-base-uncased");
  const [webhookUrl, setWebhookUrl] = useState("https://api.clauseguard.corp/v1/escalations");
  const [auditPeriod, setAuditPeriod] = useState("365");

  const saveSettings = () => {
    alert("Configuration parameters updated locally.");
  };

  return (
    <div className="space-y-8 animate-fadeIn max-w-[1000px] mx-auto p-2">
      <div className="border-b border-outline-variant/20 pb-6">
        <h2 className="font-headline text-3xl font-bold tracking-tight text-on-surface">Configuration Panel</h2>
        <p className="text-on-surface-variant text-sm mt-1">
          Configure security protocols, offline model links, and webhook integrations.
        </p>
      </div>

      <div className="flex flex-col md:flex-row gap-8 items-start">
        {/* Left Sub-navigation Tabs */}
        <div className="w-full md:w-56 bg-surface-container border border-outline-variant/20 rounded-2xl p-4 flex flex-col space-y-1">
          <button 
            onClick={() => setActiveSubTab("general")}
            className={`flex items-center gap-3 px-4 py-2.5 rounded-xl text-left text-xs font-headline uppercase font-bold tracking-wider transition-all ${
              activeSubTab === "general" ? "bg-primary/10 text-primary border border-primary/20" : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high/40"
            }`}
          >
            <SettingsIcon className="w-4 h-4" />
            General
          </button>
          
          <button 
            onClick={() => setActiveSubTab("network")}
            className={`flex items-center gap-3 px-4 py-2.5 rounded-xl text-left text-xs font-headline uppercase font-bold tracking-wider transition-all ${
              activeSubTab === "network" ? "bg-primary/10 text-primary border border-primary/20" : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high/40"
            }`}
          >
            <Globe className="w-4 h-4" />
            Network & Model
          </button>

          <button 
            onClick={() => setActiveSubTab("security")}
            className={`flex items-center gap-3 px-4 py-2.5 rounded-xl text-left text-xs font-headline uppercase font-bold tracking-wider transition-all ${
              activeSubTab === "security" ? "bg-primary/10 text-primary border border-primary/20" : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high/40"
            }`}
          >
            <Shield className="w-4 h-4" />
            Security & Audit
          </button>

          <button 
            onClick={() => setActiveSubTab("webhooks")}
            className={`flex items-center gap-3 px-4 py-2.5 rounded-xl text-left text-xs font-headline uppercase font-bold tracking-wider transition-all ${
              activeSubTab === "webhooks" ? "bg-primary/10 text-primary border border-primary/20" : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high/40"
            }`}
          >
            <Code className="w-4 h-4" />
            Webhooks
          </button>
        </div>

        {/* Right Tab Content Container */}
        <div className="flex-1 bg-surface-container border border-outline-variant/20 rounded-3xl p-8 space-y-6 w-full">
          {activeSubTab === "general" && (
            <div className="space-y-4">
              <h3 className="font-headline text-sm font-bold text-on-surface uppercase mb-4">General Settings</h3>
              <div>
                <label className="block text-xs font-semibold text-on-surface-variant mb-2">Theme Selection</label>
                <div className="flex gap-4">
                  <button 
                    onClick={() => setTheme("dark")}
                    className={`px-4 py-2 rounded-xl font-headline text-[10px] font-bold uppercase tracking-wider transition-all ${
                      theme === "dark" 
                        ? "bg-primary/10 border border-primary/20 text-primary font-bold" 
                        : "border border-outline-variant/30 text-on-surface-variant opacity-60 hover:opacity-100"
                    }`}
                  >
                    Dark Mode (Default)
                  </button>
                  <button 
                    onClick={() => setTheme("light")}
                    className={`px-4 py-2 rounded-xl font-headline text-[10px] font-bold uppercase tracking-wider transition-all ${
                      theme === "light" 
                        ? "bg-primary/10 border border-primary/20 text-primary font-bold" 
                        : "border border-outline-variant/30 text-on-surface-variant opacity-60 hover:opacity-100"
                    }`}
                  >
                    Light Mode
                  </button>
                </div>
              </div>
              <div className="pt-4">
                <label className="block text-xs font-semibold text-on-surface-variant mb-2">Interface Scaling</label>
                <select className="bg-background border border-outline-variant/30 rounded-xl px-4 py-2 text-xs focus:ring-1 focus:ring-primary focus:outline-none text-on-surface font-semibold w-full max-w-xs">
                  <option>100% (Standard)</option>
                  <option>110% (Medium)</option>
                  <option>120% (Large)</option>
                </select>
              </div>
            </div>
          )}

          {activeSubTab === "network" && (
            <div className="space-y-4">
              <h3 className="font-headline text-sm font-bold text-on-surface uppercase mb-4">Network & LLM Configurations</h3>
              <div>
                <label className="block text-xs font-semibold text-on-surface-variant mb-2">LLM Server Base URL Override</label>
                <input 
                  type="text" 
                  value={llmUrl} 
                  onChange={(e) => setLlmUrl(e.target.value)}
                  className="w-full bg-background border border-outline-variant/30 rounded-xl px-4 py-2.5 text-xs text-on-surface focus:ring-1 focus:ring-primary focus:outline-none font-mono"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-on-surface-variant mb-2">Local Embedding Weights Path</label>
                <input 
                  type="text" 
                  value={embedPath} 
                  onChange={(e) => setEmbedPath(e.target.value)}
                  className="w-full bg-background border border-outline-variant/30 rounded-xl px-4 py-2.5 text-xs text-on-surface focus:ring-1 focus:ring-primary focus:outline-none font-mono"
                />
              </div>
            </div>
          )}

          {activeSubTab === "security" && (
            <div className="space-y-4">
              <h3 className="font-headline text-sm font-bold text-on-surface uppercase mb-4">Security & Audit Policies</h3>
              <div>
                <label className="block text-xs font-semibold text-on-surface-variant mb-2">Audit Logs Retention (Days)</label>
                <select 
                  value={auditPeriod}
                  onChange={(e) => setAuditPeriod(e.target.value)}
                  className="bg-background border border-outline-variant/30 rounded-xl px-4 py-2 text-xs focus:ring-1 focus:ring-primary focus:outline-none text-on-surface font-semibold w-full max-w-xs"
                >
                  <option value="90">90 Days</option>
                  <option value="180">180 Days</option>
                  <option value="365">365 Days (Standard)</option>
                </select>
              </div>
              <div className="pt-4 flex items-center justify-between border-t border-outline-variant/20 mt-4">
                <div>
                  <h5 className="text-xs font-semibold text-on-surface">Mandatory Reviewer Authentication</h5>
                  <p className="text-[10px] text-on-surface-variant mt-1">Requires single-sign-on check before applying contradiction edits.</p>
                </div>
                <input type="checkbox" defaultChecked className="rounded border-outline-variant/40 bg-background text-primary focus:ring-primary w-4 h-4" />
              </div>
            </div>
          )}

          {activeSubTab === "webhooks" && (
            <div className="space-y-4">
              <h3 className="font-headline text-sm font-bold text-on-surface uppercase mb-4">Webhooks & Escalation Triggers</h3>
              <div>
                <label className="block text-xs font-semibold text-on-surface-variant mb-2">Escalation Receiver Endpoint URL</label>
                <input 
                  type="text" 
                  value={webhookUrl} 
                  onChange={(e) => setWebhookUrl(e.target.value)}
                  className="w-full bg-background border border-outline-variant/30 rounded-xl px-4 py-2.5 text-xs text-on-surface focus:ring-1 focus:ring-primary focus:outline-none font-mono"
                />
              </div>
              <p className="text-[10px] text-on-surface-variant leading-relaxed pt-2">
                ClauseGuard will trigger an HTTP POST webhook containing serialized contradictions, audit trails, and reviewer notes whenever an escalation action is confirmed by the human review pool.
              </p>
            </div>
          )}

          <div className="pt-6 border-t border-outline-variant/20 flex justify-end">
            <button 
              onClick={saveSettings}
              className="bg-primary hover:bg-primary/95 text-white px-6 py-2.5 rounded-xl font-headline text-xs font-bold uppercase tracking-widest transition-all"
            >
              Save Configurations
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
