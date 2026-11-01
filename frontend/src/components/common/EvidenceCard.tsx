import React, { useState } from 'react';
import { ChevronDown, ChevronUp, AlertOctagon, AlertTriangle, Info, CheckCircle, Database } from 'lucide-react';
import { EvidenceItem } from '../../api/client';

interface EvidenceCardProps {
  evidence: EvidenceItem;
}

export const EvidenceCard: React.FC<EvidenceCardProps> = ({ evidence }) => {
  const [expanded, setExpanded] = useState(false);
  const sev = evidence.severity.toLowerCase();

  let badgeColor = 'bg-emerald-950/40 text-emerald-400 border-emerald-500/40';
  let Icon = CheckCircle;
  let borderHighlight = 'hover:border-emerald-500/50';

  if (sev === 'critical') {
    badgeColor = 'bg-rose-950/60 text-rose-400 border-rose-500/60';
    Icon = AlertOctagon;
    borderHighlight = 'hover:border-rose-500/60';
  } else if (sev === 'high') {
    badgeColor = 'bg-rose-950/30 text-rose-300 border-rose-500/40';
    Icon = AlertTriangle;
    borderHighlight = 'hover:border-rose-400/50';
  } else if (sev === 'moderate') {
    badgeColor = 'bg-amber-950/40 text-amber-400 border-amber-500/40';
    Icon = AlertTriangle;
    borderHighlight = 'hover:border-amber-500/50';
  } else if (sev === 'low') {
    badgeColor = 'bg-slate-800 text-slate-300 border-slate-700';
    Icon = Info;
  }

  return (
    <div id={`evidence-${evidence.id}`} className={`scroll-mt-8 p-4 rounded-xl glass-card transition-all duration-200 border border-cyber-border ${borderHighlight}`}>
      {/* Header bar */}
      <div 
        className="flex items-start justify-between cursor-pointer select-none"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-start space-x-3">
          <Icon className={`w-5 h-5 mt-0.5 flex-shrink-0 ${badgeColor.split(' ')[1]}`} />
          <div>
            <div className="flex items-center space-x-2">
              <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded border ${badgeColor}`}>
                {evidence.severity}
              </span>
              <span className="text-xs font-mono text-slate-400">
                {evidence.category.replace(/_/g, ' ').toUpperCase()}
              </span>
            </div>
            <p className="font-semibold text-slate-200 text-sm mt-1 leading-snug">
              {evidence.evidence}
            </p>
          </div>
        </div>

        <button 
          className="text-slate-400 hover:text-white p-1 ml-2"
          aria-label={expanded ? "Collapse evidence details" : "Expand evidence details"}
        >
          {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        </button>
      </div>

      {/* Expandable Body */}
      {expanded && (
        <div className="mt-3 pt-3 border-t border-cyber-border/60 text-xs space-y-2.5">
          <p className="font-mono text-slate-400 break-all">Evidence ID: {evidence.id || 'Legacy'} · {evidence.timestamp || 'Timestamp unavailable'}</p>
          <p>{evidence.origin || 'Legacy provenance'} · {evidence.verification_status || 'UNKNOWN'}</p>
          <p className="break-words">Observed value: {evidence.observed_value || 'Raw match not retained'}</p>
          <p>Correlation group: {evidence.correlation_group || 'Unknown'}</p>
          {evidence.source_spans?.map((span,i) => <p key={i} className="font-mono break-words">Source characters {span.start}–{span.end}: “{span.text}” ({span.kind})</p>)}
          {evidence.explanation && (
            <div>
              <p className="font-bold text-slate-300 text-[11px] uppercase tracking-wider">Why it matters:</p>
              <p className="text-slate-300 mt-0.5 leading-relaxed bg-cyber-bg/50 p-2.5 rounded-lg border border-cyber-border/40">
                {evidence.explanation}
              </p>
            </div>
          )}

          <div className="flex flex-wrap items-center justify-between gap-2 pt-1 text-[11px] text-slate-400 font-mono">
            <div className="flex items-center space-x-1.5">
              <Database className="w-3.5 h-3.5 text-cyber-cyan" />
              <span>Source: <strong className="text-slate-300">{evidence.source}</strong></span>
            </div>
            <div>
              <span>Heuristic reliability: <strong className="text-cyber-cyan">{Math.round(evidence.confidence * 100)}%</strong></span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
