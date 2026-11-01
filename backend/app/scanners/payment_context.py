"""Context classifications are submitted observations, never payment authorization."""
import hashlib
import re
from decimal import Decimal

def digest(value):return hashlib.sha256(value.encode()).hexdigest()[:24]

def sentence_bounds(text,start,end):
    # PDF line wrapping is not a sentence boundary. Page markers always are.
    boundaries=list(re.finditer(r'(?<!Rs)\.(?=\s|$)|[!?;]|\n--- Page \d+ ---\n',text,re.I))
    left=max([0]+[m.end() for m in boundaries if m.end()<=start])
    right=min([len(text)]+[m.start() for m in boundaries if m.start()>=end])
    return max(left,start-350),min(right,end+350)

def page_at(text,start):
    pages=list(re.finditer(r'--- Page (\d+) ---',text[:start]))
    return int(pages[-1].group(1)) if pages else None

def span(text,start,end,kind):return {'start':start,'end':end,'text':text[start:end],'kind':kind,'page':page_at(text,start)}

def destination(text,start,end):
    a,b=sentence_bounds(text,start,end);local=text[a:b]
    personal=re.search(r'\b(?:personal|my|recruiter[’\x27]?s?|coordinator[’\x27]?s?)\s+(?:bank\s+)?(?:account|upi)|\b(?:outside|bypass|skip)\s+(?:the\s+)?(?:official\s+)?(?:application|portal|gateway)',local,re.I)
    nearest=lambda pattern: min(list(re.finditer(pattern,local,re.I)),key=lambda m:min(abs(a+m.start()-start),abs(a+m.end()-end)),default=None)
    upi=nearest(r'(?<![\w.-])[\w.-]{2,256}@(?:okaxis|okhdfcbank|oksbi|paytm|ybl|ibl|apl|axl|upi)(?![\w.-])')
    account=nearest(r'\b(?:account(?:\s+(?:number|no\.?))?|beneficiary|payee|recipient|payable to|in favou?r of)\s*[:#-]\s*([^\n.;]{2,90})')
    account_id=nearest(r'\baccount(?:\s+(?:number|no\.?))?\s*[:#-]\s*([A-Za-z0-9-]{3,34})')
    if account_id:account=account_id
    personal_name=nearest(r'\bto\s+([A-Za-z][A-Za-z -]{1,40})[’\x27]s\s+personal\s+(?:bank\s+)?account')
    if not account and personal_name:account=personal_name
    url=nearest(r'https?://[^\s<>]+')
    channel=None
    if re.search(r'\b(?:online\s+application|application\s+portal|payment\s+gateway|application/payment\s+gateway)\b',local,re.I):channel='CLAIMED_APPLICATION_GATEWAY'
    elif upi:channel='UPI'
    elif re.search(r'\b(?:bank transfer|wire transfer|NEFT|IMPS)\b',local,re.I):channel='BANK_TRANSFER'
    elif re.search(r'\b(?:gift card|cryptocurrency|bitcoin|usdt)\b',local,re.I):channel='GIFT_CARD_OR_CRYPTO'
    choices=[(min(abs(a+m.start()-start),abs(a+m.end()-end)),m,kind) for m,kind in [(upi,'upi'),(account,'account')] if m]
    chosen=min(choices,key=lambda x:x[0]) if choices else None
    recipient=(chosen[1].group() if chosen[2]=='upi' else chosen[1].group(1).strip()) if chosen else None
    refs=[]
    for m,kind in [(upi,'payment_recipient'),(account,'payment_recipient'),(personal,'payment_context'),(url,'payment_url')]:
        if m:refs.append(span(text,a+m.start(),a+m.end(),kind))
    return {'recipient':recipient,'channel':channel,'payment_url':url.group().rstrip(').,;') if url else None,
        'outside_application_flow':bool(personal),'destination_spans':refs,'scope_start':a,'scope_end':b}

def fee_exempt(text,start,end):
    a,b=sentence_bounds(text,start,end);before=text[a:start];after=text[end:b]
    return bool(re.search(r'\b(?:exempt(?:ed|ion)?|waiv(?:ed|er))\b',before[-130:],re.I)
        or re.match(r'\s*(?:is|are|:)??\s*(?:waived|not required|none|zero|₹\s*0\b|(?:Rs\.?|INR)\s*0\b)',after,re.I))

