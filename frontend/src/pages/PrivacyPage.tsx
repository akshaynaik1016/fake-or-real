import React from 'react';
import { EyeOff, ShieldCheck, Lock, Trash2, Database, Key } from 'lucide-react';

export const PrivacyPage: React.FC = () => {
  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto space-y-8">
      
      <div className="text-center space-y-2">
        <div className="inline-flex p-3 rounded-2xl bg-cyber-cyan/10 border border-cyber-cyan/40 text-cyber-cyan mb-2">
          <EyeOff className="w-8 h-8" />
        </div>
        <h1 className="text-3xl font-extrabold text-white">Privacy Policy & Data Minimization</h1>
        <p className="text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
          We practice strict data minimization. We only collect the minimal observable indicators required to assess online risk.
        </p>
      </div>

      <div className="space-y-6 text-xs sm:text-sm text-slate-300 leading-relaxed">
        
        <div className="p-6 rounded-2xl glass-card border border-cyber-border space-y-3">
          <h2 className="font-bold text-white text-base">1. What Information is Collected</h2>
          <p>
            When you submit an opportunity for verification, our engines extract:
          </p>
          <ul className="list-disc list-inside space-y-1 text-slate-400 text-xs">
            <li>Target URLs and domain hostnames</li>
            <li>Claimed organization names and recruiter email domains</li>
            <li>Public phone numbers extracted from the submission</li>
            <li>Linguistic markers, requested fee amounts, and document metadata</li>
          </ul>
          <p className="font-semibold text-rose-300 text-xs bg-rose-950/30 p-2.5 rounded-lg border border-rose-500/30 mt-2">
            We NEVER log or store private credentials, passwords, OTPs, CVVs, or UPI PINs. Any credentials detected in submitted text are immediately redacted prior to processing.
          </p>
        </div>

        <div className="p-6 rounded-2xl glass-card border border-cyber-border space-y-3">
          <h2 className="font-bold text-white text-base">2. How Uploaded Files are Handled</h2>
          <p>
            Uploaded offer letters (PDF) and screenshots (PNG, JPG) are analyzed strictly in temporary memory buffers:
          </p>
          <ul className="list-disc list-inside space-y-1 text-slate-400 text-xs">
            <li>Raw uploaded files are not stored indefinitely</li>
            <li>Temporary file buffers are scheduled for automatic purge</li>
            <li>Only non-sensitive metadata (file size, SHA-256 hash, extracted text) is stored for repeat lookup caching</li>
          </ul>
        </div>

        <div className="p-6 rounded-2xl glass-card border border-cyber-border space-y-3">
          <h2 className="font-bold text-white text-base">3. Community Reporting Privacy</h2>
          <p>
            Community reports are published anonymously without exposing your personal email address, IP address, or identity.
            All reports undergo moderation before being aggregated into community reputation signals.
          </p>
        </div>

      </div>

    </div>
  );
};
