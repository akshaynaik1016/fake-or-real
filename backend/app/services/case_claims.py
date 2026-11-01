"""Cited, deterministic claims. Missing fields remain missing; filenames are unused."""
from decimal import Decimal,InvalidOperation
import json
import re
from uuid import uuid5,NAMESPACE_URL
from app.scanners.payment_scanner import analyze_payment_risk
from app.scanners.org_scanner import VERIFIED_ORGANIZATIONS_REGISTRY
from app.scanners.sensitive_data_scanner import analyze_sensitive_data_requests

CLAIM_TYPES=['organization','opportunity_type','role','compensation','fee','duration','recruiter_name',
             'sender_email','application_url','application_method','contact_number','sensitive_data_request']

def normalize(value):
    if isinstance(value,str):return re.sub(r'\s+',' ',value.casefold()).strip()
    if isinstance(value,dict) and 'currency' in value and 'value' in value:
        value={**value,'value':format(Decimal(value['value']).normalize(),'f')}
    return json.dumps(value,sort_keys=True,ensure_ascii=False)


def extract_claims(source_id:str,text:str,input_type:str,submitted_content:str='') -> list[dict]:
    result=[];seen=set()
    def add(kind,value,start,end,method='deterministic_regex',field='extracted_text'):
        original=text if field=='extracted_text' else submitted_content
        excerpt=original[start:end]
        if not excerpt or (kind,start,end) in seen:return
        seen.add((kind,start,end))
        location={'field':field,'start':start,'end':end}
        if input_type=='pdf':
            pages=list(re.finditer(r'--- Page (\d+) ---',text[:start]))
            if pages:location['page']=int(pages[-1].group(1))
        result.append({'id':str(uuid5(NAMESPACE_URL,f'{source_id}:{kind}:{start}:{end}:{normalize(value)}')),
            'source_id':source_id,'claim_type':kind,'value':value,'normalized_value':normalize(value),
            'excerpt':excerpt,'location':location,'extraction_method':method,'verification_status':'CLAIMED'})
    explicit=list(re.finditer(r'(?im)^\s*(?:organization|company|employer)\s*:\s*([^\n.;]{2,150})',text))
    if explicit:
        for m in explicit:
            value=m.group(1).strip()
            known=next((o['canonical_name'] for o in VERIFIED_ORGANIZATIONS_REGISTRY.values() if value.casefold() in [o['canonical_name'].casefold(),*o['aliases']]),value)
            add('organization',known,m.start(1),m.end(1))
    else:
        for org in VERIFIED_ORGANIZATIONS_REGISTRY.values():
            matches=[m for alias in org['aliases'] for m in re.finditer(r'\b'+re.escape(alias)+r'\b',text,re.I)]
            if matches:
                m=min(matches,key=lambda x:x.start());add('organization',org['canonical_name'],m.start(),m.end(),'bundled_name_reference')
    for m in re.finditer(r'\b(internship|scholarship|job(?:\s+offer)?|employment)\b',text,re.I):
        add('opportunity_type',m.group().lower().split()[0],m.start(),m.end())
        break
    for kind,pattern in [
        ('role',r'(?im)^\s*(?:role|position|job title|internship role)\s*:\s*([^\n.;]{2,150})'),
        ('recruiter_name',r'(?im)^\s*(?:recruiter(?: name)?|recruitment coordinator|contact person|HR contact)\s*:\s*([A-Za-z][A-Za-z .-]{1,90})(?=\n|$)'),
    ]:
        for m in re.finditer(pattern,text):add(kind,m.group(1).strip(),m.start(1),m.end(1))
    money=analyze_payment_risk(text)
    for m in money['monetary_entities']:
        if m['role'] not in {'PAYMENT','COMPENSATION'}:continue
        add('fee' if m['role']=='PAYMENT' else 'compensation',
            {k:m[k] for k in ['value','currency','category','period']},m['start'],m['end'],'monetary_context')
    for m in re.finditer(r'(?im)\b(?:duration\s*:?\s*|internship\s+(?:lasts|for)\s+)(\d{1,2})\s*(days?|weeks?|months?|years?)\b',text):
        add('duration',{'number':int(m.group(1)),'unit':m.group(2).lower().rstrip('s')},m.start(),m.end())
    for m in re.finditer(r'\b(\d{1,2})\s*[- ]\s*(weeks?|months?|years?)\s+internship\b',text,re.I):
        add('duration',{'number':int(m.group(1)),'unit':m.group(2).lower().rstrip('s')},m.start(),m.end())
    for m in re.finditer(r'[\w.+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+',text):
        prefix=text[max(0,m.start()-80):m.start()]
        sender=bool(re.search(r'(?:from|sender|recruit(?:er|ment)\s+email)\s*:\s*(?:[^\n<]*<)?\s*$',prefix,re.I))
        add('sender_email' if sender else 'contact_email',m.group().lower(),m.start(),m.end(),'email_parser')
    for m in re.finditer(r'https?://[^\s<>"\']+',text):
        value=m.group().rstrip(').,;')
        add('application_url',value,m.start(),m.start()+len(value),'observed_url')
    if input_type=='url' and submitted_content:
        add('application_url',submitted_content.strip(),0,len(submitted_content),'submitted_url','submitted_content')
    for m in re.finditer(r'\b(?:apply|submit (?:your )?application)\s+(?:(only)\s+)?(?:via|through|by|using|on)\s+(?:the\s+)?(email|e-mail|official\s+(?:portal|website)|portal|website|WhatsApp|Telegram|online|in person)\b',text,re.I):
        channel=m.group(2).lower().replace('e-mail','email').replace('official ','')
        add('application_method',{'channel':channel,'exclusive':bool(m.group(1))},m.start(),m.end())
    for m in re.finditer(r'\+\d[\d ()-]{7,18}\d|(?im:^\s*(?:phone|contact number|mobile)\s*:\s*)([\d ()+-]{8,20})',text):
        add('contact_number',re.sub(r'[^+\d]','',m.group(1) or m.group()),m.start(1) if m.group(1) else m.start(),m.end(1) if m.group(1) else m.end())
    for item in analyze_sensitive_data_requests(text).get('items',[]):
        m=re.search(re.escape(item['match']),text,re.I)
        if m:add('sensitive_data_request',{'item':item['label'],'tier':item['tier']},m.start(),m.end(),'sensitive_data_rule')
    for m in re.finditer(r'\b(?:no\s+(?:registration\s+|application\s+|training\s+)?fees?|never\s+charge\s+(?:candidates|applicants)|without\s+(?:any\s+)?fees?)\b',text,re.I):
        add('fee_policy','NO_FEES',m.start(),m.end())
    return result
