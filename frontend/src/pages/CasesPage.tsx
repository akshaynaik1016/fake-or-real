import {useEffect,useState} from 'react';
import {Link,useNavigate} from 'react-router-dom';
import {createCase,listCases,type CaseListItem} from '../api/cases';
export function CasesPage(){
 const [cases,setCases]=useState<CaseListItem[]>([]),[title,setTitle]=useState(''),[error,setError]=useState(''),[busy,setBusy]=useState(false);const navigate=useNavigate();
 useEffect(()=>{listCases().then(setCases).catch(e=>setError(e.message));},[]);
 const create=async(e:React.FormEvent)=>{e.preventDefault();setBusy(true);setError('');try{const result=await createCase(title);navigate(`/cases/${result.case_id}`);}catch(e){setError(e instanceof Error?e.message:'Case creation failed');}finally{setBusy(false);}};
 return <div className="max-w-6xl mx-auto px-4 py-10 space-y-7">
  <div><p className="text-xs text-cyan-300 font-mono uppercase">Multi-source investigation</p><h1 className="text-3xl font-bold mt-2">Investigation cases</h1><p className="text-sm text-slate-400 mt-2">Keep posters, offer letters, messages and links together. Compare their claims and track what changes.</p></div>
  {error&&<p role="alert" className="text-rose-300">{error}</p>}
  <form onSubmit={create} className="glass-card rounded-2xl p-6 flex flex-col sm:flex-row gap-3"><label className="flex-1 text-xs text-slate-400">Case title<input required minLength={3} maxLength={200} value={title} onChange={e=>setTitle(e.target.value)} placeholder="e.g. Microsoft software internship offer" className="block w-full mt-2 p-3 rounded-xl bg-slate-950 border border-slate-600 text-white"/></label><button disabled={busy||!title.trim()} className="self-end px-5 py-3 rounded-xl bg-cyan-300 text-slate-950 text-sm font-bold disabled:opacity-40">{busy?'Creating…':'Create investigation case'}</button></form>
  <div className="grid md:grid-cols-2 gap-4">{cases.map(c=><Link key={c.id} to={`/cases/${c.id}`} className="glass-card rounded-xl p-5 border border-slate-700 hover:border-cyan-300"><h2 className="font-bold">{c.title}</h2><p className="text-sm text-cyan-300 mt-3">{c.fusion.risk_level||'UNDETERMINED'}</p><p className="text-xs text-slate-400 mt-2">{c.source_count} sources · revision {c.revision} · {c.status}</p></Link>)}</div>
  {!cases.length&&<p className="text-slate-400 text-sm">Create a case to begin. Existing <Link to="/history" className="underline text-cyan-300">single-source scans</Link> remain available.</p>}
 </div>;
}
