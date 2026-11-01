import { useMemo, useState } from 'react';
import { ReactFlow, Background, Controls, Position, type Node, type Edge } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import type { GraphCitation, Investigation } from '../../api/client';
import { layoutTrustGraph } from './trustGraphLayout';
const colors: Record<string,string> = { notice:'#4c1d95',offer:'#164e63',organization:'#312e81',domain:'#1e3a5f',email:'#064e3b',phone:'#4a044e',payment:'#78350f',evidence:'#334155',source:'#134e4a',case:'#164e63',source_document:'#1e3a5f',claim:'#155e75',contradiction:'#881337',cross_finding:'#713f12' };
const relationshipColors: Record<string,string> = { OBSERVED:'#67e8f9',CLAIMED:'#c4b5fd',VERIFIED:'#6ee7b7',CONTRADICTED:'#fb7185',UNRESOLVED:'#94a3b8' };
function SourceCitations({refs}:{refs:GraphCitation[]}) {return <div className="space-y-3">{refs.map((ref,i)=><div key={i} className="border-t border-slate-700 pt-2"><a className="text-cyan-300 underline" href={ref.url||`#source-${ref.source_id}`} target={ref.url?"_blank":undefined} rel={ref.url?"noopener noreferrer":undefined}>{ref.source_title}</a><p className="text-slate-300 mt-1 break-words">{ref.field==='scanner_output'?'Rule output: ':'Source excerpt: '}{ref.excerpt}</p><p className="text-slate-500">{ref.field} {ref.start!==undefined?`${ref.start}–${ref.end}`:''}{ref.page?` · page ${ref.page}`:''}</p></div>)}</div>;}
export default function TrustGraph({graph}: {graph:Investigation['graph']}) {
  const [selection,setSelection] = useState<{kind:'node'|'edge';id:string}|null>(null);
  const nodes:Node[] = useMemo(() => layoutTrustGraph(graph.nodes).map(item => {
    const n=graph.nodes.find(n=>n.id===item.id)!;
    return {id:n.id,position:item.position,sourcePosition:item.column==='evidence'?Position.Left:Position.Right,
      targetPosition:item.column==='identity'?Position.Right:Position.Left,
      data:{label:<div><span className="block uppercase text-[9px] opacity-60 mb-1">{n.type}</span>{item.label}</div>},
      style:{background:colors[n.type]||'#334155',color:'#f8fafc',width:230,height:82,overflow:'hidden',
        border:`2px solid ${n.inconsistent?'#fb7185':selection?.id===n.id?'#67e8f9':'#64748b'}`,borderRadius:12,fontSize:12}};
  }),[graph,selection]);
  const edges:Edge[] = useMemo(() => graph.edges.map((e,i)=>({
    id:e.id,source:e.source,target:e.target,type:'smoothstep',
    pathOptions:{borderRadius:16,offset:24+(i%5)*9},
    style:{stroke:relationshipColors[e.relationship_status||'UNRESOLVED'],strokeWidth:selection?.id===e.id?3:1.2,
      opacity:!selection||selection.id===e.id||selection.id===e.source||selection.id===e.target?0.9:0.12},
    label:selection?.id===e.id?e.relation.replaceAll('_',' '):undefined,
    labelStyle:{fill:'#e2e8f0',fontSize:10},labelBgStyle:{fill:'#0f172a'},
  })),[graph,selection]);
  const detail=selection?.kind==='node'?graph.nodes.find(n=>n.id===selection.id):null;
  const relationship=selection?.kind==='edge'?graph.edges.find(e=>e.id===selection.id):null;
  return <div className="space-y-3">
    <div className="flex flex-wrap gap-4 text-xs">{Object.entries(relationshipColors).map(([state,color])=><span key={state} style={{color}}>● {state==='VERIFIED' && graph.verification_scope==='INDEPENDENT_ONLY'?'independently verified':state.toLowerCase()}</span>)}</div>
    <p className="text-xs text-slate-400">Claimed identity → related submitted entities → evidence. Select a node or edge to inspect details.</p>
    <div className="grid grid-cols-1 lg:grid-cols-[minmax(0,1fr)_300px] gap-3">
      <div className="h-[600px] min-w-0 rounded-xl overflow-hidden bg-slate-950 border border-slate-700">
        <ReactFlow nodes={nodes} edges={edges} fitView fitViewOptions={{padding:0.08}} colorMode="dark"
          onNodeClick={(_,n)=>setSelection({kind:'node',id:n.id})} onEdgeClick={(_,e)=>setSelection({kind:'edge',id:e.id})}
          minZoom={0.15} maxZoom={2} aria-label="Evidence relationship graph">
          <Background/><Controls/>
        </ReactFlow>
      </div>
      <aside className="rounded-xl bg-slate-900 border border-slate-700 p-4 text-xs space-y-3 lg:max-h-[600px] overflow-y-auto" aria-label="Graph details" aria-live="polite">
        <h3 className="font-bold text-cyan-300 text-sm">Evidence details</h3>
        {!selection&&<p>Select an entity, finding or relationship. Full labels and provenance appear here.</p>}
        {detail&&<><p className="font-bold break-words">{detail.type}: {detail.label}</p><p className="break-all">Source: {detail.provenance}</p>
          {detail.evidence&&<><p>{detail.evidence.explanation}</p><p>{detail.evidence.verification_status}</p><p>{detail.evidence.timestamp}</p>
            <p className="break-words">Observed: {detail.evidence.observed_value}</p>
            <a className="text-cyan-300 underline" href={`#evidence-${detail.evidence.id}`}>Inspect evidence record</a></>}
          {detail.source&&<p>{detail.source.extracted_information}</p>}{!!detail.citations?.length&&<SourceCitations refs={detail.citations}/>}</>}
        {relationship&&<><p style={{color:relationshipColors[relationship.relationship_status||'UNRESOLVED']}}>{relationship.relationship_status||'UNRESOLVED'}</p>
          <p>{relationship.relation.replaceAll('_',' ')}</p><p>{graph.nodes.find(n=>n.id===relationship.source)?.label} → {graph.nodes.find(n=>n.id===relationship.target)?.label}</p>
          <p>{relationship.verification_status}</p>{relationship.evidence_ids?.map(id=><a key={id} className="block underline text-cyan-300" href={`#evidence-${id}`}>Evidence {id.slice(0,8)}</a>)}{!!relationship.citations?.length&&<SourceCitations refs={relationship.citations}/>}</>}
      </aside>
    </div>
    <p className="text-xs text-slate-400">{graph.disclaimer}</p>
    <details className="text-xs"><summary className="cursor-pointer text-cyan-300">Browse graph entities as a list</summary>
      <ul className="space-y-2 mt-2">{graph.nodes.map(n=><li key={n.id}><button className="underline text-left" onClick={()=>setSelection({kind:'node',id:n.id})}>{n.type}: {n.label}</button></li>)}</ul>
    </details>
  </div>;
}
