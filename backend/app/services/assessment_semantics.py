"""One conservative presentation contract; content completion never authenticates an offer."""
from copy import deepcopy

INELIGIBLE={'SYNTHETIC','EXTERNAL_SOURCE','AI_INTERPRETATION'}

def assessment_for(fusion,evidence,claims=()):
    concern=any(e.get('severity') in {'high','critical'} and e.get('origin') not in INELIGIBLE
        and e.get('verification_status') not in {'UNKNOWN','UNAVAILABLE','SYNTHETIC'} for e in evidence)
    # Claim-level verification requires a scoped independent record. No current
    # search/reference/content adapter creates this record.
    verified=[{'evidence_id':e['id'],'claim_id':e['verified_claim_id'],'scope':e['verification_scope']}
        for e in evidence if e.get('origin')=='EXTERNAL_SOURCE' and e.get('verification_status')=='INDEPENDENTLY_VERIFIED'
        and e.get('verified_claim_id') in {c['id'] for c in claims} and e.get('verification_scope') and e.get('source')]
    return {'state':'ELEVATED_CONCERN' if concern else 'UNDETERMINED',
        'label':'Elevated concern' if concern else 'Undetermined',
        'verification_status':'INDEPENDENTLY_VERIFIED_CLAIM' if verified else 'UNRESOLVED',
        'verified_claims':verified,'offer_authenticity':'UNRESOLVED',
        'risk_score':fusion.get('risk_score') if concern else None,
        'score_kind':'HEURISTIC_INDEX','confidence_kind':'HEURISTIC_RELIABILITY_INDEX',
        'explanation':'Observed concerns need investigation; they do not prove fraud.' if concern else
            'Insufficient independent evidence to establish authenticity. No suspicious finding is not proof of safety.'}

def integrity_view(state):
    state=deepcopy(state)
    for check in state.get('baseline',{}).get('verification_results',[]):
        if check.get('status') in {'passed','verified'}:check['status']='completed'
    state['assessment']=assessment_for(state['fusion'],state['evidence'],state.get('claims',[]))
    if state['assessment']['state']=='UNDETERMINED':
        state['fusion'].update(risk_level='UNDETERMINED',risk_score=None)
    return state

def scan_presentation(state):
    assessment=assessment_for(state['fusion'],state['evidence'],state.get('claims',[]))
    return {'assessment':assessment,'risk_level':assessment['state'].replace('_',' '),
        # Legacy trust stays in the raw stored baseline; primary API abstains.
        'trust_score':None if assessment['risk_score'] is None else 100-assessment['risk_score'],
        'analysis_confidence':state['fusion']['confidence'],
        'summary':assessment['label']+'. '+assessment['explanation']+' Verification of this specific offer remains unresolved.'}
