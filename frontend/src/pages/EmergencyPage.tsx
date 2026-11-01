import React, { useState } from 'react';
import { 
  AlertTriangle, 
  Key, 
  CreditCard, 
  ShieldAlert, 
  Send, 
  Download, 
  FileCheck, 
  Globe, 
  PhoneCall, 
  CheckCircle2, 
  ArrowRight,
  ShieldCheck,
  ExternalLink,
  Copy,
  Check
} from 'lucide-react';
import { fetchEmergencyGuidance } from '../api/client';

export const EmergencyPage: React.FC = () => {
  const [selectedIncident, setSelectedIncident] = useState('sent_money');
  const [guidance, setGuidance] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [completedSteps, setCompletedSteps] = useState<Record<number, boolean>>({});
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const incidents = [
    { id: 'sent_money', label: 'I Sent Money / Paid a Fee', icon: Send, severity: 'CRITICAL', color: 'text-rose-400' },
    { id: 'shared_otp', label: 'I Shared an OTP / Auth Code', icon: ShieldAlert, severity: 'CRITICAL', color: 'text-rose-400' },
    { id: 'shared_upi_pin', label: 'I Entered My UPI PIN', icon: Key, severity: 'CRITICAL', color: 'text-rose-400' },
    { id: 'entered_password', label: 'I Entered My Password', icon: Key, severity: 'CRITICAL', color: 'text-rose-400' },
    { id: 'entered_card', label: 'I Entered Card Details / CVV', icon: CreditCard, severity: 'CRITICAL', color: 'text-rose-400' },
    { id: 'downloaded_file', label: 'I Downloaded an APK / File', icon: Download, severity: 'HIGH', color: 'text-amber-400' },
    { id: 'shared_aadhaar_pan', label: 'I Uploaded Aadhaar / PAN', icon: FileCheck, severity: 'HIGH', color: 'text-amber-400' },
    { id: 'opened_website', label: 'I Only Visited the Link', icon: Globe, severity: 'MODERATE', color: 'text-cyan-400' },
  ];

  const handleSelectIncident = async (id: string) => {
    setSelectedIncident(id);
    setLoading(true);
    setCompletedSteps({});
    try {
      const res = await fetchEmergencyGuidance(id);
      setGuidance(res);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  const toggleStep = (stepOrder: number) => {
    setCompletedSteps(prev => ({
      ...prev,
      [stepOrder]: !prev[stepOrder]
    }));
  };

  const copyToClipboard = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2500);
  };

  // Load default on mount
  React.useEffect(() => {
    handleSelectIncident('sent_money');
  }, []);

  const totalSteps = guidance?.immediate_steps?.length || 0;
  const completedCount = Object.values(completedSteps).filter(Boolean).length;
  const progressPercent = totalSteps > 0 ? Math.round((completedCount / totalSteps) * 100) : 0;

  return (
    <div className="min-h-screen py-10 px-4 sm:px-6 lg:px-8 max-w-6xl mx-auto space-y-8">
      
      {/* Emergency Header Banner */}
      <div className="p-6 rounded-3xl bg-rose-950/50 border border-rose-500/70 shadow-[0_0_35px_rgba(244,63,94,0.2)] flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6">
        <div className="flex items-start space-x-4">
          <div className="p-3.5 rounded-2xl bg-rose-500/20 border border-rose-500/50 text-rose-400 flex-shrink-0 animate-pulse">
            <AlertTriangle className="w-8 h-8" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-[10px] font-mono uppercase px-2.5 py-0.5 rounded-full bg-rose-500 text-slate-950 font-black tracking-widest">
                CRITICAL INCIDENT RESPONSE
              </span>
              <span className="text-xs text-rose-300 font-mono">Triage Engine v2.4</span>
            </div>
            <h1 className="text-2xl sm:text-3xl font-black text-white uppercase tracking-wide mt-1">
              "I Already Clicked" — Containment Protocol
            </h1>
            <p className="text-xs sm:text-sm text-rose-200 mt-1 max-w-2xl leading-relaxed">
              If you transferred money, submitted credentials, or shared an OTP, execute these containment steps immediately.
              Every minute helps prevent unauthorized withdrawals or account compromise.
            </p>
          </div>
        </div>

        <div className="sm:text-right flex-shrink-0 w-full sm:w-auto p-4 rounded-2xl bg-slate-950/80 border border-rose-500/40">
          <span className="text-[10px] font-mono uppercase text-slate-400 block">National Cyber Fraud Helpline</span>
          <div className="flex items-center justify-start sm:justify-end space-x-2 mt-1">
            <span className="text-2xl font-black font-mono text-rose-400">1930</span>
            <button
              onClick={() => copyToClipboard('1930', 'helpline-1930')}
              className="p-1.5 rounded-lg bg-cyber-card border border-cyber-border hover:border-cyber-cyan text-slate-300 hover:text-white"
              title="Copy Helpline Number"
            >
              {copiedKey === 'helpline-1930' ? (
                <Check className="w-3.5 h-3.5 text-emerald-400" />
              ) : (
                <Copy className="w-3.5 h-3.5" />
              )}
            </button>
          </div>
          <span className="text-[10px] text-slate-400 block mt-0.5">Toll-free 24x7 Emergency Assistance</span>
        </div>
      </div>

      {/* Main Layout: Incident Selector Grid + Action Steps */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left Col: What happened selector */}
        <div className="space-y-2">
          <h2 className="text-xs font-mono uppercase tracking-widest text-slate-400 px-1 mb-2">
            Select Your Exact Scenario:
          </h2>
          {incidents.map((inc) => {
            const Icon = inc.icon;
            const isSelected = selectedIncident === inc.id;
            return (
              <button
                key={inc.id}
                onClick={() => handleSelectIncident(inc.id)}
                className={`w-full text-left p-3.5 rounded-xl border flex items-center justify-between transition-all ${
                  isSelected
                    ? 'bg-cyber-card border-rose-500 text-white shadow-[0_0_15px_rgba(244,63,94,0.25)]'
                    : 'bg-cyber-surface/60 border-cyber-border text-slate-300 hover:bg-cyber-surface hover:text-white'
                }`}
              >
                <div className="flex items-center space-x-3">
                  <Icon className={`w-4 h-4 ${inc.color}`} />
                  <span className="text-xs font-semibold">{inc.label}</span>
                </div>
                <span className={`text-[9px] font-mono font-bold uppercase px-1.5 py-0.5 rounded ${
                  inc.severity === 'CRITICAL' ? 'bg-rose-950 text-rose-400 border border-rose-800' : 'bg-slate-800 text-slate-300'
                }`}>
                  {inc.severity}
                </span>
              </button>
            );
          })}
        </div>

        {/* Right 2 Cols: Step-by-Step Emergency Protocol */}
        <div className="lg:col-span-2 space-y-6">
          {loading || !guidance ? (
            <div className="p-12 rounded-2xl glass-card flex items-center justify-center">
              <span className="font-mono text-xs text-cyber-cyan animate-pulse">Loading containment protocol...</span>
            </div>
          ) : (
            <div className="p-6 rounded-2xl glass-card border border-cyber-border space-y-6">
              
              {/* Containment Headline & Progress */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-cyber-border">
                <div>
                  <div className="flex items-center space-x-2">
                    <h3 className="font-bold text-white text-lg">{guidance.headline}</h3>
                    <span className="px-2.5 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-rose-950/80 text-rose-400 border border-rose-500/50">
                      {guidance.severity} PRIORITY
                    </span>
                  </div>
                  <p className="text-xs text-slate-400 mt-1">Check off containment actions as you execute them:</p>
                </div>

                <div className="sm:text-right flex-shrink-0">
                  <span className="text-xs font-mono font-bold text-white">
                    {completedCount} of {totalSteps} Completed ({progressPercent}%)
                  </span>
                  <div className="w-36 h-2 bg-slate-800 rounded-full mt-1 overflow-hidden border border-slate-700">
                    <div 
                      className="h-full bg-gradient-to-r from-cyan-400 to-emerald-400 transition-all duration-300"
                      style={{ width: `${progressPercent}%` }}
                    />
                  </div>
                </div>
              </div>

              {/* Warning Alert Note */}
              <p className="text-xs text-rose-200 bg-rose-950/40 p-3.5 rounded-xl border border-rose-500/40 leading-relaxed">
                <strong className="text-rose-400 uppercase font-mono mr-1">Emergency Warning:</strong>
                {guidance.caution_note}
              </p>

              {/* Action Steps Checklist */}
              <div className="space-y-3">
                <h4 className="text-xs font-mono uppercase tracking-wider text-slate-400">
                  Step-by-Step Containment Protocol:
                </h4>
                {guidance.immediate_steps.map((st: any) => {
                  const isDone = !!completedSteps[st.order];
                  return (
                    <div 
                      key={st.order}
                      onClick={() => toggleStep(st.order)}
                      className={`p-4 rounded-xl border transition-all cursor-pointer flex items-start space-x-3.5 ${
                        isDone 
                          ? 'bg-emerald-950/20 border-emerald-500/50 opacity-80' 
                          : 'bg-cyber-bg border-cyber-border hover:border-cyber-cyan/50'
                      }`}
                    >
                      <div className={`w-7 h-7 rounded-full font-mono font-bold text-xs flex items-center justify-center flex-shrink-0 transition-colors ${
                        isDone
                          ? 'bg-emerald-500 text-slate-950 shadow-[0_0_10px_rgba(16,185,129,0.4)]'
                          : 'bg-cyber-card border border-cyber-cyan/50 text-cyber-cyan'
                      }`}>
                        {isDone ? <Check className="w-4 h-4 stroke-[3]" /> : st.order}
                      </div>

                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <p className={`font-bold text-sm ${isDone ? 'text-emerald-300 line-through' : 'text-white'}`}>
                            {st.action}
                          </p>
                          <span className="text-[9px] font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                            {st.priority}
                          </span>
                        </div>
                        <p className="text-xs text-slate-300 mt-1 leading-relaxed">
                          {st.instructions}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Official Helplines Reference */}
              <div className="p-4 rounded-xl bg-cyber-surface/80 border border-cyber-border space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2 text-cyber-cyan">
                    <PhoneCall className="w-4 h-4" />
                    <h4 className="font-bold text-xs uppercase tracking-wider text-slate-200">
                      Official Emergency Helpline Registry
                    </h4>
                  </div>
                  <span className="text-[10px] font-mono text-slate-400">Click to copy</span>
                </div>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                  {Object.entries(guidance.helpline_numbers).map(([name, num], idx) => {
                    const isCopied = copiedKey === `helpline-${idx}`;
                    return (
                      <div 
                        key={idx} 
                        onClick={() => copyToClipboard(String(num), `helpline-${idx}`)}
                        className="p-2.5 rounded-lg bg-cyber-bg/90 border border-cyber-border hover:border-cyber-cyan/60 transition-all flex items-center justify-between cursor-pointer"
                      >
                        <span className="text-slate-400 truncate max-w-[150px]">{name}:</span>
                        <div className="flex items-center space-x-1.5">
                          <strong className="text-cyber-cyan font-mono">{String(num)}</strong>
                          {isCopied ? (
                            <Check className="w-3.5 h-3.5 text-emerald-400" />
                          ) : (
                            <Copy className="w-3.5 h-3.5 text-slate-500 hover:text-white" />
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>

              {/* External Cybercrime Reporting CTA */}
              <div className="p-4 rounded-xl bg-gradient-to-r from-blue-950/30 to-cyan-950/30 border border-cyber-cyan/30 flex flex-col sm:flex-row items-center justify-between gap-3">
                <div>
                  <h5 className="font-bold text-xs text-white uppercase tracking-wider">File Official Complaint with Cyber Police</h5>
                  <p className="text-[11px] text-slate-400 mt-0.5">National Cyber Crime Reporting Portal (MHA Government of India)</p>
                </div>
                <a
                  href="https://cybercrime.gov.in"
                  target="_blank"
                  rel="noopener noreferrer"
                  className="px-4 py-2 rounded-xl bg-cyber-cyan text-slate-950 font-bold text-xs hover:bg-cyan-400 transition-colors flex items-center space-x-1.5 flex-shrink-0"
                >
                  <span>Visit cybercrime.gov.in</span>
                  <ExternalLink className="w-3.5 h-3.5" />
                </a>
              </div>

            </div>
          )}
        </div>

      </div>

    </div>
  );
};
