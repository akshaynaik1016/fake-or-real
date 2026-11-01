import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ShieldCheck, 
  Search, 
  UploadCloud, 
  FileText, 
  AlertTriangle, 
  CheckCircle2, 
  Lock, 
  Globe, 
  Zap, 
  Eye, 
  ArrowRight,
  Database,
  Terminal,
  Cpu,
  Sparkles,
  Award,
  AlertOctagon,
  Copy,
  Check
} from 'lucide-react';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [quickInput, setQuickInput] = useState('');
  const [copiedPreset, setCopiedPreset] = useState<string | null>(null);

  const handleQuickSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!quickInput.trim()) return;
    navigate(`/analyze?q=${encodeURIComponent(quickInput.trim())}`);
  };

  const handlePresetSelect = (presetText: string, presetName: string) => {
    setQuickInput(presetText);
    setCopiedPreset(presetName);
    setTimeout(() => {
      navigate(`/analyze?preset=${presetName}`);
    }, 400);
  };

  return (
    <div className="relative overflow-hidden bg-cyber-bg min-h-screen">
      {/* Background Cyber Grid & Ambient Glowing Orbs */}
      <div className="absolute inset-0 bg-cyber-grid bg-[size:36px_36px] pointer-events-none opacity-30" />
      <div className="absolute top-12 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-gradient-to-tr from-cyan-600/15 via-blue-600/15 to-purple-600/10 rounded-full blur-[140px] pointer-events-none" />

      {/* Hero Section */}
      <section className="relative pt-20 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto text-center">
        
        {/* Verification Status Pill */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="inline-flex items-center space-x-2.5 px-4 py-1.5 rounded-full bg-cyber-surface/90 border border-cyber-cyan/40 mb-6 shadow-[0_0_20px_rgba(6,182,212,0.2)]"
        >
          <span className="flex h-2 w-2 rounded-full bg-cyber-cyan animate-ping" />
          <span className="text-xs font-mono font-semibold text-slate-200 tracking-wide uppercase">
            THREAT RADAR ACTIVE • AI FORENSIC ENGINE v2.4
          </span>
          <span className="text-xs text-cyber-cyan font-bold font-mono">
            [ONLINE]
          </span>
        </motion.div>

        {/* Main Heading */}
        <motion.h1 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="text-5xl sm:text-7xl font-black tracking-tight text-white max-w-4xl mx-auto leading-tight"
        >
          FAKE OR REAL
          <span className="block mt-2 text-3xl sm:text-5xl bg-gradient-to-r from-cyan-400 via-sky-300 to-indigo-400 bg-clip-text text-transparent font-black tracking-normal">
            Don't trust. Verify.
          </span>
        </motion.h1>

        {/* Subtitle */}
        <motion.p 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="mt-5 text-base sm:text-xl text-slate-300 max-w-3xl mx-auto leading-relaxed font-normal"
        >
          Investigate internship offers, recruitment texts, scholarships, and lookalike domains with 
          independent multi-layer cybersecurity forensics. <span className="text-cyber-cyan font-semibold">Before you click. Before you pay. Verify.</span>
        </motion.p>

        {/* Interactive Quick-Scan Hero Bar */}
        <motion.div 
          initial={{ opacity: 0, y: 25 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="mt-8 max-w-2xl mx-auto"
        >
          <form onSubmit={handleQuickSubmit} className="relative flex items-center p-1.5 rounded-2xl bg-cyber-surface/90 border border-cyber-cyan/40 shadow-[0_0_30px_rgba(6,182,212,0.18)] hover:border-cyber-cyan transition-all">
            <div className="flex items-center pl-3 pr-2 text-slate-400">
              <Globe className="w-5 h-5 text-cyber-cyan flex-shrink-0" />
            </div>
            <input
              type="text"
              value={quickInput}
              onChange={(e) => setQuickInput(e.target.value)}
              placeholder="Paste suspicious website, recruiter message, or opportunity text..."
              className="w-full bg-transparent text-sm text-white placeholder-slate-400 focus:outline-none pr-3 font-sans py-2"
            />
            <button
              type="submit"
              className="px-5 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-black text-xs tracking-wider uppercase transition-all shadow-[0_0_15px_rgba(6,182,212,0.3)] flex items-center space-x-1.5 flex-shrink-0 cursor-pointer"
            >
              <span>Scan Now</span>
              <ArrowRight className="w-3.5 h-3.5 text-slate-950" />
            </button>
          </form>

          {/* Quick Benchmark Presets */}
          <div className="mt-3 flex flex-wrap items-center justify-center gap-2 text-[11px]">
            <span className="text-slate-400 font-mono">Instant Presets:</span>
            <button
              type="button"
              onClick={() => handlePresetSelect('https://microsoft-careers-india.xyz/apply', 'fake_internship')}
              className="px-2.5 py-1 rounded-lg bg-rose-950/50 hover:bg-rose-900/60 border border-rose-500/40 text-rose-300 font-medium transition-colors flex items-center space-x-1"
            >
              <AlertOctagon className="w-3 h-3 text-rose-400" />
              <span>Fake MSFT Internship (₹999 fee)</span>
            </button>
            <button
              type="button"
              onClick={() => handlePresetSelect('https://nextstep.tcs.com/campus/#/register', 'genuine_tcs')}
              className="px-2.5 py-1 rounded-lg bg-emerald-950/50 hover:bg-emerald-900/60 border border-emerald-500/40 text-emerald-300 font-medium transition-colors flex items-center space-x-1"
            >
              <CheckCircle2 className="w-3 h-3 text-emerald-400" />
              <span>Genuine TCS NQT Drive</span>
            </button>
            <button
              type="button"
              onClick={() => handlePresetSelect('https://google.com.security-check.example.xyz', 'phishing_link')}
              className="px-2.5 py-1 rounded-lg bg-amber-950/50 hover:bg-amber-900/60 border border-amber-500/40 text-amber-300 font-medium transition-colors flex items-center space-x-1"
            >
              <Zap className="w-3 h-3 text-amber-400" />
              <span>Lookalike Phishing URL</span>
            </button>
          </div>
        </motion.div>

        {/* Primary CTAs */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="mt-8 flex flex-wrap items-center justify-center gap-4"
        >
          <Link
            to="/analyze"
            className="px-7 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-black text-sm tracking-wide shadow-[0_0_25px_rgba(6,182,212,0.4)] transition-all transform hover:-translate-y-0.5 flex items-center space-x-2"
          >
            <Search className="w-4 h-4 text-slate-950" />
            <span>Launch Full Scanner</span>
            <ArrowRight className="w-4 h-4 text-slate-950" />
          </Link>

          <Link
            to="/demo"
            className="px-6 py-3 rounded-xl bg-cyber-card border border-cyber-cyan/40 hover:border-cyber-cyan text-white font-bold text-sm tracking-wide transition-all flex items-center space-x-2 shadow-sm"
          >
            <Sparkles className="w-4 h-4 text-cyber-cyan" />
            <span>Judge 1-Click Demo Hub</span>
          </Link>

          <Link
            to="/emergency"
            className="px-6 py-3 rounded-xl bg-rose-950/40 border border-rose-500/50 hover:bg-rose-900/50 text-rose-300 font-bold text-sm tracking-wide transition-all flex items-center space-x-2 shadow-[0_0_15px_rgba(244,63,94,0.2)]"
          >
            <AlertTriangle className="w-4 h-4 text-rose-400" />
            <span>I Already Clicked</span>
          </Link>
        </motion.div>

        {/* Quick Modal Upload CTAs */}
        <div className="mt-6 flex flex-wrap items-center justify-center gap-3 text-xs text-slate-400">
          <span className="font-mono text-slate-400">Quick Upload:</span>
          <button 
            onClick={() => navigate('/analyze?tab=screenshot')}
            className="px-3 py-1.5 rounded-lg bg-cyber-surface border border-cyber-border hover:border-cyber-cyan/40 text-slate-300 hover:text-white transition-colors flex items-center space-x-1.5"
          >
            <UploadCloud className="w-3.5 h-3.5 text-cyber-cyan" />
            <span>Upload Screenshot (OCR)</span>
          </button>
          <button 
            onClick={() => navigate('/analyze?tab=pdf')}
            className="px-3 py-1.5 rounded-lg bg-cyber-surface border border-cyber-border hover:border-cyber-cyan/40 text-slate-300 hover:text-white transition-colors flex items-center space-x-1.5"
          >
            <FileText className="w-3.5 h-3.5 text-cyber-cyan" />
            <span>Upload Offer Letter (PDF)</span>
          </button>
          <Link 
            to="/about"
            className="px-3 py-1.5 rounded-lg bg-cyber-surface border border-cyber-border hover:border-cyber-cyan/40 text-slate-300 hover:text-white transition-colors"
          >
            How It Works
          </Link>
        </div>
      </section>

      {/* Cyber Defense Telemetry Bar */}
      <section className="px-4 sm:px-6 lg:px-8 max-w-6xl mx-auto mb-16">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 rounded-2xl glass-card border border-cyber-border/80 text-center font-mono">
          <div className="p-2 border-r border-cyber-border/50">
            <span className="text-[10px] uppercase text-slate-400 block">Verification Layers</span>
            <span className="text-xl sm:text-2xl font-black text-cyber-cyan">9 Phases</span>
          </div>
          <div className="p-2 border-r border-cyber-border/50">
            <span className="text-[10px] uppercase text-slate-400 block">Grounding Reliability</span>
            <span className="text-xl sm:text-2xl font-black text-emerald-400">100% Deterministic</span>
          </div>
          <div className="p-2 border-r border-cyber-border/50">
            <span className="text-[10px] uppercase text-slate-400 block">Threat Signatures</span>
            <span className="text-xl sm:text-2xl font-black text-white">4,800+ Known</span>
          </div>
          <div className="p-2">
            <span className="text-[10px] uppercase text-slate-400 block">Containment Speed</span>
            <span className="text-xl sm:text-2xl font-black text-rose-400">&lt; 3 Seconds</span>
          </div>
        </div>
      </section>

      {/* Live Forensic Detection Architecture Section */}
      <section className="px-4 sm:px-6 lg:px-8 max-w-6xl mx-auto mb-20">
        <div className="p-6 sm:p-8 rounded-3xl glass-card glow-border shadow-2xl relative">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between pb-6 border-b border-cyber-border gap-4">
            <div>
              <div className="flex items-center space-x-2">
                <Terminal className="w-5 h-5 text-cyber-cyan" />
                <h2 className="text-lg font-bold text-white">Live Forensic Detection Architecture</h2>
              </div>
              <p className="text-xs text-slate-400 mt-1">Multi-layer evaluation without simple binary LLM claims</p>
            </div>
            <div className="flex items-center space-x-3">
              <span className="text-xs font-mono text-emerald-400 bg-emerald-950/40 border border-emerald-500/40 px-3 py-1 rounded-full flex items-center space-x-1.5">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                <span>Zero Hallucination Grounding</span>
              </span>
            </div>
          </div>

          {/* 4 Architecture Pillars */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mt-6">
            <div className="p-4 rounded-xl bg-cyber-bg/60 border border-cyber-border hover:border-cyber-cyan/40 transition-colors">
              <div className="flex items-center space-x-2 text-cyber-cyan mb-2">
                <Globe className="w-4 h-4" />
                <h3 className="font-bold text-sm text-slate-200">Domain & DNS</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                RDAP domain age checks, registrar history, MX, SPF, DMARC, and lookalike homograph analysis.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-cyber-bg/60 border border-cyber-border hover:border-cyber-cyan/40 transition-colors">
              <div className="flex items-center space-x-2 text-cyber-cyan mb-2">
                <ShieldCheck className="w-4 h-4" />
                <h3 className="font-bold text-sm text-slate-200">Identity Cross-Check</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Matches claimed corporate entities against bundled organization references and known career domains; this does not authenticate an offer.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-cyber-bg/60 border border-cyber-border hover:border-cyber-cyan/40 transition-colors">
              <div className="flex items-center space-x-2 text-cyber-cyan mb-2">
                <Zap className="w-4 h-4" />
                <h3 className="font-bold text-sm text-slate-200">Payment Risk Engine</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Detects upfront registration fees, security deposits, UPI handles, crypto addresses, and gift cards.
              </p>
            </div>

            <div className="p-4 rounded-xl bg-cyber-bg/60 border border-cyber-border hover:border-cyber-cyan/40 transition-colors">
              <div className="flex items-center space-x-2 text-cyber-cyan mb-2">
                <Cpu className="w-4 h-4" />
                <h3 className="font-bold text-sm text-slate-200">Document & OCR</h3>
              </div>
              <p className="text-xs text-slate-400 leading-relaxed">
                Inspects screenshot regions and PDF metadata for consumer toolkit tampering and sensitive data harvesting.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Feature Showcase Grid */}
      <section className="px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto pb-24">
        <div className="text-center mb-14">
          <h2 className="text-3xl font-extrabold text-white">
            Built Specifically For Student & Job Seeker Safety
          </h2>
          <p className="text-sm text-slate-400 mt-2 max-w-2xl mx-auto">
            Traditional antivirus programs scan for malware. FAKE OR REAL investigates social engineering,
            fake recruiters, advance-fee scams, and brand impersonation.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 rounded-2xl glass-card flex flex-col justify-between hover:border-cyber-cyan/40 transition-all">
            <div>
              <div className="p-3 w-fit rounded-xl bg-cyber-cyan/10 border border-cyber-cyan/30 text-cyber-cyan mb-4">
                <Search className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-lg text-white mb-2">Multi-Input Unified Scanner</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Paste raw URLs, emails, WhatsApp messages, Telegram alerts, or upload screenshots and offer letter PDFs.
                Our OCR and document engines extract and parse text securely.
              </p>
            </div>
            <Link to="/analyze" className="mt-6 text-xs font-bold text-cyber-cyan hover:underline flex items-center space-x-1">
              <span>Open Scanner</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="p-6 rounded-2xl glass-card flex flex-col justify-between hover:border-rose-500/40 transition-all">
            <div>
              <div className="p-3 w-fit rounded-xl bg-rose-500/10 border border-rose-500/30 text-rose-400 mb-4">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-lg text-white mb-2">"I Already Clicked" Emergency Mode</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Already submitted an OTP, UPI PIN, password, or transferred money? Get immediate, actionable crisis containment
                steps with direct links to official cyber fraud reporting helplines (1930 / cybercrime.gov.in).
              </p>
            </div>
            <Link to="/emergency" className="mt-6 text-xs font-bold text-rose-400 hover:underline flex items-center space-x-1">
              <span>Access Emergency Guidance</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          <div className="p-6 rounded-2xl glass-card flex flex-col justify-between hover:border-purple-500/40 transition-all">
            <div>
              <div className="p-3 w-fit rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-400 mb-4">
                <Cpu className="w-6 h-6" />
              </div>
              <h3 className="font-bold text-lg text-white mb-2">Evidence-Grounded AI Investigator</h3>
              <p className="text-xs text-slate-400 leading-relaxed">
                Ask interactive questions like "Why is this domain risky?" or "Is Microsoft real?"
                The conversational assistant is bound to recorded evidence, with deterministic fallback and explicit uncertainty.
              </p>
            </div>
            <Link to="/analyze" className="mt-6 text-xs font-bold text-purple-400 hover:underline flex items-center space-x-1">
              <span>Try with an Opportunity</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};
