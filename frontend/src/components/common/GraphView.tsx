import {lazy,Suspense,useState} from 'react';
import type {Investigation} from '../../api/client';
import {GraphRenderGuard} from './GraphRenderGuard.tsx';
const TrustGraph=lazy(()=>import('./TrustGraph'));
export function GraphUnavailable({graph}:{graph:Investigation['graph']}){
 return <section aria-label="Graph fallback" className="text-sm space-y-3"><p role="alert" className="text-amber-200">Graph visualization unavailable. Every original record and its retained provenance remains accessible below.</p>{graph.nodes.map(n=><details key={n.id} className="text-xs border border-slate-700 rounded-lg p-3"><summary className="cursor-pointer text-cyan-300">{n.type}: {n.label}</summary><p>{n.provenance}</p>{n.citations?.map((c,i)=><p key={i} className="my-2 break-words">Source {c.source_id} {c.page?`page ${c.page}`:''} · {c.excerpt}</p>)}</details>)}</section>;
}
export function GraphView({graph}:{graph:Investigation['graph']}){
 const [retry,setRetry]=useState(0);
 return <GraphRenderGuard key={retry} fallback={<><GraphUnavailable graph={graph}/><button className="text-cyan-300 text-xs underline mt-3" onClick={()=>setRetry(n=>n+1)}>Retry visualization</button></>}><Suspense fallback={<p>Loading graph… Original records remain in the evidence sections.</p>}><TrustGraph graph={graph}/></Suspense></GraphRenderGuard>;
}
