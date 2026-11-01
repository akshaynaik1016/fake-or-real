import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Info, ShieldAlert, ShieldCheck, AlertTriangle } from 'lucide-react';

interface TrustScoreProps {
  score: number; // 0-100
  confidence: number; // 0-100
  riskLevel: string;
}

export const TrustScoreCircle: React.FC<TrustScoreProps> = ({ score, confidence, riskLevel }) => {
  const [displayScore, setDisplayScore] = useState(0);

  // Animated counter on mount
  useEffect(() => {
    let start = 0;
    const duration = 1200; // ms
    const stepTime = 20; // ms
    const steps = duration / stepTime;
    const increment = score / steps;

    const timer = setInterval(() => {
      start += increment;
      if (start >= score) {
        setDisplayScore(score);
        clearInterval(timer);
      } else {
        setDisplayScore(Math.floor(start));
      }
    }, stepTime);

    return () => clearInterval(timer);
  }, [score]);

  // Color selection based on score
  let strokeColor = '#10b981'; // Green for high trust
  let textColor = 'text-emerald-400';
  let glowColor = 'rgba(16,185,129,0.35)';
  let bgBadge = 'bg-emerald-950/60 border-emerald-500/50 text-emerald-300';
  let RiskIcon = ShieldCheck;

  if (score < 40) {
    strokeColor = '#ef4444'; // Red for low trust / critical risk
    textColor = 'text-rose-400';
    glowColor = 'rgba(239,68,68,0.4)';
    bgBadge = 'bg-rose-950/60 border-rose-500/50 text-rose-300';
    RiskIcon = ShieldAlert;
  } else if (score < 60) {
    strokeColor = '#f43f5e';
    textColor = 'text-rose-300';
    glowColor = 'rgba(244,63,94,0.35)';
    bgBadge = 'bg-rose-950/40 border-rose-500/40 text-rose-300';
    RiskIcon = AlertTriangle;
  } else if (score < 80) {
    strokeColor = '#f59e0b';
    textColor = 'text-amber-400';
    glowColor = 'rgba(245,158,11,0.35)';
    bgBadge = 'bg-amber-950/60 border-amber-500/50 text-amber-300';
    RiskIcon = AlertTriangle;
  }

  const radius = 68;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference - (score / 100) * circumference;

  return (
    <div className="flex flex-col items-center justify-center p-6 rounded-3xl glass-card relative overflow-hidden border border-cyber-border shadow-2xl">
      {/* Background radial glow */}
      <div 
        className="absolute w-48 h-48 rounded-full blur-3xl pointer-events-none opacity-30 -z-10"
        style={{ backgroundColor: strokeColor }}
      />

      <div className="flex items-center space-x-1.5 mb-3">
        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: strokeColor }} />
        <p className="text-[11px] font-mono uppercase tracking-widest text-slate-300 font-bold">
          Opportunity Legacy Trust Score
        </p>
      </div>

      {/* Circular SVG Gauge */}
      <div className="relative w-48 h-48 flex items-center justify-center">
        <svg className="w-full h-full -rotate-90 transform" viewBox="0 0 170 170">
          {/* Cyber outer tick ring */}
          <circle
            cx="85"
            cy="85"
            r="78"
            stroke="rgba(31, 45, 77, 0.6)"
            strokeWidth="2"
            strokeDasharray="2 6"
            fill="transparent"
          />

          {/* Background Track */}
          <circle
            cx="85"
            cy="85"
            r={radius}
            stroke="#131c31"
            strokeWidth="13"
            fill="transparent"
          />

          {/* Animated Active Stroke */}
          <motion.circle
            cx="85"
            cy="85"
            r={radius}
            stroke={strokeColor}
            strokeWidth="13"
            fill="transparent"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 1.4, ease: "easeOut" }}
            strokeLinecap="round"
            style={{ filter: `drop-shadow(0 0 12px ${glowColor})` }}
          />
        </svg>

        {/* Center Score Display */}
        <div className="absolute flex flex-col items-center justify-center text-center">
          <span className={`text-5xl font-black font-mono tracking-tight ${textColor} drop-shadow-md`}>
            {displayScore}
          </span>
          <span className="text-[11px] text-slate-400 font-mono tracking-widest uppercase mt-0.5">
            OUT OF 100
          </span>
        </div>
      </div>

      {/* Risk Level Badge */}
      <div className={`mt-3 px-3 py-1 rounded-full border text-xs font-mono font-bold uppercase tracking-wider flex items-center space-x-1.5 shadow-sm ${bgBadge}`}>
        <RiskIcon className="w-3.5 h-3.5 flex-shrink-0" />
        <span>{riskLevel}</span>
      </div>

      {/* Forensic Confidence Score Section */}
      <div className="w-full mt-5 pt-4 border-t border-cyber-border/80 flex items-center justify-between">
        <div className="flex items-center space-x-1.5" title="The confidence score reflects the volume and consistency of available forensic evidence without generative guessing.">
          <span className="text-xs text-slate-300 font-medium">Legacy confidence index:</span>
          <Info className="w-3.5 h-3.5 text-slate-400 cursor-help" />
        </div>
        <div className="flex items-center space-x-2">
          <div className="w-24 h-2 bg-slate-800 rounded-full overflow-hidden">
            <motion.div 
              className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full"
              initial={{ width: 0 }}
              animate={{ width: `${confidence}%` }}
              transition={{ duration: 1, delay: 0.2 }}
            />
          </div>
          <span className="font-mono text-xs font-black text-cyber-cyan">{confidence}%</span>
        </div>
      </div>
    </div>
  );
};
