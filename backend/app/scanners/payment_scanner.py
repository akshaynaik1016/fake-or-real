"""Deterministic monetary spans. Never infer a fee from an unrelated salary."""
import re
from decimal import Decimal
from typing import Any

NUMBER = r"(?:\d{1,3}(?:,\d{2})*,\d{3}|\d{1,3}(?:,\d{3})+|\d+)(?:\.\d{1,2})?"
CURRENCY_AMOUNT_REGEX = rf"(?P<currency>₹|\$|€|£|(?:(?<!\w)|(?<=for))(?:INR|Rs\.?|USD|EUR|GBP))\s*(?P<number>{NUMBER})(?![\d,])"
MONEY = re.compile(CURRENCY_AMOUNT_REGEX, re.I)
PAYMENT_PURPOSE_REGEX = r"\b(?:(?:refundable\s+)?(?:registration|processing|training|application|exam|interview|certificate|onboarding|laptop|courier|badge)\s*(?:fees?|charges?|deposit|cost)|(?:refundable\s+)?security\s+deposit|refundable\s+(?:deposit|fee|payment)|(?:registration|processing|training)\s+charges?|fees?|deposit)\b"
UPI_HANDLE_REGEX = r"(?<![\w.-])[\w.-]{2,256}@(?:okaxis|okhdfcbank|oksbi|paytm|ybl|ibl|apl|axl|upi)(?![\w-]|\.[\w-])"
CRYPTO_REGEX = r"\b(0x[a-fA-F0-9]{40}|[13][a-km-zA-HJ-NP-Z1-9]{25,34}|T[A-Za-z1-9]{33})\b"
GIFT_CARD_REGEX = r"\b(amazon\s+pay\s+gift\s+card|google\s+play\s+recharge|apple\s+gift\s+card|steam\s+wallet)\b"
PAYMENT_LINK_REGEX = r"\b(?:razorpay\.me|cashfree|instamojo|paytm\.me|phonepe\.me)\S*"
COMPENSATION = re.compile(r"\b(stipend|salar(?:y|ies)|scholarships?|compensation|remuneration|wages?|bonus|allowance|grant|award|earnings?|payout)\b", re.I)
DEMAND = re.compile(r"\b(pay|deposit|transfer|remit|send\s+money)\b", re.I)


def negated_payment_context(text: str, start: int) -> bool:
    segment=text[max(0,start-120):start]
    # Preserve negation across a comma-delimited PDF/OCR list, while ordinary
    # line/sentence boundaries and a new payment verb still reset its scope.
    segment=re.sub(r',\s*\n\s*',', ',segment)
    prefix = re.split(r"[\n!?;]|(?<!Rs)\.(?!\d)|\b(?:but|however|instead)\b", segment, flags=re.I)[-1]
    negatives = list(re.finditer(r"\b(no|not|without|zero|never|do\s+not|don't)\b", prefix, re.I))
    return bool(negatives) and not re.search(r"\b(pay|transfer|send|remit|mandatory)\b", prefix[negatives[-1].end():], re.I)


def uncertain_payment_context(text: str,start: int) -> bool:
    before=re.split(r'[.!;\n]',text[:start])[-1]
    after=re.split(r'[.!;\n]',text[start:])[0]
    clause=before+after
    return bool(re.search(r'\b(?:stipend|salary)\b.*\bor\b.*\b(?:fee|deposit)\b|\b(?:fee|deposit)\b.*\bor\b.*\b(?:stipend|salary)\b',clause,re.I)
        or '?' in clause or re.search(r'\b(?:may|might|hypothetical|example|suppose|if)\b',before,re.I))


def _clauses(text: str):
    """Sentence/clause boundaries, preserving Rs. and monetary decimals/commas."""
    protected = {i for m in MONEY.finditer(text) for i in range(m.start(), m.end())}
    separators = re.compile(r"[\n;!?]|\.(?=\s|$)|,(?!\d)|\b(?:but|while|whereas|however)\b|\band\b(?=\s+(?:(?:a|the|your)\s+)?(?:pay\b|salary\b|stipend\b|registration\b|security\b|processing\b|training\b|scholarship\b|bonus\b|fee\b))", re.I)
    start = 0
    for match in separators.finditer(text):
        if match.start() in protected or (match.group() == '.' and re.search(r"\bRs\.$", text[:match.end()], re.I)):
            continue
        if text[start:match.start()].strip():
            yield start, match.start()
        start = match.end()
    if text[start:].strip():
        yield start, len(text)


def _category(label: str, role: str) -> str:
    label = label.lower()
    if role == 'COMPENSATION':
        if 'stipend' in label: return 'STIPEND'
        if 'salar' in label or 'wage' in label: return 'SALARY'
        if 'scholarship' in label: return 'SCHOLARSHIP'
        return 'OTHER_COMPENSATION'
    if re.search(r'refundable\s+(?:fee|payment)',label):return 'REFUNDABLE_PAYMENT'
    for word, category in [('application','APPLICATION_FEE'), ('exam','APPLICATION_FEE'), ('registration', 'REGISTRATION_FEE'), ('security', 'SECURITY_DEPOSIT'),
                           ('processing', 'PROCESSING_FEE'), ('training', 'TRAINING_FEE'),
                           ('refundable', 'REFUNDABLE_DEPOSIT')]:
        if word in label: return category
    return 'OTHER_PAYMENT'


