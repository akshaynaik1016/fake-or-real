import {riskIndex} from '../components/common/assessmentSemantics';
import React, { useState } from 'react';
import { ShieldCheck, AlertOctagon, ExternalLink, Download, ArrowRight, ShieldAlert, CheckCircle2, X } from 'lucide-react';
import { RiskBadge } from '../components/common/RiskBadge';

export const ExtensionPage: React.FC = () => {
  const [activeSite, setActiveSite] = useState<'fake' | 'genuine'>('fake');
  const [showWarningModal, setShowWarningModal] = useState(false);

  const fakeData = {
    url: "https://microsoft-careers-india.xyz/onboard/pay",
    domain: "microsoft-careers-india.xyz",
    organization: "Claimed: Microsoft Corporation",
    trustScore: null,
    riskLevel: "CRITICAL RISK",
    domainAge: "Not queried",
    paymentRisk: "₹999 Registration Deposit Required",
    verificationStatus: "Unresolved — synthetic illustration",
    threatReports: "Not queried — no provider result"
  };

  const genuineData = {
    url: "https://nextstep.tcs.com/campus/#/register",
    domain: "nextstep.tcs.com",
    organization: "Tata Consultancy Services Limited",
    trustScore: null,
    riskLevel: "UNDETERMINED",
    domainAge: "Not queried",
    paymentRisk: "No Payment Demanded",
    verificationStatus: "Unresolved — synthetic illustration",
    threatReports: "Not queried — no provider result"
  };

  const current = activeSite === 'fake' ? fakeData : genuineData;

  return (
    <div className="min-h-screen py-10 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto space-y-8">
      
      {/* Header */}
      <div className="text-center">
        <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-cyber-cyan/10 border border-cyber-cyan/30 mb-3 text-cyber-cyan text-xs font-mono">
          <ShieldCheck className="w-4 h-4" />
          <span>Chrome & Edge Extension Simulator</span>
        </div>
        <h1 className="text-3xl font-extrabold text-white">Browser Extension & Real-Time Warning</h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-1 max-w-xl mx-auto">
          Synthetic extension UI preview. No network, threat-feed or authenticity check runs here. Use Analyze or Evidence Challenge to execute the real pipeline.
        </p>
      </div>

      {/* Simulator Switcher */}
      <div className="flex justify-center space-x-3">
        <button
          onClick={() => {
            setActiveSite('fake');
            setShowWarningModal(true);
          }}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeSite === 'fake'
              ? 'bg-rose-950 border border-rose-500 text-rose-300 shadow-[0_0_15px_rgba(244,63,94,0.3)]'
              : 'bg-cyber-surface border border-cyber-border text-slate-400 hover:text-white'
          }`}
        >
          Simulate Suspicious Site (microsoft-careers-india.xyz)
        </button>

        <button
          onClick={() => {
            setActiveSite('genuine');
            setShowWarningModal(false);
          }}
          className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
            activeSite === 'genuine'
              ? 'bg-emerald-950 border border-emerald-500 text-emerald-300 shadow-[0_0_15px_rgba(16,185,129,0.3)]'
              : 'bg-cyber-surface border border-cyber-border text-slate-400 hover:text-white'
          }`}
        >
          Simulate Normal-looking Unverified Site (nextstep.tcs.com)
        </button>
      </div>

      {/* Interactive Browser Frame */}
      <div className="rounded-3xl border border-cyber-border bg-slate-950 shadow-2xl overflow-hidden max-w-3xl mx-auto">
        
        {/* Browser Top Bar */}
        <div className="px-4 py-3 bg-slate-900 border-b border-slate-800 flex items-center space-x-3">
          <div className="flex space-x-1.5">
            <div className="w-3 h-3 rounded-full bg-rose-500/80" />
            <div className="w-3 h-3 rounded-full bg-amber-500/80" />
            <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
          </div>

          {/* Address Bar */}
          <div className="flex-1 bg-slate-950 border border-slate-700/80 rounded-xl px-3 py-1.5 text-xs font-mono text-slate-300 flex items-center justify-between">
            <span className="truncate">{current.url}</span>
            <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded ${
              activeSite === 'fake' ? 'bg-rose-950 text-rose-400 border border-rose-800' : 'bg-emerald-950 text-emerald-400 border border-emerald-800'
            }`}>
              {current.riskLevel}
            </span>
          </div>
        </div>

        {/* Browser Viewport with Extension Popup Overlay */}
        <div className="p-8 min-h-[360px] bg-cyber-bg relative flex items-center justify-center">
          
          {/* Extension Popup Widget */}
          <div className="w-80 rounded-2xl bg-cyber-surface border border-cyber-cyan/50 shadow-[0_0_30px_rgba(6,182,212,0.25)] p-5 space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-cyber-border">
              <div className="flex items-center space-x-2">
                <ShieldCheck className="w-5 h-5 text-cyber-cyan" />
                <span className="font-extrabold text-xs text-white">FAKE OR REAL</span>
              </div>
              <span className="text-[10px] font-mono text-cyber-cyan">Browser Shield</span>
            </div>

            <div className="flex items-center justify-between">
              <div>
                <span className="text-[10px] font-mono uppercase text-slate-400">Concern index</span>
                <p className="text-3xl font-black font-mono text-white">{riskIndex(current.trustScore,current.riskLevel)}</p>
              </div>
              <RiskBadge level={current.riskLevel} size="sm" />
            </div>

            <div className="space-y-2 text-xs">
              <div className="p-2 rounded-lg bg-cyber-bg border border-cyber-border">
                <span className="text-slate-400 text-[10px] block font-mono">Domain Age</span>
                <strong className="text-slate-200">{current.domainAge}</strong>
              </div>

              <div className="p-2 rounded-lg bg-cyber-bg border border-cyber-border">
                <span className="text-slate-400 text-[10px] block font-mono">Payment Risk</span>
                <strong className={activeSite === 'fake' ? 'text-rose-400' : 'text-emerald-400'}>
                  {current.paymentRisk}
                </strong>
              </div>

              <div className="p-2 rounded-lg bg-cyber-bg border border-cyber-border">
                <span className="text-slate-400 text-[10px] block font-mono">Verification Status</span>
                <strong className={activeSite === 'fake' ? 'text-rose-400' : 'text-emerald-400'}>
                  {current.verificationStatus}
                </strong>
              </div>
            </div>

            <a
              href="/analyze"
              className="w-full py-2 rounded-xl bg-cyber-cyan text-slate-950 font-bold text-xs hover:bg-cyan-400 transition-colors flex items-center justify-center space-x-1"
            >
              <span>Deep Analyze Site</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </a>
          </div>

        </div>

      </div>

      {/* Real-Time Warning Modal Simulator (Requirement 47) */}
      {showWarningModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md">
          <div className="max-w-md w-full bg-cyber-bg border border-rose-500 rounded-3xl p-6 shadow-[0_0_50px_rgba(239,68,68,0.4)] text-center space-y-4">
            <div className="p-3 w-fit rounded-2xl bg-rose-500/20 text-rose-400 mx-auto border border-rose-500/40">
              <AlertOctagon className="w-10 h-10" />
            </div>
            
            <h3 className="text-xl font-extrabold text-white uppercase tracking-wider">
              ⚠ WEBSITE SECURITY WARNING
            </h3>
            
            <p className="text-xs text-rose-200 leading-relaxed">
              Multiple critical risk indicators detected on <strong>microsoft-careers-india.xyz</strong>.
              Concern index: <strong>Not run (synthetic illustration)</strong>. Synthetic illustration of an upfront-fee concern; no live extension verification is shown here.
            </p>

            <div className="p-3 rounded-xl bg-slate-900 border border-slate-800 text-left text-xs space-y-1.5 text-slate-300">
              <div className="flex items-center space-x-2 text-rose-400 font-bold">
                <span>• Brand impersonation (Microsoft)</span>
              </div>
              <div className="flex items-center space-x-2 text-rose-400 font-bold">
                <span>• Upfront payment request (₹999)</span>
              </div>
              <div className="flex items-center space-x-2 text-rose-400 font-bold">
                <span>• Disposable domain registered 11 days ago</span>
              </div>
            </div>

            <div className="pt-2 flex flex-col sm:flex-row gap-2">
              <button
                onClick={() => setShowWarningModal(false)}
                className="flex-1 py-2.5 rounded-xl bg-emerald-500 text-slate-950 font-extrabold text-xs hover:bg-emerald-400 transition-colors"
              >
                Return to Safety (Recommended)
              </button>
              <button
                onClick={() => setShowWarningModal(false)}
                className="py-2.5 px-4 rounded-xl bg-cyber-card border border-cyber-border text-slate-400 hover:text-white text-xs font-semibold"
              >
                Continue Anyway
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
