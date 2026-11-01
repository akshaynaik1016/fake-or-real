import { fetchJson, downloadReport } from '../api/client';
import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { QRCodeSVG } from 'qrcode.react';
import { Award, ShieldCheck, CheckCircle2, Download, ArrowLeft, Lock, Globe } from 'lucide-react';
import { RiskBadge } from '../components/common/RiskBadge';

export const TrustPassportPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [error, setError] = useState('');
  const [passport, setPassport] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchJson(`/trust-passport/${id || 'demo-fake-msft-internship'}`)
      .then(data => {
        setPassport(data);
        setLoading(false);
      })
      .catch(e => { setError(e.message); setLoading(false); });
  }, [id]);

  if (error) return <p role="alert" className="p-8 text-rose-300">{error}</p>;
  if (loading || !passport) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <span className="font-mono text-xs text-cyber-cyan">Retrieving recorded evidence summary...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen py-12 px-4 sm:px-6 lg:px-8 max-w-2xl mx-auto space-y-6">
      
      <Link
        to={passport.scan_id ? `/scan/${passport.scan_id}` : "/analyze"}
        className="inline-flex items-center space-x-1.5 text-xs text-slate-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-3.5 h-3.5" />
        <span>Back to Full Audit Report</span>
      </Link>

      {/* Verified Certificate Card */}
      <div className="p-8 rounded-3xl glass-card border border-cyber-cyan/50 shadow-[0_0_50px_rgba(6,182,212,0.2)] text-center relative overflow-hidden">
        
        <div className="inline-flex p-3.5 rounded-2xl bg-cyber-cyan/10 border border-cyber-cyan/40 text-cyber-cyan mb-3 shadow-[0_0_20px_rgba(6,182,212,0.25)]">
          <Award className="w-10 h-10" />
        </div>

        <h1 className="text-2xl font-black uppercase tracking-wider text-white">
          Digital Trust Passport
        </h1>
        <p className="text-xs font-mono text-cyber-cyan mt-0.5">
          Recorded evidence summary · legacy baseline
        </p>

        {/* Certificate Body */}
        <div className="mt-6 p-6 rounded-2xl bg-cyber-bg/90 border border-cyber-border text-left space-y-4">
          <div>
            <span className="text-[10px] font-mono uppercase text-slate-400 block">Opportunity Target</span>
            <p className="text-base font-bold text-white mt-0.5">{passport.opportunity_name}</p>
          </div>

          <div className="grid grid-cols-2 gap-4 pt-3 border-t border-cyber-border/60">
            <div>
              <span className="text-[10px] font-mono uppercase text-slate-400 block">Trust Score</span>
              <p className="text-3xl font-black font-mono text-white mt-0.5">{passport.trust_score}/100</p>
            </div>
            <div>
              <span className="text-[10px] font-mono uppercase text-slate-400 block">Risk Tier</span>
              <div className="mt-1">
                <RiskBadge level={passport.risk_level} size="sm" />
              </div>
            </div>
          </div>

          <div className="pt-3 border-t border-cyber-border/60 text-xs text-slate-300">
            <span className="text-[10px] font-mono uppercase text-slate-400 block mb-1">Audit Summary</span>
            <p className="leading-relaxed bg-cyber-surface/60 p-3 rounded-xl border border-cyber-border/60">
              {passport.verification_summary}
            </p>
          </div>

          {/* QR Code */}
          <div className="pt-4 border-t border-cyber-border/60 flex flex-col items-center">
            <div className="p-3 bg-white rounded-2xl shadow-lg">
              <QRCodeSVG value={window.location.href} size={140} level="H" />
            </div>
            <p className="text-[11px] font-mono text-slate-400 mt-2 text-center">
              Scan QR code to view the recorded evidence summary
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="mt-6 flex items-center justify-center space-x-3">
          <button
            onClick={() => downloadReport(passport.scan_id).catch(e => setError(e.message))}
            className="px-6 py-2.5 rounded-xl bg-cyber-cyan text-slate-950 font-bold text-xs hover:bg-cyan-400 transition-colors flex items-center space-x-2 shadow-md"
          >
            <Download className="w-4 h-4" />
            <span>Download Audit PDF</span>
          </button>
        </div>

      </div>

    </div>
  );
};
