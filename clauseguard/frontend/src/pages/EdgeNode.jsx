import React, { useState, useEffect, useRef } from 'react';
import { Cpu, Thermometer, Activity, Terminal, Shield, CheckCircle, RefreshCw, AlertTriangle } from 'lucide-react';

export default function EdgeNode() {
  const [status, setStatus] = useState(null);
  const [logs, setLogs] = useState([]);
  const [selectedProfile, setSelectedProfile] = useState("auto");
  const terminalEndRef = useRef(null);

  const fetchTelemetryData = async () => {
    try {
      const { fetchTelemetry } = await import('../api/client');
      const data = await fetchTelemetry();
      setStatus(data);
      
      // Auto-append simulated log entries to the stream
      const timestamp = new Date().toLocaleTimeString();
      let newLog = `[ ${timestamp} ] heartbeat: node health status OK - telemetry synchronized`;
      if (Math.random() > 0.8) {
        newLog = `[ ${timestamp} ] request: [POST] /v1/embeddings - parsed 1.2k chars [DONE] 12ms`;
      } else if (Math.random() > 0.95) {
        newLog = `[ ${timestamp} ] WARN: Memory usage exceeds threshold. Cleaning model cache pools.`;
      }
      
      setLogs(prev => {
        const next = [...prev, newLog];
        if (next.length > 50) next.shift();
        return next;
      });
    } catch (e) {
      // handled by mock
    }
  };

  useEffect(() => {
    // Initial logs seed
    setLogs([
      "[ 142.102834 ] Initializing NVMe Storage Cluster...",
      "[ 142.349012 ] Device /dev/nvme0n1 identified as ClauseGuard SecureDrive (512GB)",
      "[ 143.001928 ] loading model: LLaMA 3.1 8B (Q4_K_M)",
      "[ 143.210492 ] model weight mapping complete (4.6 GB loaded into RAM)",
      "[ 143.558291 ] CUDA/Vulkan fallback: Using ARM-NEON optimization",
      "[ 144.102239 ] starting server on port 8080 (REST + gRPC)",
      "[ 144.102245 ] ingress tunnel established via tailscale0",
      "[ 145.829102 ] WARN: Memory usage warning threshold set at 80% RAM pressure"
    ]);

    fetchTelemetryData();
    const interval = setInterval(fetchTelemetryData, 2000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (terminalEndRef.current) {
      terminalEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [logs]);

  const handleProfileOverride = async (e) => {
    const target = e.target.value;
    setSelectedProfile(target);
    if (target === "auto") return;
    
    try {
      const { overrideProfile } = await import('../api/client');
      await overrideProfile(target);
      fetchTelemetryData();
    } catch (err) {}
  };

  if (!status) {
    return (
      <div className="flex h-[80vh] items-center justify-center">
        <p className="text-sm font-headline animate-pulse">Connecting to Edge telemetry...</p>
      </div>
    );
  }

  // Circular gauge parameter calculations
  const radius = 70;
  const stroke = 3;
  const normalizedRadius = radius - stroke * 2;
  const circumference = normalizedRadius * 2 * Math.PI;
  const strokeDashoffset = circumference - (status.cpu_pct / 100) * circumference;

  return (
    <div className="space-y-8 animate-fadeIn max-w-[1400px] mx-auto p-2">
      {/* Dynamic Warn Banner for Falling Back */}
      {status.fallback_active && (
        <div className="p-4 bg-tertiary-container/10 border-l-4 border-l-tertiary border border-tertiary/20 rounded-r-2xl flex items-center gap-3 animate-pulse">
          <AlertTriangle className="text-tertiary w-5 h-5 shrink-0" />
          <p className="text-xs text-on-surface leading-relaxed">
            <span className="font-bold">Fallback Model Active:</span> {status.active_model} (RAM pressure detected above 80%).
          </p>
        </div>
      )}

      {/* Header telemetry details */}
      <section className="flex flex-col lg:flex-row lg:items-end justify-between gap-6 border-b border-outline-variant/20 pb-6">
        <div>
          <h2 className="font-headline text-3xl font-bold tracking-tight text-on-surface">Edge Node Overview</h2>
          <p className="text-on-surface-variant text-sm mt-1">
            Real-time Raspberry Pi edge hardware telemetry and local model execution parameters.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-xs text-on-surface-variant font-headline uppercase font-bold">Development Override:</span>
          <select 
            value={selectedProfile}
            onChange={handleProfileOverride}
            className="bg-surface-container border border-outline-variant/30 rounded-xl px-4 py-2 text-xs focus:ring-1 focus:ring-primary focus:outline-none text-on-surface font-semibold"
          >
            <option value="auto">Auto-detect Profile</option>
            <option value="LAPTOP">Force LAPTOP Profile</option>
            <option value="RPI5">Force RPi5 Profile</option>
            <option value="RPI4">Force RPi4 Profile</option>
          </select>
        </div>
      </section>

      {/* Three Metric Panels Bento */}
      <section className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* 1. CPU Load Gauge */}
        <div className="bg-surface-container border border-outline-variant/20 p-6 rounded-2xl flex flex-col items-center justify-between min-h-[220px]">
          <div className="w-full flex justify-between items-start mb-4">
            <span className="font-headline text-[10px] text-on-surface-variant uppercase tracking-widest font-bold">Compute Load</span>
            <Cpu className="w-4 h-4 text-primary" />
          </div>
          <div className="relative w-36 h-36 flex items-center justify-center">
            <svg className="w-full h-full -rotate-90">
              <circle className="text-outline-variant/10" cx="72" cy="72" fill="transparent" r={normalizedRadius} stroke="currentColor" strokeWidth={stroke}></circle>
              <circle className="text-primary transition-all duration-500" cx="72" cy="72" fill="transparent" r={normalizedRadius} stroke="currentColor" strokeDasharray={circumference} strokeDashoffset={strokeDashoffset} strokeLinecap="round" strokeWidth={stroke}></circle>
            </svg>
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="font-headline text-3xl font-light text-on-surface">{status.cpu_pct.toFixed(0)}%</span>
              <span className="text-[9px] uppercase tracking-wider text-on-surface-variant mt-1 font-headline">Processor</span>
            </div>
          </div>
        </div>

        {/* 2. Thermals */}
        <div className="bg-surface-container border border-outline-variant/20 p-6 rounded-2xl flex flex-col justify-between min-h-[220px]">
          <div className="w-full flex justify-between items-start">
            <span className="font-headline text-[10px] text-on-surface-variant uppercase tracking-widest font-bold">Thermals</span>
            <CheckCircle className="w-4 h-4 text-primary" />
          </div>
          <div className="py-4">
            <div className="flex justify-between items-end mb-2">
              <span className="font-headline text-4xl font-bold">{status.temperature_c.toFixed(1)}°C</span>
              <span className="text-primary font-headline text-[10px] uppercase font-bold tracking-widest">Stable</span>
            </div>
            <div className="w-full h-1.5 bg-outline-variant/10 rounded-full overflow-hidden">
              <div className="bg-primary h-full rounded-full" style={{ width: `${(status.temperature_c / 80) * 100}%` }}></div>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-background/40 p-2.5 rounded-xl border border-outline-variant/20">
              <p className="text-[8px] text-on-surface-variant font-headline uppercase font-bold">Fan Speed</p>
              <p className="font-headline text-xs font-semibold mt-1">1,200 RPM</p>
            </div>
            <div className="bg-background/40 p-2.5 rounded-xl border border-outline-variant/20">
              <p className="text-[8px] text-on-surface-variant font-headline uppercase font-bold">Throttle</p>
              <p className="font-headline text-xs font-semibold mt-1">None</p>
            </div>
          </div>
        </div>

        {/* 3. Inference Throughput */}
        <div className="bg-surface-container border border-outline-variant/20 p-6 rounded-2xl flex flex-col justify-between min-h-[220px]">
          <div className="w-full flex justify-between items-start">
            <span className="font-headline text-[10px] text-on-surface-variant uppercase tracking-widest font-bold">Inference Speed</span>
            <Activity className="w-4 h-4 text-primary animate-pulse" />
          </div>
          <div className="py-4">
            <div className="flex justify-between items-end mb-2">
              <span className="font-headline text-4xl font-bold">{status.current_tps}</span>
              <span className="text-primary font-headline text-[10px] uppercase font-bold tracking-widest">TPS</span>
            </div>
            <p className="text-xs text-on-surface-variant leading-relaxed">
              Active model: <span className="text-primary font-semibold">{status.active_model}</span> GGUF local weights.
            </p>
          </div>
          <div className="bg-background/40 p-3 rounded-xl border border-outline-variant/20 text-center flex items-center justify-center">
            <span className="w-2 h-2 rounded-full bg-primary animate-ping mr-2"></span>
            <span className="font-headline text-[9px] uppercase tracking-widest font-bold text-primary">Live stream active</span>
          </div>
        </div>
      </section>

      {/* Logs and Management Split */}
      <section className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Terminal logs */}
        <div className="lg:col-span-2 bg-surface-container-lowest border border-outline-variant/30 rounded-2xl flex flex-col h-[400px] overflow-hidden">
          <div className="px-6 py-3 border-b border-outline-variant/20 bg-surface-container/30 flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="w-2.5 h-2.5 rounded-full bg-red-500/20 border border-red-500/40"></span>
              <span className="w-2.5 h-2.5 rounded-full bg-yellow-500/20 border border-yellow-500/40"></span>
              <span className="w-2.5 h-2.5 rounded-full bg-green-500/20 border border-green-500/40"></span>
            </div>
            <span className="font-headline text-[9px] uppercase tracking-widest font-bold text-on-surface-variant">system_log_stream</span>
          </div>
          <div className="flex-1 p-6 font-mono text-[11px] overflow-y-auto custom-scrollbar bg-surface-container-lowest space-y-2 text-on-surface-variant/90 select-text">
            {logs.map((log, idx) => {
              let colorClass = "text-on-surface-variant/80";
              if (log.includes("WARN")) {
                colorClass = "text-tertiary";
              } else if (log.includes("ERROR")) {
                colorClass = "text-error";
              } else if (log.includes("heartbeat")) {
                colorClass = "text-primary/80";
              }
              return (
                <p key={idx} className={colorClass}>{log}</p>
              );
            })}
            <div ref={terminalEndRef} />
          </div>
        </div>

        {/* Deployed Models and Integrity */}
        <div className="space-y-6">
          {/* Deployed models list */}
          <div className="p-6 bg-surface-container border border-outline-variant/20 rounded-2xl">
            <h4 className="font-headline text-[10px] text-on-surface-variant uppercase tracking-widest font-bold mb-4">Deployed Models</h4>
            <div className="space-y-4">
              {status.deployed_models.map((m, idx) => (
                <div key={idx} className="p-4 bg-background/50 border border-outline-variant/20 rounded-xl">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-xs font-semibold text-on-surface">{m.name}</span>
                    <span className={`px-2 py-0.5 rounded text-[8px] font-headline font-bold uppercase ${
                      m.status === "ACTIVE" ? "bg-primary/10 text-primary border border-primary/20" : "bg-surface-container-highest text-on-surface-variant"
                    }`}>
                      {m.status}
                    </span>
                  </div>
                  <div className="flex justify-between text-[9px] text-on-surface-variant font-mono">
                    <span>RAM: {m.memory_usage}</span>
                    <span>Latency: {m.latency}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Hardware integrity */}
          <div className="p-6 bg-surface-container border border-outline-variant/20 rounded-2xl">
            <h4 className="font-headline text-[10px] text-on-surface-variant uppercase tracking-widest font-bold mb-4">Hardware Integrity</h4>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-xs text-on-surface-variant">Storage Rail</span>
                <span className="text-xs font-semibold text-on-surface font-mono">{status.hardware_integrity.nvme}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-on-surface-variant">Network interface</span>
                <span className="text-xs font-semibold text-on-surface font-mono">{status.hardware_integrity.ethernet}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-xs text-on-surface-variant">PoE+ Power Rail</span>
                <span className="text-xs font-semibold text-on-surface font-mono">{status.hardware_integrity.power}</span>
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