def _extract_monetary_entities_base(text: str) -> list[dict[str, Any]]:
    entities = []
    for start, end in _clauses(text):
        clause = text[start:end]
        amounts = list(MONEY.finditer(clause))
        if not amounts:
            continue
        cues = []
        for pattern, role in [(re.compile(PAYMENT_PURPOSE_REGEX, re.I), 'PAYMENT'), (COMPENSATION, 'COMPENSATION')]:
            for m in pattern.finditer(clause):
                negated = role == 'PAYMENT' and (negated_payment_context(clause, m.start()) or bool(re.match(
                    r"\s*(?:is|are|:)?\s*(?:waived|not required|none|zero|₹\s*0\b|(?:Rs\.?|INR)\s*0\b)", clause[m.end():], re.I)))
                cues.append({'start': m.start(), 'end': m.end(), 'text': m.group(), 'role': 'NEGATED' if negated else role})
        # An explicit payment verb is a fallback only when there is no fee label.
        if not any(c['role'] in {'PAYMENT', 'NEGATED'} for c in cues):
            for m in DEMAND.finditer(clause):
                if not negated_payment_context(clause, m.start()):
                    cues.append({'start': m.start(), 'end': m.end(), 'text': m.group(), 'role': 'PAYMENT'})
        # Adjacent cue/amount tokens form a small bipartite graph. Maximizing
        # supported links before considering distance avoids stealing a nearby
        # fee label from the next amount when a salary label precedes this one.
        tokens=sorted([(m.start(),m.end(),'amount',i) for i,m in enumerate(amounts)]+
                      [(c['start'],c['end'],'cue',i) for i,c in enumerate(cues)])
        adjacency={i:[] for i in range(len(amounts))}
        for left,right in zip(tokens,tokens[1:]):
            if left[2]==right[2] or right[0]-left[1]>70:
                continue
            ai=left[3] if left[2]=='amount' else right[3]
            ci=left[3] if left[2]=='cue' else right[3]
            adjacency[ai].append(ci)
        def matching(forbidden=None):
            owners={}
            def augment(ai,seen):
                for ci in adjacency[ai]:
                    if (ai,ci)==forbidden or ci in seen: continue
                    seen.add(ci)
                    if ci not in owners or augment(owners[ci],seen):
                        owners[ci]=ai
                        return True
                return False
            for ai in adjacency: augment(ai,set())
            return {ai:ci for ci,ai in owners.items()}
        assigned={}
        shared_single_cue=len(amounts)>1 and len(cues)==1
        bare_alternative=any(re.match(r'\s*(?:or|to|[-–])\s*\d',clause[m.end():],re.I) for m in amounts)
        conflicting_alternative=len({c['role'] for c in cues})>1 and bool(re.search(r"\bor\b",clause,re.I))
        # Bound matching complexity on adversarial long unpunctuated input.
        if len(amounts)<=64 and not shared_single_cue and not bare_alternative and not conflicting_alternative:
            best=matching()
            for ai,ci in best.items():
                # Only links required by every maximum matching are asserted.
                # A single label for a range/list has no forced link.
                if len(matching((ai,ci)))<len(best):
                    assigned[ai]=cues[ci]
        for ai, amount in enumerate(amounts):
            cue = assigned.get(ai)
            role = cue['role'] if cue else 'AMBIGUOUS'
            category = _category(cue['text'], role) if cue and role != 'NEGATED' else role
            currency = amount.group('currency').upper().rstrip('.')
            currency = 'INR' if currency in {'₹', 'RS', 'INR'} else {'$':'USD','€':'EUR','£':'GBP'}.get(currency, currency)
            # Period only describes compensation; never reinterpret a fee as salary.
            period = None
            if role == 'COMPENSATION':
                next_bound=min([len(clause)]+[c['start'] for c in cues if c['start']>=amount.end()]+[m.start() for m in amounts if m.start()>=amount.end()])
                period_context=clause[amount.end():next_bound]
                period_pattern =r"(?:per\s+|/\s*)(month|week|day|year|annum)\b|\b(monthly|weekly|daily|yearly|annually)\b"
                period_match=re.search(period_pattern,period_context,re.I)
                if not period_match:
                    previous_bound=max([0]+[m.end() for m in amounts if m.end()<=amount.start()])
                    period_match=re.search(period_pattern,clause[max(previous_bound,amount.start()-30):amount.start()],re.I)
                if period_match:
                    raw = (period_match.group(1) or period_match.group(2)).lower()
                    period = {'monthly':'month','weekly':'week','daily':'day','yearly':'year','annually':'year','annum':'year'}.get(raw,raw)
            value = str(Decimal(amount.group('number').replace(',', '')))
            context_start=max(0,amount.start()-120); context_end=min(len(clause),amount.end()+120)
            entities.append({'raw': amount.group(), 'value': value, 'currency': currency,
                'role': role, 'category': category, 'period': period,
                'start': start+amount.start(), 'end': start+amount.end(),
                'context_start': start+context_start, 'context_end': start+context_end, 'context': clause[context_start:context_end],
                'label': cue['text'] if cue else None,
                'label_start': start+cue['start'] if cue else None,
                'label_end': start+cue['end'] if cue else None,
                'ambiguity_reason': None if cue else 'No unique monetary label in this sentence or clause'})
    return entities


def extract_monetary_entities(text: str) -> list[dict[str, Any]]:
    from app.scanners.payment_context import enrich_amounts
    return enrich_amounts(text,_extract_monetary_entities_base(text))


def analyze_payment_risk(text: str) -> dict[str, Any]:
    from app.scanners.payment_context import payment_findings
    entities=extract_monetary_entities(text or '')
    return payment_findings(text or '',entities)


def scan_payment_risks(text: str) -> dict[str, Any]:
    return analyze_payment_risk(text)
