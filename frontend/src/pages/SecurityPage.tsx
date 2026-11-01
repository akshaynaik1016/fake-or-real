import React from 'react';
import { ShieldCheck, Lock, AlertTriangle, Cpu, Terminal, EyeOff, Server, FileCheck } from 'lucide-react';

export const SecurityPage: React.FC = () => {
  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto space-y-8">
      
      <div className="text-center space-y-2">
        <div className="inline-flex p-3 rounded-2xl bg-cyber-cyan/10 border border-cyber-cyan/40 text-cyber-cyan mb-2">
          <ShieldCheck className="w-8 h-8" />
        </div>
        <h1 className="text-3xl font-extrabold text-white">Security Architecture & Defensive Engineering</h1>
        <p className="text-xs sm:text-sm text-slate-400 max-w-xl mx-auto">
          Comprehensive overview of SSRF mitigation, prompt injection boundaries, document validation, and zero-trust engineering.
        </p>
      </div>

      <div className="space-y-6 text-xs sm:text-sm text-slate-300 leading-relaxed">
        
        {/* Pillar 1: SSRF Defense */}
        <div className="p-6 rounded-2xl glass-card border border-cyber-border space-y-3">
          <div className="flex items-center space-x-2 text-cyber-cyan font-bold text-base">
            <Server className="w-5 h-5" />
            <h2>Mandatory Server-Side Request Forgery (SSRF) Protection</h2>
          </div>
          <p>
            Before fetching or resolving external URLs, the platform enforces strict network boundaries:
          </p>
          <ul className="list-disc list-inside space-y-1.5 text-slate-400 font-mono text-xs">
            <li>Blocks loopback destinations (<code className="text-cyber-cyan">127.0.0.1</code>, <code className="text-cyber-cyan">localhost</code>, <code className="text-cyber-cyan">::1</code>)</li>
            <li>Blocks private RFC 1918 subnets (<code className="text-cyber-cyan">10.0.0.0/8</code>, <code className="text-cyber-cyan">172.16.0.0/12</code>, <code className="text-cyber-cyan">192.168.0.0/16</code>)</li>
            <li>Blocks cloud metadata endpoints (<code className="text-cyber-cyan">169.254.169.254</code> AWS/GCP metadata services)</li>
            <li>Enforces pre-flight DNS resolution and detects DNS rebinding attempts before network socket connection</li>
          </ul>
        </div>

        {/* Pillar 2: Prompt Injection Defense */}
        <div className="p-6 rounded-2xl glass-card border border-cyber-border space-y-3">
          <div className="flex items-center space-x-2 text-cyber-cyan font-bold text-base">
            <Cpu className="w-5 h-5" />
            <h2>AI Prompt Injection & Instruction Containment</h2>
          </div>
          <p>
            All submitted webpages, OCR extractions, and PDF documents are treated as untrusted external data:
          </p>
          <ul className="list-disc list-inside space-y-1.5 text-slate-400 text-xs">
            <li>Untrusted text is passed inside strict isolated XML delimiter fences</li>
            <li>Text is scanned for adversarial prompt injection signatures (e.g. "ignore previous instructions", "developer mode")</li>
            <li>The AI Investigator operates purely in read-only analysis mode and cannot trigger arbitrary tool actions</li>
          </ul>
        </div>

        {/* Pillar 3: Document Security */}
        <div className="p-6 rounded-2xl glass-card border border-cyber-border space-y-3">
          <div className="flex items-center space-x-2 text-cyber-cyan font-bold text-base">
            <FileCheck className="w-5 h-5" />
            <h2>Document Sanitization & Magic-Byte Validation</h2>
          </div>
          <p>
            Uploads are validated through three independent layers:
          </p>
          <ul className="list-disc list-inside space-y-1.5 text-slate-400 text-xs">
            <li>File extensions are strictly allowlisted (.png, .jpg, .webp, .pdf, .txt, .eml)</li>
            <li>Binary streams are validated against magic byte headers (<code className="text-cyber-cyan">%PDF</code>, <code className="text-cyber-cyan">\x89PNG</code>, <code className="text-cyber-cyan">\xff\xd8\xff</code>)</li>
            <li>Hard 10MB file size limit enforced to prevent resource exhaustion attacks</li>
            <li>Files are processed in memory / temporary isolated storage and automatically scheduled for deletion</li>
          </ul>
        </div>

      </div>

    </div>
  );
};
