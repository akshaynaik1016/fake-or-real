import { fetchJson } from '../api/client';
import React, { useEffect, useState } from 'react';
import { Lock, ShieldAlert, Users, Database, Cpu, CheckCircle2, Sliders, Activity } from 'lucide-react';

export const AdminPage: React.FC = () => {
  const [error, setError] = useState('');
  const [metrics, setMetrics] = useState<any>(null);
  const [logs, setLogs] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      fetchJson('/admin/metrics'),
      fetchJson('/admin/audit-logs')
    ]).then(([m, l]) => {
      setMetrics(m);
      setLogs(l);
      setLoading(false);
    }).catch(e => { setError(e.message); setLoading(false); });
  }, []);

  if (error) return <p role="alert" className="p-8 text-rose-300">{error}</p>;
  if (loading || !metrics) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <span className="font-mono text-xs text-cyber-cyan">Accessing security administration terminal...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-10 px-4 sm:px-6 lg:px-8 max-w-6xl mx-auto space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-cyber-border gap-4">
        <div>
          <div className="flex items-center space-x-2 text-cyber-cyan mb-1">
            <Lock className="w-5 h-5" />
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white">Security & Governance Console</h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-400">
            RBAC administration, threat provider health, audit logging, and transparent scoring weights.
          </p>
        </div>
        <span className="text-xs font-mono px-3 py-1.5 rounded-full bg-emerald-950/60 text-emerald-400 border border-emerald-500/40 flex items-center space-x-2 w-fit">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
          <span>Admin Access Verified (Role: ADMIN)</span>
        </span>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-2xl glass-card border border-cyber-border">
          <span className="text-[10px] font-mono uppercase text-slate-400">Total Scans</span>
          <p className="text-2xl font-black font-mono text-white mt-1">{metrics.total_scans}</p>
        </div>
        <div className="p-4 rounded-2xl glass-card border border-rose-500/30 bg-rose-950/10">
          <span className="text-[10px] font-mono uppercase text-slate-400">Critical Detections</span>
          <p className="text-2xl font-black font-mono text-rose-400 mt-1">{metrics.critical_scans}</p>
        </div>
        <div className="p-4 rounded-2xl glass-card border border-cyber-border">
          <span className="text-[10px] font-mono uppercase text-slate-400">API Health</span>
          <p className="text-sm font-bold font-mono text-emerald-400 mt-2">{metrics.api_health}</p>
        </div>
        <div className="p-4 rounded-2xl glass-card border border-cyber-border">
          <span className="text-[10px] font-mono uppercase text-slate-400">Worker Status</span>
          <p className="text-sm font-bold font-mono text-cyber-cyan mt-2">{metrics.worker_health}</p>
        </div>
      </div>

      {/* Threat Provider Statuses */}
      <div className="p-6 rounded-2xl glass-card border border-cyber-border">
        <div className="flex items-center space-x-2 text-cyber-cyan mb-4">
          <Activity className="w-4 h-4" />
          <h3 className="font-bold text-white text-base">Threat Intelligence Provider Statuses</h3>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
          {Object.entries(metrics.threat_intel_status).map(([prov, stat]: any, idx) => (
            <div key={idx} className="p-3.5 rounded-xl bg-cyber-bg border border-cyber-border">
              <span className="text-slate-400 block font-mono text-[11px] truncate">{prov}</span>
              <strong className="text-slate-200 block mt-1">{stat}</strong>
            </div>
          ))}
        </div>
      </div>

      {/* Configured Scoring Weights (Transparent Scoring - Requirement 33) */}
      <div className="p-6 rounded-2xl glass-card border border-cyber-border">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center space-x-2 text-cyber-cyan">
            <Sliders className="w-4 h-4" />
            <h3 className="font-bold text-white text-base">Configurable Scoring Engine Weights</h3>
          </div>
          <span className="text-xs font-mono text-slate-400">Normalized: 100%</span>
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-5 gap-3 text-xs font-mono">
          {Object.entries(metrics.active_scoring_weights).map(([k, w]: any, idx) => (
            <div key={idx} className="p-3 rounded-xl bg-cyber-bg border border-cyber-border text-center">
              <span className="text-slate-400 block text-[10px] uppercase truncate">{k.replace(/_/g, ' ')}</span>
              <span className="text-lg font-black text-cyber-cyan mt-1 block">{(w * 100).toFixed(0)}%</span>
            </div>
          ))}
        </div>
      </div>

      {/* System Audit Logs (Requirement 55) */}
      <div className="p-6 rounded-2xl glass-card border border-cyber-border">
        <h3 className="font-bold text-white text-base mb-1">System Security Audit Logs</h3>
        <p className="text-xs text-slate-400 mb-4">Immutable audit events recorded with sensitive credentials redacted</p>
        
        <div className="space-y-2 font-mono text-xs">
          {logs.map((l: any, i: number) => (
            <div key={i} className="p-3 rounded-xl bg-cyber-bg border border-cyber-border flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2">
              <div className="flex items-center space-x-3">
                <span className="text-cyber-cyan font-bold">{l.action}</span>
                <span className="text-slate-400 truncate max-w-md">{JSON.stringify(l.details)}</span>
              </div>
              <span className="text-[11px] text-slate-400 whitespace-nowrap">{l.timestamp}</span>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
};
