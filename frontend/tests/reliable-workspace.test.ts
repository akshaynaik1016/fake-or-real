import test from 'node:test';
import assert from 'node:assert/strict';
import {intakeError,sourceStatus} from '../src/components/cases/intakeValidation.ts';
import {graphOverview} from '../src/components/common/graphOverview.ts';
const counts={total:0,url:0,pdf:0,screenshot:0};
test('optional source types and exactly five images',()=>{
 assert.ok(intakeError(counts,[],'',[]));
 for(const [urls,text,files] of [[['https://example.com'],'',[]],[[],'message',[]],[[],'',[{name:'x.pdf'}]],[[],'',Array.from({length:5},(_,i)=>({name:`${i}.png`}))]] as [string[],string,{name:string}[]][]){assert.equal(intakeError(counts,urls,text,files),'');}
 assert.match(intakeError(counts,[],'',Array.from({length:6},()=>({name:'x.png'}))),/5 screenshots/);
 assert.match(intakeError({...counts,screenshot:5,total:5},[],'',[{name:'x.png'}]),/5 screenshots/);
});
test('configurable PDF URL limits and partial processing labels',()=>{
 assert.match(intakeError(counts,['a','b'],'',[],{url:1,pdf:1}),/1 URLs/);
 assert.equal(sourceStatus({processing_status:'READY',extraction_status:'UNAVAILABLE'}),'Partially processed — page unavailable');
 assert.match(sourceStatus({processing_status:'FAILED',extraction_status:'FAILED'}),/Unavailable/);
 assert.match(sourceStatus({processing_status:'NEEDS_REVIEW',extraction_status:'SUCCESS'}),/review required/);
});
test('compact graph preserves original records, states and expansion',()=>{
 const nodes=[{id:'case',type:'case',label:'Opportunity'},...Array.from({length:100},(_,i)=>({id:`claim${i}`,type:'claim',label:`Claim ${i}`}))];
 const edges=nodes.slice(1).map(n=>({id:`edge${n.id}`,source:'case',target:n.id,relation:'contains',relationship_status:'CLAIMED'}));
 const view=graphOverview(nodes,edges);assert.equal(view.nodes.length,2);assert.equal(view.edges.length,1);
 assert.equal(view.nodes.find(n=>n.type==='claim')?.members?.length,100);assert.equal(view.edges[0].relationship_status,'CLAIMED');
 assert.equal(graphOverview(nodes,edges,['claim']).nodes.length,101);assert.equal(nodes.length,101);assert.equal(edges.length,100);
});

test('program overview retains six key concepts and expands all underlying records',()=>{
 const core=['organization','program','domain','payment_policy','partnership','verification'].map(type=>({id:type,type,label:type}));
 const advanced=Array.from({length:40},(_,i)=>({id:`claim${i}`,type:'claim',label:`Claim ${i}`}));
 const all=[...core,...advanced];const compact=graphOverview(all,[]);
 assert.equal(compact.nodes.length,7);assert.ok(core.every(n=>compact.nodes.some(v=>v.id===n.id)));
 assert.equal(compact.nodes.find(n=>n.type==='program_details')?.members?.length,40);
 assert.equal(graphOverview(all,[],['*']).nodes.length,46);
});
