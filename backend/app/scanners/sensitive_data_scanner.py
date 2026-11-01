import re
from typing import Dict, Any, List

SENSITIVE_DATA_TAXONOMY = {
    "CRITICAL": [
        (r"(?i)\b(otp|one\s*time\s*password)\b", "OTP (One-Time Password)"),
        (r"(?i)\b(upi\s*pin|atm\s*pin|mpin)\b", "UPI / ATM Security PIN"),
        (r"(?i)\b(cvv|cvc|security\s*code)\b", "Card CVV / Security Code"),
        (r"(?i)\b((?:login\s*|netbanking\s*)?password|credentials)\b", "Account Password / Credentials"),
        (r"(?i)\b(card\s*number|debit\s*card\s*details|credit\s*card\s*number)\b", "Full Card Number"),
        (r"(?i)\b(biometric|fingerprint|face\s*scan\s*credentials)\b", "Biometric Authentication Data")
    ],
    "MEDIUM": [
        (r"(?i)\b(aadhaar(\s*card)?|uidai)\b", "Aadhaar Card / Number"),
        (r"(?i)\b(pan(\s*card)?|permanent\s*account\s*number)\b", "PAN Card"),
        (r"(?i)\b(passport(\s*copy|\s*number)?)\b", "Passport Details"),
        (r"(?i)\b(driving\s*licen[sc]e|voter\s*id)\b", "Driver's License / Voter ID"),
        (r"(?i)\b(bank\s*account(\s*number)?|ifsc(\s*code)?|cancelled\s*cheque)\b", "Bank Account / IFSC Details")
    ],
    "LOW": [
        (r"(?i)\b(resume|cv|curriculum\s*vitae)\b", "Resume / Curriculum Vitae"),
        (r"(?i)\b(portfolio|github\s*profile|linkedin\s*profile)\b", "Professional Portfolio / Profile"),
        (r"(?i)\b(marksheet|degree\s*certificate|college\s*id)\b", "Educational Marksheet / College ID")
    ]
}


REQUEST_VERBS=r'\b(?:send|sends|sending|sent|share|shares|sharing|shared|submit(?:s|ted|ting)?|upload(?:s|ed|ing)?|provid(?:e|es|ed|ing)|enter(?:s|ed|ing)?|attach(?:es|ed|ing)?|forward(?:s|ed|ing)?|requir(?:e|es|ed|ing)|request(?:s|ed|ing)?|need(?:s|ed|ing)?|verif(?:y|ies|ied|ying)|confirm(?:s|ed|ing)?)\b'

def credential_context(text,start,end):
    from app.scanners.payment_context import sentence_bounds,span
    a,b=sentence_bounds(text,start,end);local=text[a:b];prefix=text[a:start]
    # Explicit outward disclosure takes priority over a nearby login/create phrase.
    outward=re.search(r'\b(?:send|share|forward|disclose|tell|give|provide|submit|email|whatsapp)\b',prefix,re.I)
    third_party=re.search(r'\b(?:to\s+(?:the\s+)?(?:recruiter|coordinator|me|us|agent)|with\s+(?:the\s+)?(?:recruiter|coordinator|me|us)|personal\s+(?:email|number)|WhatsApp|Telegram)\b',local,re.I)
    system_send=bool(re.search(r'\b(?:system|portal|website)\b.{0,60}\b(?:send|email|generate)\w*\b.{0,80}(?:credentials|password).{0,80}\b(?:your\s+)?(?:registered\s+)?(?:email|e-mail)',local,re.I|re.S))
    system_send=system_send or bool(re.search(r'(?:password|credentials).{0,60}(?:will be|are)\s+sent.{0,60}(?:registered|your)\s+email',local,re.I|re.S))
    system_send=system_send or bool(re.search(r'(?:password|credentials).{0,120}(?:will be|are)\s+sent.{0,120}(?:registered|same).{0,25}(?:e\s*-?\s*mail|email|mobile)',local,re.I|re.S))
    registration=bool(re.search(r'\b(?:create|choose|set|reset|generate)\s+(?:(?:a|your|new|account)\s+){0,3}password|\b(?:log\s*in|login|sign\s*in)\b.{0,100}\bpassword|\bpassword\b.{0,100}\b(?:log\s*in|login|sign\s*in)',local,re.I|re.S))
    registration=registration or bool(re.search(r'\b(?:log\s*on|log\s*in|login|sign\s*in)\b.{0,180}\b(?:credentials|password|OTP)\b|\b(?:credentials|password)\b.{0,120}\b(?:login|account|application|call\s+letter)\b',local,re.I|re.S))
    pronoun_leak=bool(re.search(r'\b(?:send|share|forward|give)\s+(?:it|these|them)\b',local,re.I))
    if re.search(r"\b(?:never|don't|do\s+not|not\s+required|no\s+need\s+to)\b",prefix[-140:],re.I):return 'NEGATED_ADVICE',a,b
    if (third_party and (outward or pronoun_leak)) or (outward and not system_send and re.search(r'\b(?:send|share|forward|disclose|tell|give|email|whatsapp)\b',prefix,re.I)):return 'OUTWARD_CREDENTIAL_REQUEST',a,b
    if system_send:return 'SYSTEM_ACCOUNT_DELIVERY',a,b
    if registration:return 'ACCOUNT_ACCESS_INSTRUCTION',a,b
    if re.search(REQUEST_VERBS,prefix[-180:],re.I):return 'OUTWARD_CREDENTIAL_REQUEST',a,b
    return 'MENTION_ONLY',a,b


