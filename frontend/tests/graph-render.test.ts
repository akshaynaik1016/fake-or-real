import test from 'node:test';
import assert from 'node:assert/strict';
import {registerHooks} from 'node:module';
import {readFileSync} from 'node:fs';
import ts from 'typescript';
import React from 'react';
import {renderToStaticMarkup} from 'react-dom/server';
// Compile the actual TSX component for this Node SSR regression. CSS is separately
// validated by the production build and browser visibility checks.
const hooks=registerHooks({load(url,context,next){
 if(url.endsWith('.css'))return {format:'module',source:'export {};',shortCircuit:true};
 if(url.endsWith('.tsx'))return {format:'module',source:ts.transpileModule(readFileSync(new URL(url),'utf8'),{compilerOptions:{jsx:ts.JsxEmit.ReactJSX,module:ts.ModuleKind.ESNext,target:ts.ScriptTarget.ES2022}}).outputText,shortCircuit:true};
 return next(url,context);
}});
const {default:TrustGraph}=await import('../src/components/common/TrustGraph.tsx');
test('M: actual React Flow component emits visible nodes on its initial render',()=>{
 const graph={nodes:[{id:'org',type:'organization',label:'Synthetic Organizer',provenance:'Submitted'},{id:'domain',type:'domain',label:'provider.example',provenance:'Submitted'}],edges:[{id:'e',source:'org',target:'domain',relation:'mentions',relationship_status:'CLAIMED'}],disclaimer:'Unverified submitted claims'};
 const html=renderToStaticMarkup(React.createElement(TrustGraph,{graph}));
 assert.match(html,/data-testid="trust-graph-canvas"/);
 assert.match(html,/data-id="org"/);assert.match(html,/data-id="domain"/);
 assert.match(html,/react-flow__node/);assert.doesNotMatch(html,/visibility:hidden/);
 assert.match(html,/Synthetic Organizer/);
});

const {AssessmentDimensions}=await import('../src/components/common/AssessmentDimensions.tsx');
const {GraphFallbackRecords}=await import('../src/components/common/GraphRenderGuard.tsx');
test('BrightPath display separates observed concerns, authenticity and processing',()=>{
 const assessment={risk_indicators:{state:'NO_SIGNIFICANT_CONCERNS_OBSERVED',label:'No significant concerns observed',explanation:'Synthetic normal-looking description; not authenticated.'},authenticity:{state:'UNVERIFIED',label:'Unverified',explanation:'No independent evidence',offer_status:'UNVERIFIED',performed:false},processing:{submitted:1,processed:1,failed:0,awaiting_review:0,claims_extracted:3,extraction_note:'Text parsed, not corroborated'},coverage:{completed:2,total:10,percent:20,criteria:[],meaning:'Recorded check slots'},confidence_explanation:'Heuristic reliability, not independent corroboration'} as any;
 const html=renderToStaticMarkup(React.createElement(AssessmentDimensions,{assessment}));
 assert.match(html,/No significant concerns observed/);assert.match(html,/Unverified/);assert.match(html,/1 of 1 submitted sources processed/);assert.match(html,/2 \/ 10/);
 assert.doesNotMatch(html,/Verified Safe|100% Real|0% fraud/);
});
test('large graph renders initial nodes and retains every original record',()=>{
 const nodes=[{id:'case',type:'case',label:'Synthetic stress case',provenance:'Synthetic'},...Array.from({length:25},(_,i)=>({id:`ev${i}`,type:'evidence',label:`Synthetic evidence ${i}`,provenance:'Synthetic test'}))];
 const graph={nodes,edges:nodes.slice(1).map(n=>({id:`edge${n.id}`,source:'case',target:n.id,relation:'has_finding',relationship_status:'OBSERVED'})),disclaimer:'Synthetic fixture, not independent evidence'};
 const html=renderToStaticMarkup(React.createElement(TrustGraph,{graph}));
 assert.match(html,/react-flow__node/);assert.match(html,/Synthetic evidence 24/);assert.match(html,/25 evidence records/);assert.doesNotMatch(html,/visibility:hidden/);
});
test('fallback exposes all original records with inspection controls',()=>{
 const nodes=Array.from({length:22},(_,i)=>({id:String(i),type:'claim',label:`Synthetic source claim ${i}`}));
 const html=renderToStaticMarkup(React.createElement(GraphFallbackRecords,{nodes,onSelect:()=>{}}));
 assert.equal((html.match(/<button/g)||[]).length,22);assert.match(html,/Synthetic source claim 21/);
});

const {GraphUnavailable}=await import('../src/components/common/GraphView.tsx');
test('chunk-load fallback retains original provenance rather than an empty canvas',()=>{
 const graph={nodes:[{id:'c',type:'claim',label:'Synthetic claim',provenance:'Submitted, unverified',citations:[{source_id:'s',source_title:'Synthetic source',excerpt:'Exact synthetic excerpt',page:2}]}],edges:[],disclaimer:'Synthetic'};
 const html=renderToStaticMarkup(React.createElement(GraphUnavailable,{graph}));
 assert.match(html,/Graph visualization unavailable/);assert.match(html,/Exact synthetic excerpt/);assert.match(html,/page 2/);
});
