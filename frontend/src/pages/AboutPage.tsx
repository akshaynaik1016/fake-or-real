import React from 'react';
import { Info, ShieldCheck, Cpu, Terminal, Users, CheckCircle2, AlertTriangle } from 'lucide-react';

export const AboutPage: React.FC = () => {
  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto space-y-8">
      
      <div className="text-center space-y-2">
        <div className="inline-flex p-3 rounded-2xl bg-cyber-cyan/10 border border-cyber-cyan/40 text-cyber-cyan mb-2">
          <Info className="w-8 h-8" />
        </div>
        <h1 className="text-3xl font-extrabold text-white">About UNMASK</h1>
        <p className="text-xs sm:text-sm text-slate-400 max-w-xl mx-auto font-mono">
          Evidence-Based Digital Trust & Safety Platform • Track: Safety Tech
        </p>
      </div>

      <div className="space-y-6 text-xs sm:text-sm text-slate-300 leading-relaxed">
        
        {/* Core Product Principle (Requirement 99) */}
        <div className="p-6 rounded-2xl glass-card border border-cyber-cyan/50 bg-cyber-surface/80 space-y-3 shadow-[0_0_25px_rgba(6,182,212,0.15)]">
          <h2 className="font-bold text-white text-base">The Core Product Principle</h2>
          <div className="p-4 rounded-xl bg-cyber-bg border border-cyber-border text-slate-200 space-y-2">
            <p className="font-semibold text-rose-300">
              ✕ The platform is NOT: "An LLM guessing whether something is a scam."
            </p>
            <p className="font-semibold text-emerald-400">
              ✓ The platform IS: "An AI system that helps users understand evidence collected from multiple independent verification systems so they can make safer decisions before they click or pay."
            </p>
          </div>
          <p className="text-xs text-slate-400 leading-relaxed">
            By grounding every risk assessment in observable forensic checks (DNS records, domain age, SSL certificate details, corporate registry matches, payment rail detection, and threat intelligence), we eliminate AI hallucination and provide verifiable proof for every score.
          </p>
        </div>

        {/* The Problem */}
        <div className="p-6 rounded-2xl glass-card border border-cyber-border space-y-3">
          <h2 className="font-bold text-white text-base">The Problem We Solve</h2>
          <p>
            Students and young professionals are targeted daily by fraudulent internship notifications, scholarship schemes,
            and task-based freelance scams across WhatsApp, Telegram, and LinkedIn. Fraudsters frequently impersonate recognized
            brands (like Microsoft, Google, TCS) using lookalike domains, demanding "refundable registration fees" or harvesting
            Aadhaar and PAN details.
          </p>
        </div>

        {/* Technology Stack */}
        <div className="p-6 rounded-2xl glass-card border border-cyber-border space-y-3">
          <h2 className="font-bold text-white text-base">Technology Stack</h2>
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3 font-mono text-xs text-slate-300">
            <div className="p-3 rounded-xl bg-cyber-bg border border-cyber-border">
              <strong className="text-cyber-cyan block mb-1">Frontend</strong>
              <span>React, TypeScript, Vite, Tailwind CSS, Framer Motion, Recharts</span>
            </div>
            <div className="p-3 rounded-xl bg-cyber-bg border border-cyber-border">
              <strong className="text-cyber-cyan block mb-1">Backend</strong>
              <span>FastAPI, Python 3.12, Pydantic, SQLAlchemy, dnspython</span>
            </div>
            <div className="p-3 rounded-xl bg-cyber-bg border border-cyber-border">
              <strong className="text-cyber-cyan block mb-1">Forensics & OCR</strong>
              <span>pypdf, ReportLab, Tesseract/PaddleOCR pipeline, scikit-learn</span>
            </div>
          </div>
        </div>

        {/* Limitations & Responsible AI */}
        <div className="p-6 rounded-2xl glass-card border border-cyber-border space-y-3">
          <h2 className="font-bold text-white text-base">Limitations & Responsible AI Statement</h2>
          <p className="text-xs text-slate-400 leading-relaxed">
            Automated assessments can be wrong. The Trust Score is an algorithmic decision aid based on observable risk indicators,
            not a formal legal certificate of authenticity or fraud. High-impact decisions should always be independently confirmed
            by directly contacting the organization through verified public channels.
          </p>
        </div>

      </div>

    </div>
  );
};
