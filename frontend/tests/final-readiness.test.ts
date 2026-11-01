import test from 'node:test';
import assert from 'node:assert/strict';
import {concernIndex,riskIndex} from '../src/components/common/assessmentSemantics.ts';
import {intakeError} from '../src/components/cases/intakeValidation.ts';
test('not scored is distinct from a zero concern estimate, legacy helper retained',()=>{
 assert.equal(concernIndex(null,'UNDETERMINED'),'Not scored');assert.equal(riskIndex(null,'UNDETERMINED'),'Undetermined');assert.equal(concernIndex(25,'ELEVATED CONCERN'),'75/100');
});
test('all-format queue accepts five images and rejects six without requiring a PDF or URL',()=>{
 const counts={total:0,screenshot:0,pdf:0,url:0};
 assert.equal(intakeError(counts,[],'Synthetic message',[]),'');
 assert.equal(intakeError(counts,['https://synthetic.example'],'Synthetic message',[{name:'synthetic.pdf'},...Array.from({length:5},(_,i)=>({name:`${i}.png`}))]),'');
 assert.match(intakeError(counts,[],'Synthetic message',Array.from({length:6},()=>({name:'x.png'}))),/5 screenshots/);
});
