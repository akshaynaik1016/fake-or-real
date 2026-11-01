import { CheckCircle2, AlertTriangle, XCircle, CircleDashed, MinusCircle } from 'lucide-react';
import type { VerificationCheckItem } from '../../api/client';
import { checkStatus, summarizeVerification } from './verificationSummary';
const appearances = {
  completed: {label:'Content check completed',Icon:CheckCircle2,color:'text-cyan-300',style:'border-cyan-500/30 bg-cyan-950/20'},
  verified: { label: 'Independently verified claim', Icon: CheckCircle2, color: 'text-emerald-400', style: 'border-emerald-500/30 bg-emerald-950/20' },
  failed: { label: 'Failed', Icon: XCircle, color: 'text-rose-400', style: 'border-rose-500/40 bg-rose-950/20' },
  warning: { label: 'Warning', Icon: AlertTriangle, color: 'text-amber-300', style: 'border-amber-500/30 bg-amber-950/20' },
  unavailable: { label: 'Unavailable', Icon: CircleDashed, color: 'text-slate-400', style: 'border-slate-600 bg-slate-900/30' },
  not_performed: { label: 'Not performed', Icon: MinusCircle, color: 'text-slate-400', style: 'border-slate-700 bg-slate-900/30' },
};
export function VerificationChecklist({ checks }: { checks: VerificationCheckItem[] }) {
  const counts = summarizeVerification(checks);
  return <section className="p-6 rounded-2xl glass-card" aria-label="Verification checklist">
    <div className="flex flex-wrap justify-between gap-4 mb-4"><div>
      <h3 className="font-bold text-slate-100">Checks and verification status</h3>
      <p className="text-xs text-slate-400 mt-1">Completed means a rule ran. It does not establish independent authenticity verification. Unavailable and unperformed checks remain unresolved.</p>
    </div><p className="text-sm text-cyan-300 font-mono" role="status">{counts.text}</p></div>
    <p className="text-xs text-slate-400 mb-4">Offer authenticity remains unresolved. {counts.completed} completed content checks · {counts.warning} warning · {counts.unavailable} unavailable · {counts.not_performed} not performed</p>
    {checks.length === 0 && <p className="text-slate-400 text-sm">No check results recorded.</p>}
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">{checks.map((item,i) => {
      const state = appearances[checkStatus(item.status) as keyof typeof appearances]; const Icon = state.Icon;
      return <div key={`${item.check_name}-${i}`} className={`p-4 rounded-xl border ${state.style}`}>
        <div className="flex flex-wrap justify-between gap-2"><span className="font-semibold text-sm">{item.check_name}</span>
          <span className={`flex gap-1 items-center text-xs ${state.color}`}><Icon size={16}/>{state.label}</span></div>
        <p className="text-xs text-slate-400 mt-2 leading-relaxed">{item.details || 'No execution details recorded.'}</p>
      </div>;
    })}</div>
  </section>;
}
