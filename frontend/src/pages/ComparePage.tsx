import React, { useState } from 'react';
import { GitCompare, ArrowRight, ShieldCheck, AlertOctagon, CheckCircle2, XCircle, AlertTriangle, Download, RefreshCw, Check } from 'lucide-react';
import { RiskBadge } from '../components/common/RiskBadge';

interface OpportunityData {
  title: string;
  organization: string;
  domain: string;
  trustScore: number;
  riskLevel: string;
  confidence: number;
  upfrontFee: string;
  sensitiveData: string;
  threatIntel: string;
  recruiterChannel: string;
  verdict: string;
}

interface PresetPair {
  id: string;
  label: string;
  oppA: OpportunityData;
  oppB: OpportunityData;
}

const PRESET_PAIRS: PresetPair[] = [
  {
    id: "tech-recruitment",
    label: "TCS NextStep vs Fake Microsoft Internship",
    oppA: {
      title: "TCS NextStep National Qualifier Drive 2026",
      organization: "Tata Consultancy Services Limited",
      domain: "nextstep.tcs.com (Official tcs.com parent)",
      trustScore: 94,
      riskLevel: "LOW RISK",
      confidence: 96,
      upfrontFee: "None (Strict Zero-Fee Corporate Policy)",
      sensitiveData: "Standard Resume & College Marksheet",
      threatIntel: "Clean across 24 global threat intelligence feeds",
      recruiterChannel: "Official Enterprise Portal (tcs.com / nextstep)",
      verdict: "Authentic enterprise infrastructure with verified MCA corporate registry and standard hiring lifecycle."
    },
    oppB: {
      title: "Microsoft AI Summer Internship Offer",
      organization: "Claimed: Microsoft Corporation",
      domain: "microsoft-careers-india.xyz (Unverified .xyz disposable)",
      trustScore: 18,
      riskLevel: "CRITICAL RISK",
      confidence: 94,
      upfrontFee: "₹999 Refundable Laptop Deposit via UPI",
      sensitiveData: "Aadhaar Card, PAN Card, Live Bank Details",
      threatIntel: "Blacklisted on abuse feeds & newly registered domain",
      recruiterChannel: "Personal WhatsApp Recruiter (+91 98765 43210)",
      verdict: "Classic advance-fee recruitment scam impersonating Microsoft. Harvests identity credentials and UPI deposits."
    }
  },
  {
    id: "freelance-scam",
    label: "Infosys Campus Hiring vs Telegram Typing Scam",
    oppA: {
      title: "Infosys InfyTQ Certification & Specialist Programmer",
      organization: "Infosys Limited",
      domain: "infytq.onwingspan.com (Verified Enterprise Tenant)",
      trustScore: 91,
      riskLevel: "LOW RISK",
      confidence: 95,
      upfrontFee: "Free of Cost for all eligible students",
      sensitiveData: "Student ID, Academic Transcripts",
      threatIntel: "Zero threat detections across all monitors",
      recruiterChannel: "Campus Placement Cell & Official Platform",
      verdict: "Legitimate enterprise certification with secure authentication and zero monetary demand."
    },
    oppB: {
      title: "Work-From-Home Typing & Data Entry Executive",
      organization: "Direct Career Solutions (Unregistered Entity)",
      domain: "typing-job-portal.top (Anonymous .top domain)",
      trustScore: 24,
      riskLevel: "HIGH RISK",
      confidence: 92,
      upfrontFee: "₹1,499 Mandatory Software License Activation",
      sensitiveData: "Bank Account Number, Signature JPEG",
      threatIntel: "Known template matching 18 recurring phishing kits",
      recruiterChannel: "Telegram Channel (@FastTypingJobsIndia)",
      verdict: "Advance-fee task scam with salary exaggeration (₹5,000/day) and unrecoverable registration fee demands."
    }
  },
  {
    id: "scholarship-scam",
    label: "Google Scholarship vs $250 Advance-Fee Fraud",
    oppA: {
      title: "Generation Google Scholarship (APAC)",
      organization: "Google LLC / Alphabet Inc.",
      domain: "buildyourfuture.withgoogle.com (Official Google)",
      trustScore: 97,
      riskLevel: "LOW RISK",
      confidence: 98,
      upfrontFee: "Zero application fee or processing charges",
      sensitiveData: "Essay Responses, Resume, Recommendation Letters",
      threatIntel: "Verified EV SSL & Authorized Google Infrastructure",
      recruiterChannel: "Official Google Student Portal",
      verdict: "High-trust philanthropic program on Google primary domain with rigorous identity verification."
    },
    oppB: {
      title: "Global Youth Merit Scholarship Award ($5,000)",
      organization: "International Education Foundation (Unregistered)",
      domain: "scholarship-portal-gov.online (Deceptive .online)",
      trustScore: 12,
      riskLevel: "CRITICAL RISK",
      confidence: 96,
      upfrontFee: "$250 International Wire Clearance Fee",
      sensitiveData: "Passport Scan, Bank Account, OTP Validation",
      threatIntel: "Multiple reports of credential harvesting and identity theft",
      recruiterChannel: "Cold Phishing Email (awards@scholarship-portal-gov.online)",
      verdict: "High-risk lottery/scholarship fraud utilizing deceptive gov naming to solicit upfront fees."
    }
  }
];

