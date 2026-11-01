import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { 
  ShieldCheck, 
  AlertTriangle, 
  Bot, 
  Award, 
  Download, 
  Share2, 
  ArrowLeft, 
  Clock, 
  ExternalLink, 
  Building2, 
  Globe, 
  Zap, 
  FileText,
  AlertOctagon,
  CheckCircle2,
  Lock
} from 'lucide-react';
import { getScanById, downloadReport, ScanDetail } from '../api/client';
import { InvestigationPanel } from '../components/common/InvestigationPanel';
import { TrustScoreCircle } from '../components/common/TrustScoreCircle';
import { RiskBadge } from '../components/common/RiskBadge';
import { VerificationChecklist } from '../components/common/VerificationChecklist';
import { EvidenceCard } from '../components/common/EvidenceCard';
import { AIInvestigatorModal } from '../components/common/AIInvestigatorModal';
import { TrustPassportModal } from '../components/common/TrustPassportModal';

export const ScanResultPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [scan, setScan] = useState<ScanDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Modals state
  const [isAIModalOpen, setIsAIModalOpen] = useState(false);
  const [isPassportModalOpen, setIsPassportModalOpen] = useState(false);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    getScanById(id)
      .then((data) => {
        setScan(data);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message || "Failed to load scan");
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="flex flex-col items-center space-y-3">
          <div className="w-12 h-12 border-4 border-cyber-cyan border-t-transparent rounded-full animate-spin" />
          <p className="font-mono text-sm text-cyber-cyan">Retrieving forensic audit records...</p>
        </div>
      </div>
    );
  }

  if (error || !scan) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4 text-center">
        <div className="p-8 rounded-2xl glass-card max-w-md">
          <AlertOctagon className="w-12 h-12 text-rose-500 mx-auto mb-3" />
          <h2 className="text-xl font-bold text-white mb-2">Scan Record Not Found</h2>
          <p className="text-xs text-slate-400 mb-6">{error || "The requested scan ID does not exist."}</p>
          <Link
            to="/analyze"
            className="px-6 py-2.5 rounded-xl bg-cyber-cyan text-slate-950 font-bold text-xs"
          >
            Start New Scan
          </Link>
        </div>
      </div>
    );
  }

  const criticalFindings = scan.evidence.filter(e => e.severity === 'critical');
  const otherEvidence = scan.evidence.filter(e => e.severity !== 'critical');

  return (
    <div className="min-h-screen py-10 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8">
      
      {/* Top Breadcrumb & Action bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-cyber-border gap-4">
        <div className="flex items-center space-x-3">
          <Link
            to="/analyze"
            className="p-2 rounded-lg bg-cyber-surface border border-cyber-border text-slate-400 hover:text-white transition-colors"
            title="Back to Scanner"
          >
            <ArrowLeft className="w-4 h-4" />
          </Link>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-mono text-xs text-slate-400">Scan ID: {scan.id.slice(0, 10)}...</span>
              {scan.is_demo && (
                <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800">
                  Demo Case
                </span>
              )}
            </div>
            <h1 className="font-extrabold text-lg sm:text-xl text-white truncate max-w-xl">
              {scan.target_identifier || "Opportunity Investigation"}
            </h1>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Trust Passport trigger */}
          <button
            type="button"
            onClick={() => setIsPassportModalOpen(true)}
            className="px-4 py-2.5 rounded-xl bg-cyber-card border border-cyber-cyan/50 hover:border-cyber-cyan hover:bg-cyan-950/40 text-cyan-300 text-xs font-bold transition-all flex items-center space-x-2 shadow-[0_0_15px_rgba(6,182,212,0.2)] cursor-pointer"
          >
            <Award className="w-4 h-4 text-cyber-cyan" />
            <span>Trust Passport</span>
          </button>

          {/* AI Investigator trigger */}
          <button
            type="button"
            onClick={() => setIsAIModalOpen(true)}
            className="px-4 py-2.5 rounded-xl bg-purple-950/60 border border-purple-500/60 hover:bg-purple-900/60 hover:border-purple-400 text-purple-200 text-xs font-bold transition-all flex items-center space-x-2 shadow-[0_0_15px_rgba(139,92,246,0.25)] cursor-pointer"
          >
            <Bot className="w-4 h-4 text-purple-400" />
            <span>AI Investigator</span>
            <span className="w-2 h-2 rounded-full bg-purple-400 animate-pulse" />
          </button>

          {/* Download PDF button */}
          <button
            onClick={() => downloadReport(scan.id).catch(e => setError(e.message))}
            className="px-4 py-2.5 rounded-xl bg-gradient-to-r from-cyan-500 via-sky-400 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-black text-xs tracking-wider uppercase transition-all flex items-center space-x-2 shadow-[0_0_20px_rgba(6,182,212,0.4)] cursor-pointer"
          >
            <Download className="w-4 h-4 text-slate-950" />
            <span>Download PDF</span>
          </button>
        </div>
      </div>

      <InvestigationPanel scan={scan} onUpdate={setScan} />

      {/* Legacy baseline preserved */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Trust Score Gauge Card */}
        <div className="lg:col-span-1">
          <TrustScoreCircle
            score={scan.trust_score}
            confidence={scan.analysis_confidence}
            riskLevel={scan.risk_level}
          />
        </div>

        {/* Executive Summary & Fast Insights */}
        <div className="lg:col-span-2 p-6 rounded-2xl glass-card flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-3">
              <span className="text-xs font-mono uppercase tracking-wider text-slate-400">
                Legacy deterministic baseline
              </span>
              <RiskBadge level={scan.risk_level} size="md" />
            </div>

            <p className="text-slate-200 text-sm leading-relaxed mb-4">
              {scan.summary}
            </p>

            {/* Critical indicators pill alert if present */}
            {criticalFindings.length > 0 && (
              <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-500/50 mb-4">
                <div className="flex items-center space-x-2 text-rose-300 font-bold text-xs uppercase tracking-wider mb-2">
                  <AlertOctagon className="w-4 h-4 text-rose-400 flex-shrink-0" />
                  <span>{criticalFindings.length} Critical Risk Indicator{criticalFindings.length > 1 ? 's' : ''} Detected</span>
                </div>
                <ul className="space-y-1 text-xs text-rose-200">
                  {criticalFindings.map((cf, idx) => (
                    <li key={idx} className="flex items-start space-x-1.5">
                      <span className="text-rose-400 mt-0.5">•</span>
                      <span><strong>{cf.category.replace(/_/g, ' ').toUpperCase()}:</strong> {cf.evidence}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="pt-4 border-t border-cyber-border/80 flex flex-wrap items-center justify-between text-xs text-slate-400 gap-2">
            <div className="flex items-center space-x-2">
              <Clock className="w-3.5 h-3.5 text-slate-500" />
              <span>Analyzed: {new Date(scan.created_at).toLocaleString()}</span>
            </div>
            <div className="flex items-center space-x-2">
              <Lock className="w-3.5 h-3.5 text-cyber-cyan" />
              <span>Recorded investigation timestamp</span>
            </div>
          </div>
        </div>
      </div>

      {/* 9-Point Verification Checklist (Requirement 37) */}
      <VerificationChecklist checks={scan.verification_results} />

      {/* Main Grid: Observed Evidence Cards vs Recommended Actions */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left 2 Cols: Expandable Evidence Cards (Requirement 65 & 86) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="font-bold text-white text-lg">Observed Forensic Evidence</h2>
              <p className="text-xs text-slate-400">Click any card to expand source provenance and risk explanation</p>
            </div>
            <span className="font-mono text-xs text-cyber-cyan font-bold">
              {scan.evidence.length} Evidence Items
            </span>
          </div>

          <div className="space-y-3">
            {scan.evidence.map((ev, idx) => (
              <EvidenceCard key={idx} evidence={ev} />
            ))}
          </div>
        </div>

        {/* Right Col: Contextual Safety Recommendations & Timeline (Requirement 38 & 66) */}
        <div className="space-y-6">
          
          {/* Actionable Recommendations */}
          <div className="p-6 rounded-2xl glass-card border border-cyber-border">
            <h3 className="font-bold text-white text-base mb-1">Recommended Next Steps</h3>
            <p className="text-xs text-slate-400 mb-4">Tailored actions based on detected risk signals</p>

            <ul className="space-y-3">
              {scan.recommended_actions.map((rec, idx) => (
                <li key={idx} className="flex items-start space-x-2 text-xs text-slate-200">
                  <CheckCircle2 className="w-4 h-4 text-cyber-cyan flex-shrink-0 mt-0.5" />
                  <span className="leading-relaxed">{rec}</span>
                </li>
              ))}
            </ul>

            <div className="mt-6 pt-4 border-t border-cyber-border">
              <Link
                to="/emergency"
                className="w-full py-2.5 px-3 rounded-xl bg-rose-950/40 border border-rose-500/50 hover:bg-rose-900/50 text-rose-300 text-xs font-bold transition-colors flex items-center justify-center space-x-1.5"
              >
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>Already transferred funds or shared OTP?</span>
              </Link>
            </div>
          </div>

          {/* Analysis Sequence Timeline (Requirement 66) */}
          <div className="p-6 rounded-2xl glass-card border border-cyber-border">
            <h3 className="font-bold text-white text-base mb-1">Analysis Timeline</h3>
            <p className="text-xs text-slate-400 mb-4">Execution logs across verification modules</p>

            <div className="space-y-3 relative pl-4 border-l border-cyber-border">
              {scan.timeline.map((event, idx) => {
                let dotColor = 'bg-slate-500';
                if (event.status === 'passed') dotColor = 'bg-emerald-400';
                if (event.status === 'critical') dotColor = 'bg-rose-500 animate-ping';
                if (event.status === 'warning') dotColor = 'bg-amber-400';

                return (
                  <div key={idx} className="relative">
                    <span className={`absolute -left-[21px] top-1 w-2.5 h-2.5 rounded-full ${dotColor}`} />
                    <div className="flex items-center justify-between text-[11px] font-mono text-slate-400">
                      <span className="font-bold text-slate-300">{event.step}</span>
                      <span>{event.timestamp_str}</span>
                    </div>
                    <p className="text-xs text-slate-400 mt-0.5">{event.details}</p>
                  </div>
                );
              })}
            </div>
          </div>

        </div>
      </div>

      {/* AI Investigator Modal */}
      <AIInvestigatorModal
        scanId={scan.id}
        isOpen={isAIModalOpen}
        onClose={() => setIsAIModalOpen(false)}
      />

      {/* Trust Passport Modal */}
      <TrustPassportModal
        scanId={scan.id}
        opportunityName={scan.target_identifier || "Analyzed Opportunity"}
        trustScore={scan.trust_score}
        riskLevel={scan.risk_level}
        confidence={scan.analysis_confidence}
        checksPassed={scan.verification_results.filter(c => ['passed','verified'].includes(c.status)).length}
        totalChecks={scan.verification_results.length || 9}
        evidenceCount={scan.evidence.length}
        isOpen={isPassportModalOpen}
        onClose={() => setIsPassportModalOpen(false)}
      />
    </div>
  );
};
