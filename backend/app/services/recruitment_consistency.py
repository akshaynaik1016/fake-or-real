"""Cited internal policy inconsistencies; no independent authenticity conclusion."""
import re
from uuid import uuid5,NAMESPACE_URL

def internal_policy_findings(claims):
    exemptions=[c for c in claims if c['claim_type']=='fee_exemption']
    requirements=[c for c in claims if c['claim_type']=='fee_applicability' and c['value'].get('policy')=='PAYMENT_REQUIRED']
    findings=[]
    def ref(c):return {'source_id':c['source_id'],'source_title':'Submitted fee policy','claim_id':c['id'],'excerpt':c['excerpt'],**c['location']}
    for category in ['GEN','EWS','OBC','SC','ST','PwBD','ESM']:
        positives=[c for c in requirements if category in [x.upper().split()[0] for x in c['value']['categories']]]
        negatives=[c for c in exemptions if re.search(r'\b'+category+r'\b',str(c['value']),re.I)]
        if not positives or not negatives:continue
        refs=[ref(c) for c in [*positives,*negatives]];key='fee_category_inconsistency:'+category
        findings.append({'id':str(uuid5(NAMESPACE_URL,key+':'.join(c['claim_id'] for c in refs))),
            'category':'recruitment_policy_conflict','severity':'moderate','fact_key':key,'confidence':0.9,
            'evidence':f'Submitted fee instructions differ for {category}: payment is required in one passage and an exemption is stated elsewhere.',
            'source':'Contextual recruitment policy comparison','explanation':'Cited passages may use different eligibility scopes or contain an inconsistency. Confirm the exact category-specific rule independently before paying. This is not proof of document fraud.',
            'observed_value':category,'origin':'DETERMINISTIC_RULE','verification_status':'OBSERVED_POLICY_INCONSISTENCY','correlation_group':'payment',
            'source_id':refs[0]['source_id'],'source_ids':list(dict.fromkeys(r['source_id'] for r in refs)),
            'source_spans':[{'start':r['start'],'end':r['end'],'text':r['excerpt'],'kind':'fee_policy_context',**({'page':r['page']} if r.get('page') else {})} for r in refs],
            'citations':refs,'original_excerpt':refs[0]['excerpt'],'extraction_method':'category_fee_policy_comparison','claim_type':'fee_applicability',
            'extracted_value':{'category':category,'required_and_exempt':True},'provenance_kind':'RULE_OUTPUT'})
    return findings
