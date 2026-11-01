"""Submitted program descriptions; no inferred employer/partner authorization."""
import re

def program_fields(text):
    fields=[]
    def add(kind,value,m):fields.append((kind,value,m.start(),m.end(),'explicit_program_context'))
    for m in re.finditer(r'\btraining\s*(?:\+|and|&)\s*internship\b',text,re.I):add('opportunity_type','Training + Internship',m)
    for m in re.finditer(r'\b(?:duration\s*:\s*)?(\d{1,2})\s*[–—-]\s*(\d{1,2})\s*(months?|weeks?)\b',text,re.I):
        add('duration_range',{'minimum':int(m[1]),'maximum':int(m[2]),'unit':m[3].lower().rstrip('s')},m)
    for m in re.finditer(r'(?im)^.*\b(?:internship\s+)?certificat\w*\b[^\n]*',text):
        if re.search(r'\bDice\s+ID\b',m.group(),re.I):
            # This is quoted association wording, not proof of an issuer's identity.
            add('certificate_association',m.group().strip(),m)
        elif re.search(r'\b(?:issued\s+by|association|associated\s+with)\b',m.group(),re.I):add('certificate_association',m.group().strip(),m)
    for m in re.finditer(r'\bPlacement\s+Assistance\s*\(\s*100%\s+Guarantee\s*\)',text,re.I):
        add('placement_promise',{'wording':m.group(),'scope':'PLACEMENT_ASSISTANCE','job_guaranteed':None},m)
    for m in re.finditer(r'\b(?:100%\s+guaranteed\s+job\s+placement|guaranteed\s+job\s+placement)\b',text,re.I):
        add('placement_promise',{'wording':m.group(),'scope':'JOB_PLACEMENT','job_guaranteed':True},m)
    for m in re.finditer(r'\btraining\s+fees?\s+(?:are\s+|is\s+)?applicable\b',text,re.I):
        add('fee_policy_disclosure',{'category':'TRAINING_FEE','applies':True,'amount':None,'authorization':'UNRESOLVED'},m)
    return fields

def program_unknowns(claims):
    if not any(c['claim_type']=='fee_policy_disclosure' for c in claims):return []
    unknowns=[]
    if not any(c['claim_type']=='fee' and c['value'].get('category')=='TRAINING_FEE' for c in claims):unknowns.append('Exact training fee is unspecified.')
    if not any(c['claim_type']=='payment_destination' for c in claims):unknowns.append('Payment recipient is not identified in the available claims.')
    unknowns+=['Refund policy and whether training/internship are separate offerings require clarification.']
    if any(c['claim_type']=='claimed_collaborator' for c in claims):unknowns.append('Authorization of the claimed partnerships has not been independently established.')
    if any(c['claim_type']=='certificate_association' for c in claims):unknowns.append('Claimed certificate association/issuer authorization remains unresolved.')
    if any(c['claim_type']=='placement_promise' and c['value']['scope']=='PLACEMENT_ASSISTANCE' for c in claims):unknowns.append('The guarantee refers to placement assistance; guaranteed job placement is not established.')
    return unknowns


def claim_display(value):
    if value is None:return 'Unspecified'
    if isinstance(value,dict):return '; '.join(k.replace('_',' ')+': '+claim_display(v) for k,v in value.items() if v is not None)
    if isinstance(value,list):return ', '.join(claim_display(v) for v in value)
    return str(value)
