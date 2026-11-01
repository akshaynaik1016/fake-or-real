import React, { useState } from 'react';
import { Sliders, Save, CheckCircle2, ShieldCheck, RotateCcw, AlertTriangle } from 'lucide-react';

const DEFAULT_WEIGHTS = {
  url_security: 15,
  domain_intelligence: 10,
  organization_verification: 15,
  email_security: 10,
  threat_intelligence: 15,
  content_analysis: 10,
  payment_risk: 10,
  identity_verification: 5,
  document_analysis: 5,
  community_reports: 5,
};

export const SettingsPage: React.FC = () => {
  const [weights, setWeights] = useState({ ...DEFAULT_WEIGHTS });
  const [saved, setSaved] = useState(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const total = Object.values(weights).reduce((a, b) => a + b, 0);

  const handleReset = () => {
    setWeights({ ...DEFAULT_WEIGHTS });
    setErrorMsg(null);
  };

  const handleSave = () => {
    if (total !== 100) {
      setErrorMsg(`Forensic weights must sum to exactly 100% (currently ${total}%). Please balance the sliders.`);
      return;
    }
    setErrorMsg(null);
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="min-h-screen py-10 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto space-y-8">
      
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-cyber-border gap-4">
        <div>
          <div className="flex items-center space-x-2 text-cyber-cyan mb-1">
            <Sliders className="w-5 h-5" />
            <h1 className="text-2xl sm:text-3xl font-extrabold text-white">Forensic Engine Weights & Calibration</h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-400">
            Tune multi-factor detection sensitivity and risk scoring attribution across 10 security verification vectors.
          </p>
        </div>

        <div className="p-3.5 rounded-2xl bg-cyber-surface/80 border border-cyber-border text-right flex-shrink-0">
          <span className="text-[10px] font-mono uppercase text-slate-400 block">Total Engine Weight</span>
          <div className="flex items-center justify-end space-x-2">
            <span className={`text-2xl font-black font-mono ${total === 100 ? 'text-emerald-400' : 'text-rose-400'}`}>
              {total}%
            </span>
            <span className={`text-[10px] font-mono font-bold uppercase px-2 py-0.5 rounded ${
              total === 100 ? 'bg-emerald-950 text-emerald-400 border border-emerald-500/40' : 'bg-rose-950 text-rose-400 border border-rose-500/40'
            }`}>
              {total === 100 ? 'CALIBRATED' : 'UNBALANCED'}
            </span>
          </div>
        </div>
      </div>

      {saved && (
        <div className="p-4 rounded-xl bg-emerald-950/70 border border-emerald-500/60 text-emerald-300 text-xs flex items-center space-x-2 shadow-[0_0_15px_rgba(16,185,129,0.2)]">
          <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          <span>Forensic weights successfully calibrated and saved to active scoring profile!</span>
        </div>
      )}

      {errorMsg && (
        <div className="p-4 rounded-xl bg-rose-950/70 border border-rose-500/60 text-rose-300 text-xs flex items-center space-x-2">
          <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
          <span>{errorMsg}</span>
        </div>
      )}

      {/* Weights sliders */}
      <div className="p-6 rounded-2xl glass-card border border-cyber-border space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="font-bold text-white text-base">Multi-Signal Distribution Matrix</h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Adjust relative weight contributions for each detection subsystem.
            </p>
          </div>
          <button
            onClick={handleReset}
            className="px-3.5 py-1.5 rounded-xl bg-cyber-bg border border-cyber-border hover:border-cyber-cyan text-slate-300 hover:text-white text-xs font-mono flex items-center space-x-1.5 transition-colors"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Reset Defaults</span>
          </button>
        </div>

        <div className="space-y-4 pt-2">
          {Object.entries(weights).map(([key, val]) => (
            <div key={key} className="space-y-1.5 p-3 rounded-xl bg-cyber-bg/60 border border-cyber-border/80">
              <div className="flex justify-between text-xs">
                <span className="text-slate-200 font-semibold capitalize font-mono text-[11px]">
                  {key.replace(/_/g, ' ')}
                </span>
                <span className="font-mono text-cyber-cyan font-bold bg-cyber-cyan/10 px-2 py-0.5 rounded border border-cyber-cyan/20">
                  {val}%
                </span>
              </div>
              <input
                type="range"
                min="0"
                max="35"
                value={val}
                onChange={(e) => setWeights({ ...weights, [key]: parseInt(e.target.value) || 0 })}
                className="w-full accent-cyan-400 cursor-pointer bg-slate-800"
              />
            </div>
          ))}
        </div>

        <div className="pt-4 border-t border-cyber-border flex items-center justify-between">
          <span className="text-xs text-slate-400 font-mono">
            {total === 100 ? '✓ Ready to apply configuration' : `⚠ Balance required: ${100 - total > 0 ? `+${100 - total}% needed` : `${total - 100}% over limit`}`}
          </span>
          <button
            onClick={handleSave}
            disabled={total !== 100}
            className="px-6 py-2.5 rounded-xl bg-cyber-cyan text-slate-950 font-extrabold text-xs hover:bg-cyan-400 transition-colors flex items-center space-x-1.5 disabled:opacity-50 disabled:cursor-not-allowed shadow-[0_0_15px_rgba(6,182,212,0.3)]"
          >
            <Save className="w-4 h-4 stroke-[2.5]" />
            <span>Apply Weights</span>
          </button>
        </div>
      </div>

    </div>
  );
};
