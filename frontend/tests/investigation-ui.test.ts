import test from 'node:test';
import assert from 'node:assert/strict';
import { layoutTrustGraph, shortLabel } from '../src/components/common/trustGraphLayout.ts';
import { summarizeVerification, checkStatus } from '../src/components/common/verificationSummary.ts';

test('identity left, entities middle, findings right without overlapping node bounds',()=>{
  const graph=[{id:'submission',type:'offer',label:'Offer'},{id:'org',type:'organization',label:'Organization'},
    {id:'domain',type:'domain',label:'example.com'},{id:'email',type:'email',label:'hr@example.com'},
    ...Array.from({length:18},(_,i)=>({id:'e'+i,type:'evidence',label:'Finding '+i}))];
  const result=layoutTrustGraph(graph);
  assert.equal(result.find(n=>n.id==='org')!.position.x,0);
  assert.equal(result.find(n=>n.id==='domain')!.position.x,330);
  assert.ok(result.filter(n=>n.column==='evidence').every(n=>n.position.x>=660));
  assert.equal(new Set(result.map(n=>`${n.position.x},${n.position.y}`)).size,result.length);
  for (const a of result) for(const b of result) if(a.id!==b.id)
    assert.ok(Math.abs(a.position.x-b.position.x)>=230||Math.abs(a.position.y-b.position.y)>=82);
  assert.deepEqual(result,layoutTrustGraph(graph));
});
test('labels are short while source values are unchanged',()=>{
  const label='A detailed finding '.repeat(20); assert.equal(shortLabel(label).length,64);
  const input=[{id:'e',type:'evidence',label}]; layoutTrustGraph(input); assert.equal(input[0].label,label);
});
test('unavailable checks are unresolved, not failed',()=>{
  const checks=[{check_name:'Payment',status:'failed'},...Array.from({length:8},(_,i)=>({check_name:String(i),status:'unavailable'}))];
  const result=summarizeVerification(checks as any); assert.equal(result.text,'1 failed · 8 unresolved · 0 independently verified');
  assert.equal(result.failed,1);assert.equal(result.unavailable,8);
});
test('all five check states and historical passed values are supported',()=>{
  const result=summarizeVerification(['passed','verified','failed','warning','unavailable','not_performed'].map(status=>({check_name:status,status})) as any);
  assert.equal(result.verified,0);assert.equal(result.completed,2);assert.equal(result.unresolved,5);assert.equal(checkStatus('unknown'),'unavailable');
  assert.equal(summarizeVerification([]).text,'0 failed · 0 unresolved · 0 independently verified');
});