def enrich_amounts(text,entities):
    from app.scanners.payment_scanner import MONEY,PAYMENT_PURPOSE_REGEX
    liability=re.compile(r'\b(?:service[\s–—-]+agreement|service[\s–—-]+bond|breach|contractual\s+penalt(?:y|ies)|liquidated\s+damages|bond\s+(?:amount|liability))\b',re.I)
    reimbursement=re.compile(r'\b(?:reimburse(?:ment|d)?|reimbursable|travel\s+(?:expenses?|allowance))\b',re.I)
    for e in entities:
        a,b=sentence_bounds(text,e['start'],e['end']);local=text[a:b]
        # Generic fee/deposit wording inside an explicitly described application
        # flow is policy context; a labelled security/registration demand stays distinct.
        generic=e.get('label','') or ''
        policy_context=bool(re.search(r'\bapplication\b|\bpayment\s+gateway\b',local,re.I))
        if e['role']=='PAYMENT' and e['category']=='OTHER_PAYMENT' and policy_context:
            e['category']='APPLICATION_FEE'
        if e['role']=='AMBIGUOUS':
            page_start=text.rfind('--- Page ',0,e['start'])
            headings=list(re.finditer(r'\b(?:application\s+fees?|do\s+I\s+need\s+to\s+pay\s+application\s+fee)\b',text[max(0,page_start):e['start']],re.I))
            if headings:
                heading=max(0,page_start)+headings[-1].start();section=text[heading:e['start']]
                if len(section)<650 and not re.search(r'\b(?:salary|stipend|penalty|reimbursement|what are|how many)\b',section,re.I):
                    e.update(role='PAYMENT',category='APPLICATION_FEE')
        raw_distance=lambda m: min(abs(a+m.start()-e['start']),abs(a+m.end()-e['end']))
        liabilities=list(liability.finditer(local));refunds=list(reimbursement.finditer(local))
        fees=[m for m in re.finditer(PAYMENT_PURPOSE_REGEX,local,re.I) if not fee_exempt(text,a+m.start(),a+m.end())]
        nearest_fee=min([raw_distance(m) for m in fees]+[10000])
        rationale='Unique local amount/label relationship.' if e['role']!='AMBIGUOUS' else 'No unique amount/label relationship; amount purpose is unresolved.'
        if liabilities and min(raw_distance(m) for m in liabilities)<350 and min(raw_distance(m) for m in liabilities)<nearest_fee:
            upfront=bool(re.search(r'\b(?:pay|transfer|deposit)\b.{0,100}\b(?:before (?:the )?(?:interview|joining|offer)|now|immediately)\b',local,re.I|re.S))
            e.update(role='PAYMENT' if upfront else 'CONTRACTUAL_LIABILITY',category='CONTRACTUAL_PENALTY',period=None)
            rationale='Amount occurs in service-agreement/breach-liability context; no upfront recruitment payment is inferred.'
        elif refunds and min(raw_distance(m) for m in refunds)<120 and min(raw_distance(m) for m in refunds)<nearest_fee:
            e.update(role='REIMBURSEMENT',category='REIMBURSEMENT',period=None)
            rationale='Amount is described as reimbursement/expense allowance, not a payment demanded from the applicant.'
        e.update(classification_rationale=rationale,page=page_at(text,e['start']),verification_status='UNRESOLVED',
            supporting_text=text[a:b],support_start=a,support_end=b,amount_role='STATED_AMOUNT')
        if e['category']=='APPLICATION_FEE':
            if re.search(r'\b(?:including|inclusive of|inclusive)\s+(?:all\s+)?GST\b',text[e['end']:min(b,e['end']+70)],re.I):e['amount_role']='TAX_INCLUSIVE_TOTAL'
            if re.search(r'\bfor\s+all\s+(?:candidates|applicants|categories)\b',local,re.I):e['applicability']='ALL'
        e.update(destination(text,e['start'],e['end']))
    # Only explicit tax equations/total statements establish a related base/total.
    for base,total in zip(entities,entities[1:]):
        between=text[base['end']:total['start']]
        if base['currency']!=total['currency'] or len(between)>180 or '--- Page' in between:continue
        if not re.search(r'\bGST\b',between,re.I) or not re.search(r'\+|\binclud|=|\btotal\b|\bi[.]?e[.]?\b|\bamounting\b',between,re.I):continue
        if Decimal(total['value'])<=Decimal(base['value']):continue
        a=max(0,base['start']-130);local=text[a:total['end']+70]
        if not re.search(r'\b(?:application|examination|exam)\s+fee',local,re.I):continue
        relation=digest(base['currency']+':application_fee:'+base['value']+':'+total['value'])
        for e,role in [(base,'BASE_FEE'),(total,'TAX_INCLUSIVE_TOTAL')]:
            e.update(role='PAYMENT',category='APPLICATION_FEE',period=None,relation_group=relation,amount_role=role,
                classification_rationale='The submitted text explicitly relates this base fee and GST-inclusive total. This records a stated relationship, not independent validation of tax or payment authorization.',
                related_amount_spans=[span(text,base['start'],base['end'],'base_fee'),span(text,total['start'],total['end'],'tax_inclusive_total')])
    return entities

