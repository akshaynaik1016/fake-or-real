import { API_BASE } from '../../api/client';
import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck, Lock, EyeOff, Info, Globe, Cpu } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-cyber-border bg-cyber-bg/95 pt-12 pb-8 text-slate-400 text-xs">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Responsible AI Disclaimer Banner */}
        <div className="p-4 rounded-xl bg-cyber-surface/60 border border-cyber-border/80 mb-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
          <div className="flex items-start space-x-3">
            <Cpu className="w-5 h-5 text-cyber-cyan flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-semibold text-slate-200 text-sm">Responsible AI & Verification Principle</p>
              <p className="text-slate-400 mt-0.5 leading-relaxed">
                FAKE OR REAL does not make unsupported accusations. Automated assessments evaluate observable cybersecurity signals,
                identity cross-checks, and language patterns to help you verify opportunities before you click or pay.
              </p>
            </div>
          </div>
          <Link
            to="/about"
            className="px-3 py-1.5 rounded-lg text-xs font-medium text-cyber-cyan bg-cyber-cyan/10 border border-cyber-cyan/30 hover:bg-cyber-cyan/20 transition-colors whitespace-nowrap"
          >
            How It Works
          </Link>
        </div>

        {/* Footer Columns */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
          <div>
            <div className="flex items-center space-x-2 text-white font-bold mb-3">
              <ShieldCheck className="w-4 h-4 text-cyber-cyan" />
              <span>FAKE OR REAL</span>
            </div>
            <p className="text-slate-400 leading-relaxed mb-3">
              Evidence-based digital trust & safety platform protecting students and job seekers against online scams.
            </p>
            <p className="font-mono text-[11px] text-cyber-cyan">Don't trust. Verify.</p>
          </div>

          <div>
            <p className="font-semibold text-slate-200 mb-3 uppercase tracking-wider text-[11px]">Investigation</p>
            <ul className="space-y-2">
              <li><Link to="/analyze" className="hover:text-cyber-cyan transition-colors">Unified Scanner</Link></li>
              <li><Link to="/compare" className="hover:text-cyber-cyan transition-colors">Opportunity Comparison</Link></li>
              <li><Link to="/emergency" className="hover:text-rose-400 transition-colors">I Already Clicked (Emergency)</Link></li>
              <li><Link to="/community" className="hover:text-cyber-cyan transition-colors">Community Scam Feed</Link></li>
            </ul>
          </div>

          <div>
            <p className="font-semibold text-slate-200 mb-3 uppercase tracking-wider text-[11px]">Integrations & Tools</p>
            <ul className="space-y-2">
              <li><Link to="/demo" className="hover:text-cyber-cyan transition-colors">Judge 1-Click Demo Hub</Link></li>
              <li><Link to="/extension" className="hover:text-cyber-cyan transition-colors">Browser Extension Preview</Link></li>
              <li><Link to="/settings" className="hover:text-cyber-cyan transition-colors">Scoring Weights Config</Link></li>
              <li><a href={`${API_BASE.replace(/\/api$/, '')}/docs`} target="_blank" rel="noreferrer" className="hover:text-cyber-cyan transition-colors">OpenAPI Documentation</a></li>
            </ul>
          </div>

          <div>
            <p className="font-semibold text-slate-200 mb-3 uppercase tracking-wider text-[11px]">Trust & Transparency</p>
            <ul className="space-y-2">
              <li><Link to="/security" className="hover:text-cyber-cyan transition-colors">Security Architecture</Link></li>
              <li><Link to="/privacy" className="hover:text-cyber-cyan transition-colors">Privacy & Data Minimization</Link></li>
              <li><Link to="/about" className="hover:text-cyber-cyan transition-colors">About & Limitations</Link></li>
              <li><Link to="/admin" className="hover:text-cyber-cyan transition-colors">Admin Governance</Link></li>
            </ul>
          </div>
        </div>

        {/* Bottom copyright */}
        <div className="pt-6 border-t border-cyber-border/60 flex flex-col sm:flex-row items-center justify-between text-slate-400">
          <p>© 2026 FAKE OR REAL. Built for Safety Tech Hackathon. All rights reserved.</p>
          <p className="mt-2 sm:mt-0 font-mono text-[11px] text-slate-400">
            Isolated Sandbox • SSRF Guard • Prompt Injection Protected
          </p>
        </div>
      </div>
    </footer>
  );
};
