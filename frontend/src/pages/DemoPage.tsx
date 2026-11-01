import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, ArrowRight, ShieldCheck, AlertOctagon, AlertTriangle, Zap, CheckCircle2, Loader2, Search, Filter } from 'lucide-react';
import { runDemoCase } from '../api/client';
import { RiskBadge } from '../components/common/RiskBadge';

export const DemoPage: React.FC = () => {
  const navigate = useNavigate();
  const [loadingCaseId, setLoadingCaseId] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const demoCases = [
    {
      id: "demo-fake-msft-internship",
      title: "Fake Microsoft AI Internship (Benchmark)",
      expectedRisk: "CRITICAL RISK",
      category: "internship",
      badge: "Master Judge Test",
      description: "Claims to be a Microsoft AI Internship offering ₹45,000/month for 2 hours daily work. Demands ₹999 refundable laptop deposit via UPI and harvests Aadhaar/PAN cards.",
      domain: "microsoft-careers-india.xyz",
      highlights: ["Organization Mismatch", "₹999 Registration Fee", "Aadhaar/PAN Harvesting", "Urgency Pressure"],
      latency: "1.6s"
    },
    {
      id: "demo-genuine-tcs-opportunity",
      title: "Synthetic TCS NextStep comparison",
      expectedRisk: "UNDETERMINED",
      category: "internship",
      badge: "Legitimate Baseline",
      description: "Synthetic comparison using a bundled domain reference. No live corporate registry, sender or offer authorization is asserted.",
      domain: "nextstep.tcs.com",
      highlights: ["Official Domain Verified", "Synthetic DNS / TLS fixtures", "Zero Fee Requirement", "Bundled reference match"],
      latency: "1.2s"
    },
    {
      id: "demo-fake-google-scholarship",
      title: "Fake Google Generation Scholarship",
      expectedRisk: "CRITICAL RISK",
      category: "scholarship",
      badge: "Advance-Fee Fraud",
      description: "Claims an award of $5,000 scholarship, but requires a $250 international dispatch fee via wire/crypto and requests OTP verification.",
      domain: "scholarship-portal-gov.online",
      highlights: ["$250 Upfront Fee", "OTP Harvesting", "Disposable .online Domain", "Counterfeit CA"],
      latency: "1.4s"
    },
    {
      id: "demo-phishing-upi-portal",
      title: "Banking / UPI KYC Suspension Phishing",
      expectedRisk: "CRITICAL RISK",
      category: "phishing",
      badge: "Phishing & Credential Theft",
      description: "Simulated credential harvesting portal on a disposable .top domain mimicking national banking portals to steal passwords and ATM PINs.",
      domain: "sbi-kyc-update-alert.quick-internships-direct.top",
      highlights: ["Lookalike Hostname", "Entropy Obfuscation", "PIN Request", "Synthetic threat fixture"],
      latency: "1.5s"
    },
    {
      id: "demo-freelance-deposit-scam",
      title: "Freelance SMS / Typing Security Deposit Scam",
      expectedRisk: "HIGH RISK",
      category: "freelance",
      badge: "Work-From-Home Hook",
      description: "Advertises ₹3,000-5,000/day for copying text with no experience. Demands ₹1,499 refundable software deposit to an unverified WhatsApp recruiter.",
      domain: "Direct Work Solutions",
      highlights: ["Salary Anomaly", "₹1,499 Activation Fee", "Unverified Recruiter", "Template Overlap"],
      latency: "1.3s"
    }
  ];

  const filteredCases = demoCases.filter(c => {
    const matchesCategory = selectedCategory === 'all' || c.category === selectedCategory;
    const matchesSearch = !searchQuery.trim() || 
      c.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.domain.toLowerCase().includes(searchQuery.toLowerCase()) ||
      c.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const handleRunCase = async (caseId: string) => {
    setLoadingCaseId(caseId);
    setErrorMessage(null);
    try {
      const res = await runDemoCase(caseId);
      navigate(`/scan/${res.id}`);
    } catch (e: any) {
      setErrorMessage(`Error running forensic demo test: ${e.message}`);
      setLoadingCaseId(null);
    }
  };

  return (
    <div className="min-h-screen py-10 px-4 sm:px-6 lg:px-8 max-w-5xl mx-auto space-y-8">
      <a href="/challenge" className="block rounded-xl p-4 border border-cyan-500 text-cyan-200">Open Evidence Challenge — run three synthetic cases through the real pipeline</a>
      <p className="p-4 text-amber-200 text-sm">Synthetic demonstration offers. Fixture findings are labelled and excluded from evidence fusion. Tavily is live only when configured; no LLM is required.</p>
      
      {/* Banner */}
      <div className="text-center">
        <div className="inline-flex items-center space-x-2 px-3.5 py-1.5 rounded-full bg-cyber-cyan/10 border border-cyber-cyan/40 mb-4 shadow-[0_0_15px_rgba(6,182,212,0.2)]">
          <Sparkles className="w-4 h-4 text-cyber-cyan" />
          <span className="text-xs font-mono font-bold text-cyber-cyan uppercase tracking-wider">
            Deterministic Forensic Test Benchmark
          </span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-extrabold text-white">
          Hackathon 1-Click Evaluation Hub
        </h1>
        <p className="text-xs sm:text-sm text-slate-400 mt-2 max-w-xl mx-auto leading-relaxed">
          Run the deterministic workflow without API keys. Synthetic fixtures are labelled; external verification is shown only when performed.
        </p>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-2xl glass-card border border-cyber-border flex flex-col sm:flex-row items-center justify-between gap-3">
        <div className="flex flex-wrap items-center gap-1.5 w-full sm:w-auto">
          {[
            { id: 'all', label: 'All Benchmarks (5)' },
            { id: 'internship', label: 'Internships & Jobs' },
            { id: 'scholarship', label: 'Scholarships' },
            { id: 'phishing', label: 'Phishing Portals' },
            { id: 'freelance', label: 'Work From Home' },
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setSelectedCategory(tab.id)}
              className={`px-3 py-1.5 rounded-xl text-xs font-mono transition-all ${
                selectedCategory === tab.id
                  ? 'bg-cyber-cyan text-slate-950 font-extrabold shadow-[0_0_10px_rgba(6,182,212,0.3)]'
                  : 'bg-cyber-bg border border-cyber-border text-slate-300 hover:text-white'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="relative w-full sm:w-64">
          <Search className="w-3.5 h-3.5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search test cases..."
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-cyber-bg border border-cyber-border rounded-xl text-white placeholder-slate-500 focus:outline-none focus:border-cyber-cyan"
          />
        </div>
      </div>

      {errorMessage && (
        <div className="p-4 rounded-xl bg-rose-950/60 border border-rose-500/60 text-rose-300 text-xs flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-4 h-4 text-rose-400 flex-shrink-0" />
            <span>{errorMessage}</span>
          </div>
          <button onClick={() => setErrorMessage(null)} className="text-rose-400 hover:text-white font-mono text-xs">
            Dismiss
          </button>
        </div>
      )}

      {/* Demo Cards Grid */}
      <div className="space-y-4">
        {filteredCases.map((c) => {
          const isLoading = loadingCaseId === c.id;
          return (
            <div 
              key={c.id}
              className="p-6 rounded-2xl glass-card border border-cyber-border hover:border-cyber-cyan/50 transition-all flex flex-col sm:flex-row items-start sm:items-center justify-between gap-6"
            >
              <div className="space-y-2 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className="text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-bold border border-slate-700">
                    {c.badge}
                  </span>
                  <RiskBadge level={c.expectedRisk} size="sm" />
                  <span className="text-xs font-mono text-slate-400 truncate max-w-xs">{c.domain}</span>
                  <span className="text-[10px] font-mono text-cyber-cyan ml-auto sm:ml-0 bg-cyber-cyan/10 px-2 py-0.5 rounded border border-cyber-cyan/20">
                    Synthetic scenario
                  </span>
                </div>

                <h3 className="font-bold text-lg text-white">{c.title}</h3>
                <p className="text-xs text-slate-300 leading-relaxed max-w-2xl">{c.description}</p>

                <div className="flex flex-wrap gap-1.5 pt-1">
                  {c.highlights.map((h, i) => (
                    <span key={i} className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyber-bg text-slate-300 border border-cyber-border">
                      • {h}
                    </span>
                  ))}
                </div>
              </div>

              <div className="flex-shrink-0 w-full sm:w-auto">
                <button
                  onClick={() => handleRunCase(c.id)}
                  disabled={isLoading}
                  className="w-full sm:w-auto px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-400 to-blue-500 hover:from-cyan-300 hover:to-blue-400 text-slate-950 font-black text-xs tracking-wider uppercase shadow-[0_0_20px_rgba(6,182,212,0.4)] transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-4 h-4 animate-spin text-slate-950" />
                      <span>Executing Scan Pipeline...</span>
                    </>
                  ) : (
                    <>
                      <span>Run Verification</span>
                      <ArrowRight className="w-4 h-4 text-slate-950" />
                    </>
                  )}
                </button>
              </div>
            </div>
          );
        })}
      </div>

    </div>
  );
};
