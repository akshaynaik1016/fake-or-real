import {RiskBadge} from './RiskBadge';
import {riskIndex} from './assessmentSemantics';
// Kept as the existing results component; primary presentation uses concern/abstention.
export function TrustScoreCircle({score,confidence,riskLevel}:{score:number|null;confidence:number;riskLevel:string}) {
 return <section className="glass-card rounded-3xl p-6 space-y-5 text-center">
  <h2 className="font-bold">Evidence assessment</h2><RiskBadge level={riskLevel}/>
  <div><p className="text-xs text-slate-400">Concern index · higher means more concern</p><p className="text-2xl font-mono mt-3">{riskIndex(score,riskLevel)}</p></div>
  <p className="text-xs text-slate-400">Evidence reliability index: {confidence}/100. Heuristic, not a calibrated probability.</p>
  <p className="text-sm text-amber-200">Specific offer authenticity remains unresolved.</p>
 </section>;
}
