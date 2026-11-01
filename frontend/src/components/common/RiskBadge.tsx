import React from 'react';
import { ShieldCheck, AlertTriangle, AlertOctagon, ShieldAlert } from 'lucide-react';

interface RiskBadgeProps {
  level: string;
  size?: 'sm' | 'md' | 'lg';
}

export const RiskBadge: React.FC<RiskBadgeProps> = ({ level, size = 'md' }) => {
  const norm = level.toUpperCase();
  
  let config = {
    bg: 'bg-emerald-950/40',
    border: 'border-emerald-500/50',
    text: 'text-emerald-400',
    glow: 'shadow-[0_0_15px_rgba(16,185,129,0.25)]',
    icon: ShieldCheck,
    label: 'LOW RISK'
  };

  if (norm.includes('CRITICAL')) {
    config = {
      bg: 'bg-rose-950/60',
      border: 'border-rose-500/70',
      text: 'text-rose-400',
      glow: 'shadow-[0_0_20px_rgba(239,68,68,0.35)]',
      icon: AlertOctagon,
      label: 'CRITICAL RISK'
    };
  } else if (norm.includes('HIGH')) {
    config = {
      bg: 'bg-rose-950/30',
      border: 'border-rose-500/40',
      text: 'text-rose-300',
      glow: 'shadow-[0_0_15px_rgba(244,63,94,0.25)]',
      icon: ShieldAlert,
      label: 'HIGH RISK'
    };
  } else if (norm.includes('MODERATE')) {
    config = {
      bg: 'bg-amber-950/40',
      border: 'border-amber-500/50',
      text: 'text-amber-400',
      glow: 'shadow-[0_0_15px_rgba(245,158,11,0.25)]',
      icon: AlertTriangle,
      label: 'MODERATE RISK'
    };
  }

  const Icon = config.icon;
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs space-x-1',
    md: 'px-3 py-1 text-xs space-x-1.5',
    lg: 'px-4 py-2 text-sm space-x-2'
  }[size];

  return (
    <span className={`inline-flex items-center font-bold tracking-wider rounded-lg border ${config.bg} ${config.border} ${config.text} ${config.glow} ${sizeClasses}`}>
      <Icon className={size === 'lg' ? 'w-4 h-4' : 'w-3.5 h-3.5'} />
      <span>{config.label}</span>
    </span>
  );
};
