import test from 'node:test';
import assert from 'node:assert/strict';
import {assessmentLabel,riskIndex,researchLabel} from '../src/components/common/assessmentSemantics.ts';
import {summarizeVerification} from '../src/components/common/verificationSummary.ts';
test('unknown and legacy reassuring labels always abstain',()=>{for(const s of ['LOW RISK','LOW','INSUFFICIENT_INFORMATION','UNDETERMINED','',undefined])assert.equal(assessmentLabel(s),'Undetermined');});
test('concern labels remain distinct from authenticity',()=>{for(const s of ['HIGH','CRITICAL RISK','ELEVATED_CONCERN'])assert.equal(assessmentLabel(s),'Elevated concern');assert.equal(riskIndex(100,'LOW RISK'),'Undetermined');assert.equal(riskIndex(null,'UNDETERMINED'),'Undetermined');assert.equal(riskIndex(15,'ELEVATED CONCERN'),'85/100');});
test('research completion and outages both leave offer verification unresolved',()=>{assert.match(researchLabel('COMPLETED'),/Context retrieved.*unresolved/);assert.match(researchLabel('SEARCH_UNAVAILABLE'),/unavailable.*unresolved/);assert.match(researchLabel('SEARCH_NOT_PERFORMED'),/unresolved/);});
test('completed or historical passed content rules never become independent verification',()=>{const r=summarizeVerification(['completed','verified','passed','unavailable'].map(status=>({status})));assert.equal(r.verified,0);assert.equal(r.completed,3);assert.equal(r.unresolved,4);assert.equal(r.failed,0);});
