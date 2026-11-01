"""Describe what each check established, including checks that did not run."""
import re


def verification_summary(checks: list[dict]) -> dict:
    counts = dict.fromkeys(['verified','failed','warning','unavailable','not_performed'],0)
    for check in checks:
        status = 'verified' if check.get('status') == 'passed' else check.get('status')
        counts[status if status in counts else 'unavailable'] += 1
    counts['unresolved'] = counts['warning']+counts['unavailable']+counts['not_performed']
    counts['text'] = f"{counts['failed']} failed · {counts['unresolved']} unresolved · {counts['verified']} verified"
    return counts


def build_verification_checklist(*, content, domain, org, organization, dns, tls, email, phone, threat, payment, sensitive, document, synthetic=False):
    checks=[]
    def add(name,status,details): checks.append({'check_name':name,'status':status,'details':details})
    if not org: add('Organization','not_performed','No organization claim identified.')
    elif not domain: add('Organization','warning','Organization identified; no submitted website domain compared. Sender authorization remains unknown.')
    elif organization and organization.get('mismatch'): add('Organization','failed',organization['explanation']+' Bundled reference comparison only.')
    else: add('Organization','warning','Bundled domain reference match or unknown organization; specific offer authorization remains unresolved.')
    if not domain: add('Domain','not_performed','No domain submitted for DNS inspection.')
    elif synthetic or (dns or {}).get('is_demo_source'): add('Domain','unavailable','Synthetic domain fixture; no live DNS/registration verification.')
    elif (dns or {}).get('status') != 'COMPLETED': add('Domain','unavailable','Live DNS disabled or unavailable; registration age unknown.')
    else: add('Domain','warning','DNS records observed; registration date and offer authorization remain unknown.')
    if not email.get('sender_email'): add('Email','not_performed','No sender email available.')
    elif any(f.get('severity') == 'critical' for f in email.get('flags',[])): add('Email','failed','Submitted sender details contain a deterministic identity inconsistency. Pasted headers do not authenticate the sender.')
    else: add('Email','warning',f"Submitted sender: {email['sender_email']}. Authenticity not independently verified.")
    if not re.search(r'\+\d[\d -]{7,}\d',content) and not re.fullmatch(r'\+?\d[\d -]{7,}\d',content.strip()):
        add('Phone','not_performed','No phone number submitted.')
    else: add('Phone','unavailable','No live phone reputation source queried; fixture complaints are not verification.')
    if not domain: add('SSL','not_performed','No website domain submitted.')
    elif synthetic or (tls or {}).get('is_demo_source'): add('SSL','unavailable','Synthetic TLS fixture; no live certificate verification.')
    elif (tls or {}).get('status') == 'UNAVAILABLE': add('SSL','unavailable','TLS check disabled or unavailable.')
    elif (tls or {}).get('is_valid'): add('SSL','verified','TLS certificate validated; HTTPS does not authenticate the offer.')
    else: add('SSL','unavailable','No TLS certificate verified.')
    live=[p for p in (threat or {}).get('provider_results',[]) if not p.get('is_demo_intelligence')]
    if not threat: add('Threat Intelligence','not_performed','No target for threat lookup.')
    elif any(p.get('status') == 'FLAGGED' for p in live): add('Threat Intelligence','failed','A live provider flagged the submitted target; inspect provider evidence.')
    elif any(p.get('status') == 'CLEAN' for p in live): add('Threat Intelligence','verified','Configured provider returned no active match; absence of a match does not prove safety.')
    else: add('Threat Intelligence','unavailable','No live threat provider returned a result.')
    if not content.strip(): add('Payment','not_performed','No text to inspect.')
    elif payment['payment_detected']: add('Payment','failed','Payment-related finding in submitted text. Inspect amount-specific evidence; ambiguous amounts are not inferred.')
    else: add('Payment','verified','Content rules completed: no payment demand observed. This does not verify the offer.')
    if not document: add('Document','not_performed','No document parser or reviewed OCR content submitted.')
    elif document.get('has_manipulation_indicators'): add('Document','warning','Document metadata indicators require review; editing is not proof of fraud.')
    elif document.get('ocr_status') in {'EMPTY','ERROR','UNAVAILABLE'}: add('Document','warning','Original OCR was incomplete; investigation uses user-entered reviewed text.')
    else: add('Document','verified','Document text processed; this does not verify issuer identity or authenticity.')
    if sensitive.get('has_critical'): add('Identity','failed','Critical credential-related content observed; inspect the exact request.')
    elif sensitive.get('has_medium'): add('Identity','warning','Government identity document request observed; authorization unresolved.')
    elif content.strip(): add('Identity','verified','Content rules completed: no sensitive identity request observed.')
    else: add('Identity','not_performed','No text to inspect.')
    return checks
