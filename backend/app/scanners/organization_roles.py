"""Role-aware names with exact spans. Submitted roles never establish affiliation."""
import re

def extract_organization_roles(text,registry):
    rows=[];occupied=[]
    def add(a,b,role,method,primary=False):
        raw=text[a:b];value=re.sub(r'\s+',' ',raw).strip(' ,:[]')
        if not 2<=len(value)<=150:return
        ref=next((o for o in registry.values() if value.casefold() in [o['canonical_name'].casefold(),*[x.casefold() for x in o['aliases']]]),None)
        rows.append({'canonical_name':ref['canonical_name'] if ref else value,'display_name':value,'role':role,'primary':primary,'start':a,'end':b,'excerpt':raw,'extraction_method':method,'verification_status':'CLAIMED','reference':ref})
    # Capture role-bearing lists before considering a reference-name fallback.
    for m in re.finditer(r'\b(?:collaborat\w*|partner\w*|associat\w*)\s+(?:with\s+)?(?:[^\n\[.!?]{0,75})\[([^\]\n]{2,700})\]',text,re.I):
        for part in re.finditer(r'[^,;…]+',m.group(1)):
            a=m.start(1)+part.start();b=m.start(1)+part.end()
            while a<b and text[a].isspace():a+=1
            while b>a and text[b-1].isspace():b-=1
            add(a,b,'CLAIMED_COLLABORATOR','explicit_partner_list');occupied.append((a,b))
    for m in re.finditer(r'(?im)^[ \t]*(?:claimed\s+)?(?:partners?|collaborators?)\s*:\s*([^\n.!?]{2,500})',text):
        for part in re.finditer(r'[^,;]+',m.group(1)):
            a=m.start(1)+part.start();b=m.start(1)+part.end()
            while a<b and text[a].isspace():a+=1
            while b>a and text[b-1].isspace():b-=1
            add(a,b,'CLAIMED_COLLABORATOR','explicit_partner_list');occupied.append((a,b))
    role_labels=[('PRIMARY_ORGANIZER',r'organization|organisation|company|program\s+organizer|programme\s+organiser|organizer|organiser|organized by|organisation name|company name'),
                 ('CLAIMED_EMPLOYER',r'employer|hiring\s+company'),('CLAIMED_TRAINING_PROVIDER',r'training\s+provider'),
                 ('CLAIMED_CERTIFICATE_ISSUER',r'certificate\s+issuer|certificates?\s+issued\s+by'),('PAYMENT_RECIPIENT',r'payment\s+recipient|payee'),('CLAIMED_DOMAIN_OWNER',r'domain\s+owner|website\s+owner')]
    for role,label in role_labels:
        for m in re.finditer(r'(?im)^[ \t]*(?:'+label+r')\s*:\s*([^\n.;!]{2,150})',text):
            add(m.start(1),m.end(1),role,'explicit_organization_role',role in {'PRIMARY_ORGANIZER','CLAIMED_EMPLOYER','CLAIMED_TRAINING_PROVIDER'})
            occupied.append((m.start(1),m.end(1)))
    for m in re.finditer(r'(?im)\bGreetings\s+from\s+([A-Za-z][A-Za-z0-9& -]{1,80})(?=[!\n.,]|$)',text):
        add(m.start(1),m.end(1),'PRIMARY_ORGANIZER','sender_greeting',True);occupied.append((m.start(1),m.end(1)))
    for m in re.finditer(r'(?im)\b(?:organized|organised|offered|conducted)\s+by\s+([A-Za-z][A-Za-z0-9& -]{1,80})(?=[!\n.,]|$)',text):
        add(m.start(1),m.end(1),'PRIMARY_ORGANIZER','explicit_program_provider',True);occupied.append((m.start(1),m.end(1)))
    for m in re.finditer(r'(?m)^[ \t]*([A-Z][A-Z0-9&.-]*(?:[ \t]+[A-Z][A-Z0-9&.-]*){0,4}[ \t]+(?:TECH|TECHNOLOGIES|SOLUTIONS|SYSTEMS|LABS|FOUNDATION|PVT[.]? LTD[.]?|LIMITED|INC[.]?))[ \t]*$',text):
        if not re.search(r'\b(?:JOIN|APPLY|HIRING|INTERNSHIP|PROGRAM|WELCOME|OUR|YOUR)\b',m.group(1)):
            add(m.start(1),m.end(1),'PRIMARY_ORGANIZER','business_heading',True)
    # Natural-language partner mentions, including unknown organizations.
    for m in re.finditer(r'\b(?:in\s+(?:collaboration|partnership)\s+with|partners?\s+with|collaborat(?:e|es|ing)\s+with)\s+([A-Z][A-Za-z0-9& -]{1,80})(?=[,.!\n]|$)',text):
        add(m.start(1),m.end(1),'CLAIMED_COLLABORATOR','explicit_partner_phrase');occupied.append((m.start(1),m.end(1)))
    for org in registry.values():
        for m in sorted([m for alias in org['aliases'] for m in re.finditer(r'\b'+re.escape(alias)+r'\b',text,re.I)],key=lambda m:(m.start(),-len(m.group()))):
            if any(a<=m.start()<b for a,b in occupied):continue
            nearby=text[max(0,m.start()-80):m.end()+65]
            if re.search(r'certificat[^.!?\n]{0,70}$',text[max(0,m.start()-80):m.start()],re.I) or re.match(r'\s+(?:certificates?\b|Dice\s+ID\b)',text[m.end():],re.I):role='CLAIMED_CERTIFICATE_ASSOCIATION';primary=False
            elif re.search(r'partner|collaborat|MNCs?\s+Companies',text[max(0,m.start()-120):m.start()],re.I):role='CLAIMED_COLLABORATOR';primary=False
            else:role='CLAIMED_EMPLOYER';primary=True
            add(m.start(),m.end(),role,'contextual_name_reference',primary);occupied.append((m.start(),m.end()))
    # Explicit providers outrank incidental name-reference matches. No famous-company ranking.
    ranked=sorted([r for r in rows if r['primary']],key=lambda r:(r['extraction_method']=='contextual_name_reference',r['role']!='PRIMARY_ORGANIZER',r['start']))
    selected=ranked[0]['canonical_name'] if ranked else None
    for r in rows:r['primary']=r['primary'] and r['canonical_name']==selected
    unique={}
    for row in rows:unique.setdefault((row['start'],row['end'],row['role']),row)
    return sorted(unique.values(),key=lambda r:r['start'])
