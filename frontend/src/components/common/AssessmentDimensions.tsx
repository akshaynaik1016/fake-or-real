import type {Assessment} from '../../api/client';
export function AssessmentLabels({assessment}:{assessment?:Assessment}){
 return <div className="text-xs space-y-1"><p>Risk indicators: {assessment?.risk_indicators?.label||'Not recorded'}</p><p className="text-amber-200">Authenticity: {assessment?.authenticity?.label||'Unverified'}</p></div>;
}
export function AssessmentDimensions({assessment}:{assessment?:Assessment}){
 if(!assessment?.risk_indicators)return <p className="text-xs text-amber-200">Observed risk details unavailable for this historical snapshot. Authenticity remains unverified.</p>;
 const risk=assessment.risk_indicators,auth=assessment.authenticity,cov=assessment.coverage,p=assessment.processing;
 return <section aria-label="Risk indicators and authenticity" className="space-y-4"><p className="text-xs text-slate-300">Overall assessment: {assessment.label} · Risk index: {assessment.risk_score===null?'Not scored':`${assessment.risk_score}/100 (heuristic)`}</p>
 <div className="grid md:grid-cols-2 gap-4"><div className={`rounded-xl border p-4 ${risk.state==='ELEVATED_CONCERN'?'border-rose-500/50 bg-rose-950/20':risk.state==='NO_SIGNIFICANT_CONCERNS_OBSERVED'?'border-cyan-600/40 bg-cyan-950/20':'border-amber-600/40 bg-slate-950/60'}`}><p className="text-xs uppercase text-slate-300">Risk indicators · observed signals</p><h3 className="font-bold text-lg mt-2">{risk.label}</h3><p className="text-xs text-slate-300 mt-2">{risk.explanation}</p></div><div className="rounded-xl border border-amber-600/40 bg-slate-950/60 p-4"><p className="text-xs uppercase text-slate-300">Offer authenticity</p><h3 className="font-bold text-lg mt-2">{auth?.label||'Unverified'}</h3><p className="text-xs text-slate-300 mt-2">{auth?.explanation}</p><p className="text-xs text-amber-200 mt-2">A low-concern description is not a verified offer. Matching notice fields do not authenticate a recruiter or payment destination.</p></div></div>
 <details className="text-xs"><summary className="cursor-pointer text-cyan-300">Processing, extraction, confidence and coverage explained</summary><div className="space-y-3 mt-3">
 {p&&<p>{p.submitted!==null?`${p.processed} of ${p.submitted} submitted sources processed; ${p.failed} failed; ${p.awaiting_review} awaiting review.`:'Single-source processing recorded.'} {p.claims_extracted} structured claims. {p.extraction_note}</p>}
 <p>{assessment.confidence_explanation}</p><p>{cov?.percent}% coverage · {cov?.completed??'unknown'} / {cov?.total??'unknown'} recorded check slots. {cov?.meaning}</p>
 <ul className="space-y-2">{cov?.criteria.map((c,i)=><li key={i}>{c.name}: {c.completed?'Completed (scope limited to this check)':`Unresolved — ${c.reason}`}</li>)}</ul>
 </div></details></section>;
}