def payment_findings(text,entities):
    from app.scanners.payment_scanner import PAYMENT_PURPOSE_REGEX,UPI_HANDLE_REGEX,CRYPTO_REGEX,GIFT_CARD_REGEX,PAYMENT_LINK_REGEX,negated_payment_context,uncertain_payment_context
    payments=[e for e in entities if e['role']=='PAYMENT' and Decimal(e['value'])>0]
    compensation=[e for e in entities if e['role']=='COMPENSATION']
    groups={}
    relations={}
    for e in entities:
        if e.get('relation_group'):relations.setdefault((e['category'],e['currency'],e['value']),set()).add(e['relation_group'])
    for e in payments:
        aliases=relations.get((e['category'],e['currency'],e['value']),set())
        if len(aliases)==1:e['relation_group']=next(iter(aliases))
    def add(key,flag):
        if key not in groups:groups[key]=flag;groups[key]['fact_key']=key;groups[key]['occurrences']=1;return
        current=groups[key];current['occurrences']+=1
        current['source_spans']=list({(s['start'],s['end'],s.get('kind')):s for s in [*current['source_spans'],*flag['source_spans']]}.values())
        current['amounts']=list(dict.fromkeys([*current.get('amounts',[]),*flag.get('amounts',[])]))
    def flag_for(e):
        context=destination(text,e['start'],e['end']);app=e['category']=='APPLICATION_FEE'
        uncertain=uncertain_payment_context(text,e.get('label_start') if e.get('label_start') is not None else e['start'])
        external=context['outside_application_flow'] or context['channel']=='GIFT_CARD_OR_CRYPTO'
        sev='critical' if external or (not app and not uncertain) else 'moderate'
        key='payment:'+e['category']+':'+e.get('relation_group',e['currency']+':'+e['value'])+':'+str(context['recipient'])+':'+str(context['channel'])
        spans=[span(text,e['start'],e['end'],'payment_amount'),span(text,e['support_start'],e['support_end'],'payment_context'),*e.get('related_amount_spans',[]),*context['destination_spans']]
        if e.get('label_start') is not None:spans.append(span(text,e['label_start'],e['label_end'],'payment_label'))
        message=('Application fee policy observed; amount/payment authorization remain unresolved: ' if app and not external else 'Payment request identified ('+e['category'].lower().replace('_',' ')+'): ')+e['raw']+'.'
        return key,{'code':'APPLICATION_FEE_UNRESOLVED' if app and not external else 'OUTSIDE_FLOW_PAYMENT' if external else 'UPFRONT_PAYMENT_REQUEST',
            'severity':sev,'message':message,'detail':e['classification_rationale']+' Recipient and channel are submitted claims, not proof of authorization. Verify this exact advertisement, fee and destination independently.',
            'observed_value':e['raw'],'source_spans':spans,'amounts':[e['raw']],
            'payment_context':{k:context[k] for k in ['recipient','channel','payment_url','outside_application_flow']}}
    for e in payments:
        key,flag=flag_for(e);add(key,flag)
    purposes=[]
    for m in re.finditer(PAYMENT_PURPOSE_REGEX,text,re.I):
        if negated_payment_context(text,m.start()) or fee_exempt(text,m.start(),m.end()):continue
        a,b=sentence_bounds(text,m.start(),m.end())
        if re.search(r'\b(?:breach|service[ -]agreement|contractual\s+penalty)\b',text[a:b],re.I):continue
        purposes.append(m)
        if any(e['support_start']<=m.start()<e['support_end'] for e in payments):continue
        app=bool(re.search(r'\b(?:application|exam)\b',m.group(),re.I)) or (m.group().lower() in {'fee','fees','deposit'} and bool(re.search(r'\bapplication\b|payment\s+gateway',text[a:b],re.I)))
        category='APPLICATION_FEE' if app else 'UNPRICED_'+re.sub(r'\W+','_',m.group().upper())
        ctx=destination(text,m.start(),m.end())
        # A repeated unpriced application-policy mention supports the single
        # priced policy only when recipient/channel are compatible and unique.
        compatible=[k for k,f in groups.items() if k.startswith('payment:'+category+':') and
            (not ctx['recipient'] or ctx['recipient']==f['payment_context']['recipient']) and ctx['outside_application_flow']==f['payment_context']['outside_application_flow']]
        if len(compatible)==1:
            flag={**groups[compatible[0]],'source_spans':[span(text,m.start(),m.end(),'payment_label')],'amounts':[]};add(compatible[0],flag);continue
        sev='critical' if ctx['outside_application_flow'] else 'moderate' if app or uncertain_payment_context(text,m.start()) else 'critical'
        key='payment:'+category+':unpriced:'+str(ctx['recipient'])+':'+str(ctx['channel'])
        add(key,{'code':'APPLICATION_FEE_UNRESOLVED' if app else 'UNPRICED_PAYMENT_REQUEST','severity':sev,
            'message':f"{'Application fee policy' if app else 'Payment requirement'} mentioned ({m.group()}); amount not unambiguously linked.",
            'detail':'No amount is inferred. Payment purpose, recipient and authorization remain unresolved.','observed_value':m.group(),
            'source_spans':[span(text,m.start(),m.end(),'payment_label')],'payment_context':ctx,'amounts':[]})
    methods=[]
    for pattern,method in [(UPI_HANDLE_REGEX,'UPI'),(CRYPTO_REGEX,'Cryptocurrency'),(GIFT_CARD_REGEX,'Gift Cards'),(PAYMENT_LINK_REGEX,'Payment Link')]:
        for match in re.finditer(pattern,text,re.I):
            methods.append(method)
            # Identifiers already captured by a contextual payment finding are
            # supporting references, not another independent finding.
            if any(any(s['start']<=match.start()<s['end'] for s in f['source_spans']) for f in groups.values()):continue
            add('payment_identifier:'+method+':'+match.group().casefold(),{'code':'PAYMENT_IDENTIFIER_OBSERVED','severity':'moderate',
                'message':f'{method} payment identifier observed: {match.group()}.','detail':'Identifier alone is not a payment demand or proof of fraud.',
                'observed_value':match.group(),'source_spans':[span(text,match.start(),match.end(),'payment_identifier')],'amounts':[]})
    raw_values={e['raw']:(e['currency'],Decimal(e['value'])) for e in entities}
    for flag in groups.values():
        unique={}
        for raw in flag.get('amounts',[]):unique.setdefault(raw_values.get(raw,raw),raw)
        flag['amounts']=list(unique.values())
        if len(flag['amounts'])>1:flag['message']='Application fee policy observed; related stated base/total amounts: '+', '.join(flag['amounts'])+'. Payment authorization remains unresolved.'
    return {'payment_detected':bool(groups),'flags':list(groups.values()),'monetary_entities':entities,'amounts_detected':entities,
        'payment_amounts':payments,'compensation_amounts':compensation,'detected_amounts':list(dict.fromkeys(e['value'] for e in payments)),
        'amounts_detected_legacy':entities,'purposes_found':list(dict.fromkeys(m.group() for m in purposes)),
        'detected_methods':list(dict.fromkeys(methods)),'upi_handles':list(dict.fromkeys(re.findall(UPI_HANDLE_REGEX,text,re.I))),
        'ambiguous_amounts':[e for e in entities if e['role']=='AMBIGUOUS'],
        'liability_amounts':[e for e in entities if e['role']=='CONTRACTUAL_LIABILITY'],
        'reimbursements':[e for e in entities if e['role']=='REIMBURSEMENT'],
        'elevated_payment_concern':any(f['severity'] in {'high','critical'} for f in groups.values()),
        'critical_nuance':'An unverified fee remains unresolved. Contractual liabilities and reimbursements are not upfront fees.'}