export const ComparePage: React.FC = () => {
  const [selectedPresetId, setSelectedPresetId] = useState<string>("tech-recruitment");
  const [exportedToast, setExportedToast] = useState(false);

  const currentPreset = PRESET_PAIRS.find(p => p.id === selectedPresetId) || PRESET_PAIRS[0];
  const { oppA, oppB } = currentPreset;
  const scoreDiff = oppA.trustScore - oppB.trustScore;

  const handleExport = () => {
    setExportedToast(true);
    setTimeout(() => setExportedToast(false), 3000);
  };

  return (
    <div className="min-h-screen py-10 px-4 sm:px-6 lg:px-8 max-w-6xl mx-auto space-y-8">
      
      {/* Header */}
      <div className="text-center">
        <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-cyber-cyan/10 border border-cyber-cyan/40 mb-3 text-cyber-cyan text-xs font-mono font-bold">
          <GitCompare className="w-4 h-4" />
          <span>SIDE-BY-SIDE FORENSIC COMPARISON ENGINE</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white">
          Multi-Opportunity Trust Differential
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-2 max-w-2xl mx-auto leading-relaxed">
          Directly evaluate two opportunities side-by-side to expose discrepancies in corporate registration,
          domain infrastructure, upfront payment traps, and threat intelligence.
        </p>

        {/* Preset Selector Chips */}
        <div className="flex flex-wrap items-center justify-center gap-2 pt-5">
          <span className="text-[11px] font-mono text-slate-400 uppercase mr-1">Demo Scenarios:</span>
          {PRESET_PAIRS.map((preset) => (
            <button
              key={preset.id}
              onClick={() => setSelectedPresetId(preset.id)}
              className={`px-3.5 py-1.5 rounded-full text-xs font-mono transition-all ${
                selectedPresetId === preset.id
                  ? 'bg-cyber-cyan text-slate-950 font-extrabold shadow-[0_0_15px_rgba(6,182,212,0.4)]'
                  : 'bg-cyber-surface/80 border border-cyber-border text-slate-300 hover:border-cyber-cyan/60 hover:text-white'
              }`}
            >
              {preset.label}
            </button>
          ))}
        </div>
      </div>

      {/* Delta Callout Banner */}
      <div className="p-4 rounded-2xl bg-cyber-surface/90 border border-cyber-cyan/40 shadow-[0_0_25px_rgba(6,182,212,0.15)] flex flex-col sm:flex-row items-center justify-between gap-4">
        <div className="flex items-center space-x-3 text-center sm:text-left">
          <div className="w-10 h-10 rounded-xl bg-cyber-cyan/20 border border-cyber-cyan/40 text-cyber-cyan flex items-center justify-center font-mono font-black text-sm flex-shrink-0">
            +{scoreDiff}
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-bold text-white text-sm">Trust Score Differential</span>
              <span className="px-2 py-0.5 rounded text-[10px] font-mono uppercase bg-emerald-950/80 text-emerald-400 border border-emerald-500/50">
                Opportunity A Favored
              </span>
            </div>
            <p className="text-xs text-slate-300 mt-0.5">
              Opportunity A maintains a <strong>+{scoreDiff} point forensic advantage</strong> with zero upfront fees and verified enterprise domain ownership.
            </p>
          </div>
        </div>

        <button 
          onClick={handleExport}
          className="px-4 py-2 rounded-xl bg-cyber-card border border-cyber-border hover:border-cyber-cyan text-white text-xs font-bold transition-all flex items-center space-x-1.5 flex-shrink-0"
        >
          {exportedToast ? (
            <>
              <Check className="w-4 h-4 text-emerald-400" />
              <span className="text-emerald-400">Exported to Audit Log</span>
            </>
          ) : (
            <>
              <Download className="w-4 h-4 text-cyber-cyan" />
              <span>Export Comparison PDF</span>
            </>
          )}
        </button>
      </div>

      {/* Comparison Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        
        {/* Opportunity A Card (Verified) */}
        <div className="p-6 rounded-3xl glass-card border border-emerald-500/50 relative overflow-hidden bg-gradient-to-b from-emerald-950/20 to-transparent">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-mono uppercase px-3 py-1 rounded-full bg-emerald-950/80 text-emerald-400 font-extrabold border border-emerald-500/50 flex items-center space-x-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>OPPORTUNITY A (VERIFIED)</span>
            </span>
            <RiskBadge level={oppA.riskLevel} size="sm" />
          </div>

          <h3 className="font-extrabold text-xl text-white mb-1">{oppA.title}</h3>
          <p className="text-xs text-slate-400 font-mono mb-5">{oppA.organization}</p>

          <div className="flex items-center justify-between p-4 rounded-2xl bg-cyber-bg border border-cyber-border mb-6">
            <div>
              <span className="text-[10px] font-mono uppercase text-slate-400">Trust Score</span>
              <p className="text-4xl font-black font-mono text-emerald-400">{oppA.trustScore}<span className="text-sm font-normal text-slate-400">/100</span></p>
            </div>
            <div className="text-right">
              <span className="text-[10px] font-mono uppercase text-slate-400">Forensic Confidence</span>
              <p className="text-base font-bold text-cyber-cyan font-mono">{oppA.confidence}%</p>
              <span className="text-[10px] text-emerald-400 font-mono">High Grounding</span>
            </div>
          </div>

          <div className="space-y-3 text-xs">
            <div className="p-3.5 rounded-xl bg-cyber-surface/80 border border-cyber-border">
              <span className="text-slate-400 block text-[10px] uppercase font-mono">Domain Infrastructure</span>
              <span className="font-bold text-emerald-400 flex items-center space-x-1.5 mt-0.5">
                <CheckCircle2 className="w-3.5 h-3.5 flex-shrink-0 text-emerald-400" />
                <span className="break-all">{oppA.domain}</span>
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-cyber-surface/80 border border-cyber-border">
              <span className="text-slate-400 block text-[10px] uppercase font-mono">Upfront Fees / Deposit</span>
              <span className="font-bold text-emerald-400 flex items-center space-x-1.5 mt-0.5">
                <CheckCircle2 className="w-3.5 h-3.5 flex-shrink-0 text-emerald-400" />
                <span>{oppA.upfrontFee}</span>
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-cyber-surface/80 border border-cyber-border">
              <span className="text-slate-400 block text-[10px] uppercase font-mono">Requested Information</span>
              <span className="font-medium text-slate-200 block mt-0.5">{oppA.sensitiveData}</span>
            </div>

            <div className="p-3.5 rounded-xl bg-cyber-surface/80 border border-cyber-border">
              <span className="text-slate-400 block text-[10px] uppercase font-mono">Threat Intelligence</span>
              <span className="font-medium text-slate-200 block mt-0.5">{oppA.threatIntel}</span>
            </div>

            <div className="p-3.5 rounded-xl bg-cyber-surface/80 border border-cyber-border">
              <span className="text-slate-400 block text-[10px] uppercase font-mono">Recruiter Channel</span>
              <span className="font-medium text-slate-200 block mt-0.5">{oppA.recruiterChannel}</span>
            </div>
          </div>
        </div>

        {/* Opportunity B Card (Suspicious) */}
        <div className="p-6 rounded-3xl glass-card border border-rose-500/50 relative overflow-hidden bg-gradient-to-b from-rose-950/20 to-transparent">
          <div className="flex items-center justify-between mb-4">
            <span className="text-xs font-mono uppercase px-3 py-1 rounded-full bg-rose-950/80 text-rose-400 font-extrabold border border-rose-500/50 flex items-center space-x-1.5">
              <AlertOctagon className="w-3.5 h-3.5 text-rose-400" />
              <span>OPPORTUNITY B (SUSPICIOUS)</span>
            </span>
            <RiskBadge level={oppB.riskLevel} size="sm" />
          </div>

          <h3 className="font-extrabold text-xl text-white mb-1">{oppB.title}</h3>
          <p className="text-xs text-slate-400 font-mono mb-5">{oppB.organization}</p>

          <div className="flex items-center justify-between p-4 rounded-2xl bg-cyber-bg border border-cyber-border mb-6">
            <div>
              <span className="text-[10px] font-mono uppercase text-slate-400">Trust Score</span>
              <p className="text-4xl font-black font-mono text-rose-400">{oppB.trustScore}<span className="text-sm font-normal text-slate-400">/100</span></p>
            </div>
            <div className="text-right">
              <span className="text-[10px] font-mono uppercase text-slate-400">Forensic Confidence</span>
              <p className="text-base font-bold text-cyber-cyan font-mono">{oppB.confidence}%</p>
              <span className="text-[10px] text-rose-400 font-mono">Critical Red Flags</span>
            </div>
          </div>

          <div className="space-y-3 text-xs">
            <div className="p-3.5 rounded-xl bg-rose-950/25 border border-rose-500/40">
              <span className="text-slate-400 block text-[10px] uppercase font-mono">Domain Infrastructure</span>
              <span className="font-bold text-rose-400 flex items-center space-x-1.5 mt-0.5">
                <XCircle className="w-3.5 h-3.5 flex-shrink-0 text-rose-400" />
                <span className="break-all">{oppB.domain}</span>
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-rose-950/25 border border-rose-500/40">
              <span className="text-slate-400 block text-[10px] uppercase font-mono">Upfront Fees / Deposit</span>
              <span className="font-bold text-rose-400 flex items-center space-x-1.5 mt-0.5">
                <AlertOctagon className="w-3.5 h-3.5 flex-shrink-0 text-rose-400" />
                <span>{oppB.upfrontFee}</span>
              </span>
            </div>

            <div className="p-3.5 rounded-xl bg-cyber-surface/80 border border-cyber-border">
              <span className="text-slate-400 block text-[10px] uppercase font-mono">Requested Information</span>
              <span className="font-medium text-amber-300 block mt-0.5">{oppB.sensitiveData}</span>
            </div>

            <div className="p-3.5 rounded-xl bg-cyber-surface/80 border border-cyber-border">
              <span className="text-slate-400 block text-[10px] uppercase font-mono">Threat Intelligence</span>
              <span className="font-medium text-rose-300 block mt-0.5">{oppB.threatIntel}</span>
            </div>

            <div className="p-3.5 rounded-xl bg-cyber-surface/80 border border-cyber-border">
              <span className="text-slate-400 block text-[10px] uppercase font-mono">Recruiter Channel</span>
              <span className="font-medium text-rose-300 block mt-0.5">{oppB.recruiterChannel}</span>
            </div>
          </div>
        </div>

      </div>

      {/* Forensic Verdict Callout */}
      <div className="p-6 rounded-2xl glass-card bg-cyber-surface/80 border border-cyber-border space-y-3">
        <div className="flex items-center space-x-2">
          <ShieldCheck className="w-5 h-5 text-cyber-cyan" />
          <h4 className="font-bold text-white text-base">Comprehensive Forensic Verdict</h4>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-500/30">
            <strong className="text-emerald-400 block font-mono text-[11px] mb-1">OPPORTUNITY A ANALYSIS:</strong>
            <p className="text-slate-300 leading-relaxed">{oppA.verdict}</p>
          </div>
          <div className="p-3.5 rounded-xl bg-rose-950/20 border border-rose-500/30">
            <strong className="text-rose-400 block font-mono text-[11px] mb-1">OPPORTUNITY B RED FLAGS:</strong>
            <p className="text-slate-300 leading-relaxed">{oppB.verdict}</p>
          </div>
        </div>
      </div>

    </div>
  );
};
