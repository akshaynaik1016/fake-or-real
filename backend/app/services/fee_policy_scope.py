"""Conservative category/stage/condition scope; absence of scope is not equality."""
import re
CATEGORY=r'GEN|General|UR|EWS|OBC|SC|ST|PwBD|PwD|ESM'
def category_values(text):
    names={'GENERAL':'GEN','UR':'GEN','PWD':'PWBD'}
    return list(dict.fromkeys(names.get(x.upper(),x.upper()) for x in re.findall(r'\b(?:'+CATEGORY+r')\b',text,re.I)))
def policy_rules(claims,text):
    from app.scanners.payment_context import sentence_bounds
    notices=list(dict.fromkeys(c['normalized_value'] for c in claims if c['claim_type']=='advertisement_number'))
    rules=[]
    for c in claims:
        if c['claim_type'] not in {'fee_applicability','fee_exemption'}:continue
        a,b=sentence_bounds(text,c['location']['start'],c['location']['end'])
        excerpt=text[a:b];lower=excerpt.casefold()
        cats=category_values(str(c['value']))
        stage='interview' if re.search(r'\binterview\s+(?:stage|fee)',lower) else 'training' if re.search(r'\btraining\s+(?:stage|fee)',lower) else 'application' if re.search(r'\bapplication\s+fee',lower) else None
        condition=re.search(r'\b(?:if|unless|except|provided that|subject to|residen(?:t|ts) of|domicil(?:e|ed) in)\b[^.;\n]{1,160}',excerpt,re.I)
        condition=condition.group().strip().casefold() if condition else None
        # Only an explicit universal scope + exact notice can establish sameness;
        # otherwise a same-category overlap is a possible inconsistency.
        universal=bool(re.search(r'\ball\s+(?:applicants|candidates)(?:\s+in\s+(?:this|the)\s+category)?\b',excerpt,re.I))
        rules.append(({'categories':cats,'policy':'EXEMPT' if c['claim_type']=='fee_exemption' else 'PAYMENT_REQUIRED',
            'fee_type':'APPLICATION_FEE' if stage=='application' else 'OTHER','stage':stage,'condition':condition,
            'scope':'ALL_APPLICANTS' if universal else 'UNRESOLVED','notice':notices[0] if len(notices)==1 else None},a,b))
    return rules

def scope_comparison(a,b):
    if a.get('notice') and b.get('notice') and a['notice']!=b['notice']:return 'NOT_COMPARABLE'
    if a.get('stage') and b.get('stage') and a['stage']!=b['stage']:return 'CONTEXT_DEPENDENT'
    if a.get('condition') and b.get('condition') and a['condition']!=b['condition']:return 'CONTEXT_DEPENDENT'
    if a.get('notice') and a.get('notice')==b.get('notice') and a.get('fee_type')==b.get('fee_type')=='APPLICATION_FEE' and a.get('stage')==b.get('stage')=='application' and a.get('scope')==b.get('scope')=='ALL_APPLICANTS' and a.get('condition')==b.get('condition'):
        return 'CONFIRMED_CONTRADICTION'
    return 'POSSIBLE_INCONSISTENCY'
