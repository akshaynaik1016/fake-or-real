"""Cited, deterministic claims. Missing fields remain missing; filenames are unused."""
from decimal import Decimal,InvalidOperation
import json
import re
from uuid import uuid5,NAMESPACE_URL
from app.scanners.payment_scanner import analyze_payment_risk
from app.scanners.org_scanner import organization_mentions
from app.scanners.sensitive_data_scanner import analyze_sensitive_data_requests

CLAIM_TYPES=['organization','opportunity_type','role','compensation','fee','duration','recruiter_name',
             'sender_email','application_url','application_method','contact_number','sensitive_data_request','urgency','advertisement_number','job_title','publication_date','vacancies','application_deadline','eligibility','fee_exemption','official_website','payment_channel','payment_destination']

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
    from app.scanners.org_scanner import organization_role_mentions
    for role in organization_role_mentions(text):
        add('organization_role',{'name':role['canonical_name'],'role':role['role'],'primary':role['primary']},role['start'],role['end'],role['extraction_method'])
        if role['role']=='CLAIMED_COLLABORATOR':add('claimed_collaborator',role['display_name'],role['start'],role['end'],role['extraction_method'])
    for mention in organization_mentions(text):
        add('organization',mention['canonical_name'],mention['start'],mention['end'],mention['extraction_method'])
    from app.services.program_claims import program_fields
    for kind,value,start,end,method in program_fields(text):add(kind,value,start,end,method)
    for m in re.finditer(r'\b(internship|scholarship|job(?:\s+offer)?|employment)\b',text,re.I):
        if not any(c['claim_type']=='opportunity_type' for c in result):add('opportunity_type',m.group().lower().split()[0],m.start(),m.end())
        break
    for kind,pattern in [
        ('role',r'(?im)^\s*(?:role|position|job title|internship role)\s*:\s*([^\n.;]{2,150})'),
        ('recruiter_name',r'(?im)^\s*(?:recruiter(?: name)?|recruitment coordinator|contact person|HR contact)\s*:\s*([A-Za-z][A-Za-z .-]{1,90})(?=\n|$)'),
    ]:
        for m in re.finditer(pattern,text):add(kind,m.group(1).strip(),m.start(1),m.end(1))
    from app.services.recruitment_claims import recruitment_fields
    for kind,value,start,end,method in recruitment_fields(text):add(kind,value,start,end,method)
    money=analyze_payment_risk(text)
    for m in money['monetary_entities']:
        if m['role'] not in {'PAYMENT','COMPENSATION','CONTRACTUAL_LIABILITY','REIMBURSEMENT'}:continue
        if m['role']=='PAYMENT' and Decimal(m['value'])<=0:continue
        add({'PAYMENT':'fee','COMPENSATION':'compensation','CONTRACTUAL_LIABILITY':'contractual_penalty','REIMBURSEMENT':'reimbursement'}[m['role']],
            ({k:m[k] for k in ['value','currency','category','period']}|({k:m[k] for k in ['amount_role','applicability'] if k in m} if m['category']=='APPLICATION_FEE' else {})),m['start'],m['end'],'monetary_context')
    for tax in money['monetary_entities']:
        if tax['role']=='TAX':add('tax_component',{k:tax[k] for k in ['value','currency','category']},tax['start'],tax['end'],'explicit_tax_component')
    for item in money['monetary_entities']:
        if item.get('amount_role')=='BASE_FEE' and item.get('related_amount_spans'):
            refs=item['related_amount_spans'];from app.scanners.payment_scanner import MONEY
            amounts=[MONEY.fullmatch(r['text']) for r in refs]
            if all(amounts):add('fee_relation',{'base':amounts[0].group('number').replace(',',''),'total':amounts[1].group('number').replace(',',''),'currency':item['currency'],'relationship':'STATED_GST_TOTAL'},refs[0]['start'],refs[1]['end'],'explicit_tax_relation')
    for m in re.finditer(r'(?im)\b(?:duration\s*:?\s*|internship\s+(?:lasts|for)\s+)(\d{1,2})\s*(days?|weeks?|months?|years?)\b',text):
        add('duration',{'number':int(m.group(1)),'unit':m.group(2).lower().rstrip('s')},m.start(),m.end())
    for m in re.finditer(r'\b(\d{1,2})\s*[- ]\s*(weeks?|months?|years?)\s+internship\b',text,re.I):
        add('duration',{'number':int(m.group(1)),'unit':m.group(2).lower().rstrip('s')},m.start(),m.end())
    for m in re.finditer(r'[\w.+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)+',text):
        prefix=text[max(0,m.start()-80):m.start()]
        sender=bool(re.search(r'(?:from|sender(?:\s+email)?|recruit(?:er|ment)\s+email)\s*:\s*(?:[^\n<]*<)?\s*$',prefix,re.I))
        add('sender_email' if sender else 'contact_email',m.group().lower(),m.start(),m.end(),'email_parser')
    for m in re.finditer(r'https?://[^\s<>"\']+',text):
        value=m.group().rstrip(').,;')
        add('application_url',value,m.start(),m.start()+len(value),'observed_url')
    if input_type=='url' and submitted_content:
        add('application_url',submitted_content.strip(),0,len(submitted_content),'submitted_url','submitted_content')
    for m in re.finditer(r'\b(?:apply|submit (?:your )?application)\s+(?:(only)\s+)?(?:via|through|by|using|on)\s+(?:the\s+)?(email|e-mail|official\s+(?:portal|website)|portal|website|WhatsApp|Telegram|DM|direct message|online|in person)\b',text,re.I):
        channel=m.group(2).lower().replace('e-mail','email').replace('official ','')
        add('application_method',{'channel':channel,'exclusive':bool(m.group(1))},m.start(),m.end())
    for m in re.finditer(r'\+\d[\d ()-]{7,18}\d|(?im:^\s*(?:phone|contact number|mobile)\s*:\s*)([\d ()+-]{8,20})',text):
        add('contact_number',re.sub(r'[^+\d]','',m.group(1) or m.group()),m.start(1) if m.group(1) else m.start(),m.end(1) if m.group(1) else m.end())
    for m in re.finditer(r'\b(?:within\s+\d+\s+(?:hours?|minutes?)|act\s+immediately|offer\s+expires\s+today|only\s+\d+\s+seats?\s+left|last\s+chance|immediate\s+confirmation\s+required)\b',text,re.I):
        add('urgency',m.group(),m.start(),m.end(),'urgency_rule')
    for m in re.finditer(r'(?<![\w@])(?:[a-zA-Z0-9-]+\.)+(?:com|org|net|in|xyz|online|top|io|example)\b',text):
        add('domain',m.group().lower(),m.start(),m.end(),'observed_domain')
    sensitive=analyze_sensitive_data_requests(text)
    for item in sensitive.get('account_instructions',[]):
        add('account_instruction',item['classification'],item['start'],item['end'],'account_instruction_context')
    for item in sensitive.get('items',[]):
        add('sensitive_data_request',{'item':item['label'],'tier':item['tier']},item['start'],item['end'],'sensitive_data_rule')
    for m in re.finditer(r'\b(?:no\s+(?:registration\s+|application\s+|training\s+)?fees?|never\s+charge\s+(?:candidates|applicants)|without\s+(?:any\s+)?fees?)\b',text,re.I):
        if not re.search(r'\b(?:for|except|SC|ST|PwBD|category|categories)\b',text[m.end():m.end()+90],re.I) and not re.search(r'\b(?:SC|ST|PwBD|ESM|EWS|OBC|General|UR)\b[^.\n]{0,50}$',text[max(0,m.start()-65):m.start()],re.I):add('fee_policy','NO_FEES',m.start(),m.end())
    from app.services.fee_policy_scope import policy_rules
    for value,start,end in policy_rules(result,text):add('fee_policy_rule',value,start,end,'category_stage_scope_parser')
    return result
