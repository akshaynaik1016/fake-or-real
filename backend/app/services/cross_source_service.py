from decimal import Decimal
from collections import defaultdict
from uuid import uuid5,NAMESPACE_URL
from urllib.parse import urlsplit

def citation(claim,sources):
    source=sources[claim['source_id']]
    return {'source_id':source['id'],'source_title':source['title'],'source_type':source['input_type'],
        'claim_id':claim['id'],'excerpt':claim['excerpt'],**claim['location']}


def compare_claims(case_id,claims,sources):
    findings={}
    def add(kind,classification,severity,description,rows):
        rows=sorted({c['id']:c for c in rows}.values(),key=lambda c:c['id'])
        key=str(uuid5(NAMESPACE_URL,case_id+kind+':'.join(c['id'] for c in rows)))
        findings[key]={'id':key,'kind':kind,'classification':classification,'severity':severity,
            'description':description,'citations':[citation(c,sources) for c in rows]}
    grouped=defaultdict(list)
    for c in claims:grouped[c['claim_type']].append(c)
    for kind,rows in grouped.items():
        agreement=defaultdict(list)
        for c in rows:agreement[c['normalized_value']].append(c)
        for group in agreement.values():
            if len({c['source_id'] for c in group})>1:
                add('SUPPORTING_CLAIMS','SUPPORTING_CLAIMS','low',
                    'Sources repeat the same '+kind.replace('_',' ')+' claim. Agreement is not independent verification.',group)
        for i,a in enumerate(rows):
            for b in rows[i+1:]:
                if a['source_id']==b['source_id'] or a['normalized_value']==b['normalized_value']:continue
                if sources[a['source_id']]['content_hash']==sources[b['source_id']]['content_hash']:continue
                classification='POSSIBLE_INCONSISTENCY'; severity='moderate'; description=None
                av,bv=a['value'],b['value']
                if kind=='compensation':
                    if Decimal(av['value'])==Decimal(bv['value']) and av['currency']==bv['currency'] and av['period']==bv['period'] and av['category']==bv['category']:continue
                    comparable=av['currency']==bv['currency'] and av['period'] is not None and av['period']==bv['period'] and av['category']==bv['category']
                    classification='CONFIRMED_CONTRADICTION' if comparable else 'POSSIBLE_INCONSISTENCY'
                    description='Different stated compensation amounts. '+('Currency, period and compensation type match.' if comparable else 'Currency, period or compensation context needs clarification.')
                elif kind=='duration':
                    def duration(v):
                        return ('month',v['number']*(12 if v['unit']=='year' else 1)) if v['unit'] in {'month','year'} else ('day',v['number']*(7 if v['unit']=='week' else 1))
                    da,db=duration(av),duration(bv)
                    if da==db:continue
                    classification='CONFIRMED_CONTRADICTION' if da[0]==db[0] else 'POSSIBLE_INCONSISTENCY'
                    description='Different stated opportunity durations; months are not assumed equal to a fixed number of weeks.'
                elif kind=='organization':
                    classification='CONFIRMED_CONTRADICTION';description='The submitted sources state different organization identities for this case.'
                elif kind in {'sender_email','contact_email'}:
                    if av.split('@')[-1]==bv.split('@')[-1]:continue
                    description='Recruiter/contact email domains differ. Different addresses alone do not establish impersonation.'
                elif kind=='application_url':
                    if urlsplit(av).hostname==urlsplit(bv).hostname:continue
                    description='Application URL hosts differ; both may be legitimate channels and require verification.'
                elif kind=='application_method':
                    if av['channel']==bv['channel']:continue
                    classification='CONFIRMED_CONTRADICTION' if av['exclusive'] or bv['exclusive'] else 'POSSIBLE_INCONSISTENCY'
                    description='Application instructions name different channels'+(' despite an explicit only-channel instruction.' if av['exclusive'] or bv['exclusive'] else '; exclusivity is not established.')
                if description:add(kind.upper()+'_CONFLICT',classification,severity,description,[a,b])
    policies=grouped.get('fee_policy',[])
    for fee in grouped.get('fee',[]):
        opposite=[c for c in policies if c['source_id']!=fee['source_id'] and c['value']=='NO_FEES']
        if opposite:
            add('FEE_INSTRUCTION_CONFLICT','CONFIRMED_CONTRADICTION','high','A source requests payment while another explicitly states no fees.',[fee,*opposite])
        elif len(sources)>1:
            add('NEW_PAYMENT_REQUEST','NEW_INFORMATION','high','Payment is requested in this source. A missing fee field in another source is not a contradiction.',[fee])
    return list(findings.values())
