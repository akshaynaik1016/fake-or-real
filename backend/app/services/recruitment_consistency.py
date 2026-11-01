"""Cited policy overlap, with scope unknowns kept separate from contradictions."""
from uuid import uuid5,NAMESPACE_URL
from app.services.fee_policy_scope import scope_comparison

def internal_policy_findings(claims):
    rules=[c for c in claims if c['claim_type']=='fee_policy_rule'];findings=[]
    for category in ['GEN','EWS','OBC','SC','ST','PWBD','ESM']:
        positive=[c for c in rules if category in c['value']['categories'] and c['value']['policy']=='PAYMENT_REQUIRED']
        negative=[c for c in rules if category in c['value']['categories'] and c['value']['policy']=='EXEMPT']
        pairs=[(a,b,scope_comparison(a['value'],b['value'])) for a in positive for b in negative if a['source_id']==b['source_id']]
        pairs=[p for p in pairs if p[2] in {'POSSIBLE_INCONSISTENCY','CONFIRMED_CONTRADICTION'}]
        if not pairs:continue
        certain=all(p[2]=='CONFIRMED_CONTRADICTION' for p in pairs)
        rows=list({c['id']:c for a,b,_ in pairs for c in [a,b]}.values())
        refs=[{'source_id':c['source_id'],'source_title':'Submitted fee policy','claim_id':c['id'],'excerpt':c['excerpt'],**c['location']} for c in rows]
        key='fee_category_inconsistency:'+category
        findings.append({'id':str(uuid5(NAMESPACE_URL,key+':'.join(c['claim_id'] for c in refs))),
            'category':'recruitment_policy_conflict','severity':'moderate','fact_key':key,'confidence':0.9,
            'evidence':(('Conflicting submitted policies' if certain else 'Possible inconsistency — needs clarification')+f' for {category}: payment and exemption passages overlap. '+('The exact notice, application stage and explicit applicant scope match.' if certain else 'The same notice, stage, conditions and applicant scope have not all been established.')),
            'source':'Contextual recruitment policy comparison','explanation':'Compare the full category, stage and applicability conditions independently before paying. Different scoped rules can coexist. This is not proof of document fraud.',
            'observed_value':category,'origin':'DETERMINISTIC_RULE','verification_status':'OBSERVED_POLICY_CONTRADICTION' if certain else 'OBSERVED_POLICY_INCONSISTENCY','correlation_group':'payment',
            'source_id':refs[0]['source_id'],'source_ids':list(dict.fromkeys(r['source_id'] for r in refs)),
            'source_spans':[{'start':r['start'],'end':r['end'],'text':r['excerpt'],'kind':'fee_policy_context',**({'page':r['page']} if r.get('page') else {})} for r in refs],
            'citations':refs,'original_excerpt':refs[0]['excerpt'],'extraction_method':'category_fee_policy_comparison','claim_type':'fee_applicability',
            'extracted_value':{'category':category,'required_and_exempt':True,'comparison':'CONFIRMED_CONTRADICTION' if certain else 'POSSIBLE_INCONSISTENCY'},'provenance_kind':'RULE_OUTPUT'})
    return findings
