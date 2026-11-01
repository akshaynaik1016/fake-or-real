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
