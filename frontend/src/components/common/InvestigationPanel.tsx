import { lazy, Suspense, useState } from 'react';
import { executeInvestigationAction, getScanById, type ScanDetail } from '../../api/client';
import {RecruitmentReview} from './RecruitmentReview';
import {assessmentLabel,researchLabel} from './assessmentSemantics';
const TrustGraph = lazy(() => import('./TrustGraph'));

export function InvestigationPanel({ scan, onUpdate }: { scan: ScanDetail; onUpdate: (scan: ScanDetail) => void }) {
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState('');
  const state = scan.investigation;
  if (!state) return <p className="text-amber-300">Investigation details unavailable for this record.</p>;
  const { fusion, language } = state;
  const execute = async (action: string) => {
    setBusy(action); setError('');
    try {
      await executeInvestigationAction(scan.id, action, state.revision);
      onUpdate(await getScanById(scan.id));
    } catch (e) { setError(e instanceof Error ? e.message : 'Investigation failed'); }
    finally { setBusy(null); }
  };
  return <div className="space-y-6">
    <section className="glass-card rounded-2xl p-6 space-y-4" aria-label="Evidence fusion">
      <div className="flex flex-wrap justify-between gap-3"><h2 className="font-bold text-xl">Evidence Fusion</h2>
        <span className="text-xs font-mono text-cyan-300">{fusion.assessment_mode} · {state.status} · revision {state.revision}</span></div>
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {[['Risk classification', assessmentLabel(state.assessment?.state||fusion.risk_level)],
          ['Risk score (higher = more concern)', fusion.risk_score === null ? 'Undetermined' : `${fusion.risk_score}/100`],
          ['Evidence confidence', `${fusion.confidence}/100`], ['Investigation coverage', `${fusion.evidence_coverage}%`]].map(([label, value]) =>
          <div className="rounded-xl bg-slate-950/70 p-4" key={label}><p className="text-xs text-slate-400">{label}</p><p className="text-lg font-bold mt-2">{value}</p></div>)}
      </div>
      <p className="text-sm text-amber-200">Heuristic risk and confidence are decision-support indices, not validated probabilities. Risk and independent verification are separate. Specific offer authenticity is unresolved.</p>
      {!!state.assessment?.verified_claims.length&&<div className="text-xs text-cyan-200">Independently verified claim (limited scope): {state.assessment.verified_claims.map(c=><p key={c.evidence_id}>{c.scope} · claim {c.claim_id} · evidence {c.evidence_id}</p>)}<p>These scoped claims do not authenticate the overall offer.</p></div>}
      {fusion.explanation.map((line, i) => <p key={i} className="text-xs text-slate-400">{line}</p>)}
      <details><summary className="text-cyan-300 cursor-pointer text-sm">Calculation and unknowns</summary>
        <p className="text-xs mt-3">Configured prior assumption: {fusion.prior}. Correlated observations contribute once.</p>
        <div className="overflow-x-auto mt-3"><table className="w-full text-xs text-left"><thead><tr><th className="p-2">Evidence</th><th>Contribution</th><th>Score update</th></tr></thead>
          <tbody>{fusion.evidence_updates.map(u => <tr key={u.evidence_id} className="border-t border-slate-700">
            <td className="p-2"><a className="underline text-cyan-300" href={`#evidence-${u.evidence_id}`}>{u.evidence_id.slice(0, 12)}</a><p>{u.correlation_group}</p></td>
            <td>{u.included ? `×${u.heuristic_multiplier ?? u.likelihood_ratio}` : 'Excluded'}<p className="text-slate-400 max-w-sm">{u.reason}</p></td>
            <td>{u.before} → {u.after}</td></tr>)}</tbody></table></div>
        <ul className="list-disc pl-5 mt-4 text-xs text-amber-200 space-y-2">{fusion.unknowns.map((u, i) => <li key={i}>{u}</li>)}</ul>
      </details>
    </section>
    <RecruitmentReview claims={state.claims||[]} evidence={state.evidence} review={state.notice_review}/>
    {!!state.monetary_entities?.length && <section className="glass-card rounded-2xl p-6 space-y-3" aria-label="Monetary entities">
      <h2 className="font-bold text-lg">Amounts in the submission</h2>
      {state.monetary_entities.map((amount,i) => <div key={i} className="text-sm border-t border-slate-700 pt-2">
        <strong>{amount.raw}{amount.period?`/${amount.period}`:''}</strong> · {amount.role.replaceAll('_',' ')} · {amount.category.replaceAll('_',' ')}
        <p className="text-xs text-slate-400">{amount.page?`Page ${amount.page} · `:''}characters {amount.start}–{amount.end}. {amount.classification_rationale||amount.ambiguity_reason||'Linked within the source clause.'}</p>
        <details className="text-xs mt-1"><summary className="cursor-pointer text-cyan-300">Source context</summary>{amount.supporting_text||amount.context}</details>
      </div>)}
    </section>}
    <section className="glass-card rounded-2xl p-6 space-y-3">
      <h2 className="font-bold text-lg">Investigation Summary</h2>
      <p className="text-xs font-mono text-purple-300">Provider: {language.provider} · {language.mode}</p>
      <p className="text-xs text-slate-400">{language.reason}</p>
      {language.mode === 'LLM_INTERPRETATION' && <p className="text-amber-200 text-xs">AI interpretation; not independently verified.</p>}
      {language.interpretations.length === 0 && <p className="text-sm text-slate-400">No recorded findings to summarize. Independent verification is still required.</p>}
      {language.interpretations.map((item, i) => <div key={i} className="text-sm text-slate-200"><p>{item.text}</p>
        <div className="flex gap-3 mt-1">{item.evidence_ids.map(id => <a key={id} href={`#evidence-${id}`} className="text-cyan-300 underline text-xs">Evidence {id.slice(0, 8)}</a>)}</div></div>)}
    </section>
    <section className="glass-card rounded-2xl p-6 space-y-3">
      <h2 className="font-bold text-lg">Identity and External Research</h2>
      <p className="text-sm">Claimed organization: {state.claimed_organization || 'Not identified'}</p>
      <div className="flex flex-wrap gap-2">{state.entities.filter(e => ['email', 'domain'].includes(e.type)).map(e =>
        <span key={e.id} className="px-3 py-2 rounded-lg bg-slate-900 text-xs break-all">Submitted {e.type}: {e.value}</span>)}</div>
      <p className="text-xs text-amber-200">Sender and specific offer authorization remain unverified. A company website or search mention does not authenticate this offer.</p>
      {state.research.map((r, i) => <div key={i} className="border-t border-slate-700 pt-3 space-y-3">
        <p className="text-sm text-cyan-300">Tavily: {researchLabel(r.status)}</p><p className="text-xs text-slate-400">{r.reason}</p>
        {r.query && <p className="text-xs">Query: {r.query}</p>}
        {r.sources.map(s => <details key={s.id} className="bg-slate-900 p-3 rounded-lg text-xs">
          <summary className="cursor-pointer">{s.title} · {s.source_type.replaceAll('_', ' ')}</summary>
          <a className="block my-2 text-cyan-300 underline break-all" href={s.url} target="_blank" rel="noopener noreferrer">{s.url}</a>
          <p>{s.extracted_information}</p><p className="text-slate-400 mt-2">{s.retrieved_at} · {s.verification_status}</p>
        </details>)}
      </div>)}
    </section>
    <section className="glass-card rounded-2xl p-6 space-y-4"><h2 className="font-bold text-lg">TrustGraph</h2>
      <p className="text-xs text-slate-400">Pan, zoom and select an entity to inspect its provenance. Red borders highlight recorded identity inconsistencies.</p>
      <Suspense fallback={<p>Loading graph…</p>}><TrustGraph graph={state.graph} /></Suspense>
    </section>
    <section id="next-investigation" className="glass-card rounded-2xl p-6 space-y-4">
      <h2 className="font-bold text-lg">Next Best Investigation</h2>
      <p className="text-xs text-slate-400">Transparent rule ranking considers unresolved identity, financial harm, source availability and execution cost. Search budget used: {state.research_calls}/3.</p>
      {error && <p role="alert" className="text-rose-300">{error}</p>}
      {state.recommendations.map(a => <div key={a.action_id} className="rounded-xl border border-slate-700 p-4 space-y-2">
        <div className="flex justify-between gap-4"><h3 className="font-bold text-sm">{a.title}</h3><span className="text-xs text-cyan-300">{a.priority} · {a.ranking_score}</span></div>
        <p className="text-sm text-slate-300">{a.reason}</p><p className="text-xs text-slate-400">{a.instructions}</p>
        <p className="text-xs">Required: {a.required_information.join(', ')}</p>
        {a.execution_type === 'AUTOMATED' ? <button onClick={() => execute(a.action_id)} disabled={busy !== null || a.status !== 'AVAILABLE'}
          className="rounded-lg bg-cyan-300 px-4 py-2 text-xs font-bold text-slate-950 disabled:opacity-40">{busy === a.action_id ? 'Investigating…' : a.status === 'AVAILABLE' ? 'Investigate Next' : a.status}</button>
          : <span className="text-xs font-mono text-amber-200">MANUAL VERIFICATION · {a.status}</span>}
        {a.unavailable_reason && <p className="text-xs text-amber-200">{a.unavailable_reason}</p>}
      </div>)}
      {state.last_change && <div role="status" className="p-4 bg-cyan-950 rounded-xl text-sm"><strong>{state.last_change.status === 'UNAVAILABLE' ? 'Check could not complete' : 'Investigation updated'}</strong>
        <p>{state.last_change.reason}</p><p>Risk score: {state.last_change.before.risk_score ?? 'Unknown'} → {state.last_change.after.risk_score ?? 'Unknown'}. {state.last_change.risk_score_changed ? 'The contributing evidence changed.' : 'No change to the contributing risk signals.'}</p></div>}
      <details><summary className="cursor-pointer text-cyan-300 text-xs">Execution history</summary>
        {state.history.map((h, i) => <p key={i} className="text-xs mt-2">{h.timestamp} · {h.action_id} · {h.status} · {h.details}</p>)}
      </details>
    </section>
  </div>;
}
