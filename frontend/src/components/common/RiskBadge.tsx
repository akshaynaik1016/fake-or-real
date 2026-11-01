import {AlertTriangle,ShieldQuestion} from 'lucide-react';
import {assessmentLabel} from './assessmentSemantics';
export function RiskBadge({level,size='md'}:{level:string;size?:'sm'|'md'|'lg'}) {
  const label=assessmentLabel(level),elevated=label==='Elevated concern';
  const Icon=elevated?AlertTriangle:ShieldQuestion;
  return <span className={`inline-flex items-center gap-1.5 rounded-lg border font-bold ${size==='sm'?'px-2 py-1 text-xs':'px-3 py-2 text-sm'} ${elevated?'bg-rose-950/30 border-rose-500/50 text-rose-300':'bg-amber-950/30 border-amber-500/40 text-amber-200'}`}><Icon size={15}/>{label}</span>;
}