def analyze_sensitive_data_requests(text: str) -> Dict[str, Any]:
    from app.scanners.payment_context import span,sentence_bounds
    text=text or '';items=[];flags=[];normal=[]
    for tier,patterns in SENSITIVE_DATA_TAXONOMY.items():
        for pattern,label in patterns:
            for match in re.finditer(pattern,text):
                if label=='Passport Details' and re.match(r'\s*[- ]?\s*(?:size|sized|style)\s+(?:photo|photograph)',text[match.end():],re.I):continue
                context,a,b=credential_context(text,match.start(),match.end())
                if tier=='CRITICAL':
                    if context in {'SYSTEM_ACCOUNT_DELIVERY','ACCOUNT_ACCESS_INSTRUCTION'}:
                        normal.append({'classification':context,'item':label,'excerpt':text[a:b],
                            'start':a,'end':b,'page':span(text,a,b,'account_instruction')['page'],
                            'rationale':'Account registration/login or system-to-applicant delivery is described. The portal and document remain unverified.'})
                        continue
                    if context!='OUTWARD_CREDENTIAL_REQUEST':continue
                else:
                    prefix=text[max(a,match.start()-180):match.start()]
                    if context=='NEGATED_ADVICE' or not re.search(REQUEST_VERBS,prefix,re.I):continue
                items.append({'tier':tier,'label':label,'match':match.group(),'start':match.start(),'end':match.end()})
                code='CRITICAL_CREDENTIAL_REQUEST' if tier=='CRITICAL' else 'GOVERNMENT_ID_REQUEST' if tier=='MEDIUM' else 'STANDARD_APPLICATION_DATA'
                flags.append({'tier':tier,'severity':'critical' if tier=='CRITICAL' else 'moderate' if tier=='MEDIUM' else 'low','code':code,
                    'message':('Outward credential disclosure request: ' if tier=='CRITICAL' else 'Submitted document request: ')+label+'.',
                    'detail':'Do not disclose passwords, OTPs, PINs or authentication secrets to a recruiter. Login instructions alone are not classified as disclosure.' if tier=='CRITICAL' else 'Verify the purpose and authorized recipient before sharing personal documents.',
                    'observed_value':match.group(),'source_spans':[span(text,match.start(),match.end(),'sensitive_data_request'),span(text,a,b,'request_context')],
                    'fact_key':'credential_disclosure' if tier=='CRITICAL' else 'document_request:'+label})
    normal=list({(i['start'],i['end'],i['classification']):i for i in normal}.values())
    tiers={i['tier'] for i in items}
    return {'detected_tiers':sorted(tiers),'items':items,'flags':flags,'has_critical':'CRITICAL' in tiers,'has_medium':'MEDIUM' in tiers,
        'has_sensitive_requests':bool(items),'account_instructions':normal,
        'detected_requests':[{'severity':i['tier'],**i} for i in items]}


def scan_sensitive_data(text: str) -> Dict[str, Any]:
    return analyze_sensitive_data_requests(text)
