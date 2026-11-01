import { downloadReport } from '../../api/client';
import React, { useState } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { ShieldCheck, Award, X, Download, Share2, CheckCircle2, AlertOctagon, Copy, Check } from 'lucide-react';
import { RiskBadge } from './RiskBadge';
import {riskIndex} from './assessmentSemantics';

interface TrustPassportModalProps {
  scanId: string;
  opportunityName: string;
  trustScore: number|null;
  riskLevel: string;
  confidence: number;
  checksPassed: number;
  totalChecks: number;
  evidenceCount: number;
  isOpen: boolean;
  onClose: () => void;
}

export const TrustPassportModal: React.FC<TrustPassportModalProps> = ({
  scanId,
  opportunityName,
  trustScore,
  riskLevel,
  confidence,
  checksPassed,
  totalChecks,
  evidenceCount,
  isOpen,
  onClose
}) => {
  const [error, setError] = useState('');
  const [copied, setCopied] = useState(false);
  if (!isOpen) return null;

  const verificationUrl = `${window.location.origin}/trust-passport/${scanId}`;

  const handleCopyLink = () => {
    navigator.clipboard.writeText(verificationUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200"
      onClick={onClose}
    >
      <div 
        className="w-full max-w-md bg-gradient-to-b from-cyber-surface via-cyber-card to-cyber-bg border border-cyber-cyan/40 rounded-3xl shadow-[0_0_50px_rgba(6,182,212,0.25)] p-6 relative overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        
        {/* Close Button */}
        <button
          type="button"
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
          aria-label="Close Modal"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Passport Header */}
        <div className="text-center mb-6">
          <div className="inline-flex p-3 rounded-2xl bg-cyan-500/10 border border-cyber-cyan/40 text-cyber-cyan mb-2 shadow-[0_0_20px_rgba(6,182,212,0.2)]">
            <Award className="w-8 h-8 text-cyber-cyan" />
          </div>
          <h3 className="font-black text-xl tracking-wider text-white uppercase font-sans">
            DIGITAL TRUST PASSPORT
          </h3>
          <p className="text-xs font-mono text-cyan-400 mt-0.5">Recorded evidence · authenticity unresolved</p>
        </div>

        {error && <p role="alert" className="text-rose-300 text-xs">{error}</p>}
        {/* Passport Card Body */}
        <div className="p-5 rounded-2xl bg-cyber-bg/90 border border-cyber-border space-y-4">
          <div>
            <p className="text-[10px] font-mono uppercase tracking-wider text-slate-400">Target Opportunity</p>
            <p className="font-bold text-white text-base line-clamp-2 mt-0.5">{opportunityName}</p>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-2 border-t border-cyber-border/60">
            <div>
              <p className="text-[10px] font-mono uppercase text-slate-400">Concern index</p>
              <p className="text-2xl font-black font-mono text-white mt-0.5">{riskIndex(trustScore,riskLevel)}</p>
            </div>
            <div>
              <p className="text-[10px] font-mono uppercase text-slate-400">Risk Assessment</p>
              <div className="mt-1">
                <RiskBadge level={riskLevel} size="sm" />
              </div>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3 pt-2 border-t border-cyber-border/60 text-xs text-slate-300">
            <div>
              <span className="text-slate-400 block text-[10px] uppercase font-mono">Content checks completed</span>
              <span className="font-semibold text-white">{checksPassed} of {totalChecks}</span>
            </div>
            <div>
              <span className="text-slate-400 block text-[10px] uppercase font-mono">Evidence Signals</span>
              <span className="font-semibold text-white">{evidenceCount} captured</span>
            </div>
          </div>

          {/* QR Code Section */}
          <div className="pt-4 border-t border-cyber-border flex flex-col items-center">
            <div className="p-3.5 bg-white rounded-2xl shadow-xl border border-slate-200">
              <QRCodeSVG value={verificationUrl} size={130} level="H" />
            </div>
            <p className="text-[10px] font-mono text-slate-400 mt-2.5 text-center">
              Scan QR code to view the recorded evidence summary
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="mt-5 flex items-center space-x-2.5">
          <button
            onClick={() => downloadReport(scanId).catch(e => setError(e.message))}
            className="flex-1 py-2.5 px-3 rounded-xl bg-gradient-to-r from-cyan-500 via-sky-400 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-black text-xs tracking-wider uppercase transition-all flex items-center justify-center space-x-1.5 shadow-[0_0_15px_rgba(6,182,212,0.3)] cursor-pointer"
          >
            <Download className="w-4 h-4 text-slate-950" />
            <span>Download Audit PDF</span>
          </button>
          <button
            type="button"
            onClick={handleCopyLink}
            className="py-2.5 px-3.5 rounded-xl bg-cyber-card border border-cyber-border hover:border-cyber-cyan/50 text-slate-200 hover:text-white text-xs font-semibold transition-all flex items-center space-x-1.5 cursor-pointer"
          >
            {copied ? (
              <>
                <Check className="w-4 h-4 text-emerald-400" />
                <span className="text-emerald-300 font-bold">Copied!</span>
              </>
            ) : (
              <>
                <Share2 className="w-4 h-4 text-cyber-cyan" />
                <span>Share</span>
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};
