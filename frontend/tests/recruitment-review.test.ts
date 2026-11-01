import test from 'node:test';
import assert from 'node:assert/strict';
import {groupClaims,claimValue,groupedResults} from '../src/components/common/recruitmentPresentation.ts';
import {layoutTrustGraph} from '../src/components/common/trustGraphLayout.ts';
test('repeated notice claims group visually while every source/page reference remains',()=>{
 const claims=Array.from({length:16},(_,i)=>({id:String(i),source_id:'doc',claim_type:'fee',value:{currency:'INR',value:'1180'},excerpt:'Rs. 1180',location:{field:'extracted_text',start:i*10,end:i*10+8,page:i+1},extraction_method:'monetary_context',verification_status:'CLAIMED'}));
 const groups=groupClaims(claims);assert.equal(groups.length,1);assert.equal(groups[0].references.length,16);assert.equal(groups[0].references[15].location.page,16);
});
test('distinct destinations remain separate and tax relation is explained',()=>{
 assert.match(claimValue({base:'1000',total:'1180',currency:'INR'}),/1000.*GST.*1180/);
 const rows=[{claim_type:'payment_destination',value:'ALICE',status:'UNRESOLVED'},{claim_type:'payment_destination',value:'BOB',status:'UNRESOLVED'}];
 assert.equal(groupedResults(rows).length,2);
});
test('notice has a real non-overlapping layout position',()=>{
 const graph=layoutTrustGraph([{id:'org',type:'organization',label:'Org'},{id:'notice',type:'notice',label:'Advertisement'},{id:'fee',type:'payment',label:'Fee'},{id:'source',type:'source',label:'Independent source'}]);
 assert.equal(graph.find(n=>n.id==='notice')!.position.x,0);
 assert.equal(new Set(graph.map(n=>`${n.position.x},${n.position.y}`)).size,4);
});
