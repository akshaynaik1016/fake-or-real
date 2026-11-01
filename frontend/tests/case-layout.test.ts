import test from 'node:test';
import assert from 'node:assert/strict';
import {layoutTrustGraph} from '../src/components/common/trustGraphLayout.ts';
test('case graph keeps cases and identities left, documents central, comparisons right',()=>{
 const nodes=[{id:'case',type:'case',label:'Case'},{id:'org',type:'organization',label:'Org'},{id:'doc',type:'source_document',label:'Poster'},{id:'claim',type:'claim',label:'15000/month'},{id:'conflict',type:'contradiction',label:'Different stipend'},{id:'agreement',type:'cross_finding',label:'Repeated claim'}];
 const result=layoutTrustGraph(nodes);const byId=Object.fromEntries(result.map(n=>[n.id,n]));
 assert.equal(byId.case.position.x,0);assert.equal(byId.org.position.x,0);
 assert.equal(byId.doc.position.x,330);assert.equal(byId.claim.position.x,330);
 assert.ok(byId.conflict.position.x>=660);assert.ok(byId.agreement.position.x>=660);
 assert.equal(new Set(result.map(n=>`${n.position.x},${n.position.y}`)).size,nodes.length);
});
