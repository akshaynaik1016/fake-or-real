"""Deterministic notice fields. Labels and excerpts, not invented recruitment facts."""
import re
from datetime import datetime

DATE=r'(?:\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\s+\d{4}|\d{4}-\d{2}-\d{2}|\d{1,2}[./-]\d{1,2}[./-]\d{4})'

def date_value(raw):
    raw=re.sub(r'\s+',' ',raw).strip()
    for fmt in ['%d %B %Y','%d %b %Y','%Y-%m-%d']:
        try:return datetime.strptime(raw,fmt).date().isoformat()
        except ValueError:pass
    m=re.fullmatch(r'(\d{1,2})[./-](\d{1,2})[./-](\d{4})',raw)
    if m and int(m[1])>12:
        try:return datetime(int(m[3]),int(m[2]),int(m[1])).date().isoformat()
        except ValueError:pass
    return raw # Ambiguous/invalid numeric dates stay literal.

def recruitment_fields(text):
    fields=[]
    def add(kind,value,start,end,method='labelled_recruitment_field'):
        fields.append((kind,value,start,end,method))
    for m in re.finditer(r'\b(?:advertisement|advt\.?|adv\.?|reference)\s*(?:number|no\.?|#)\s*[:.-]?\s*([A-Za-z0-9]+(?:\s*[/_-]\s*[A-Za-z0-9]+){1,10})',text,re.I):
        add('advertisement_number',re.sub(r'\s+','',m.group(1)).upper(),m.start(1),m.end(1))
    for kind,label in [('publication_date',r'(?:advertisement|publication|published|notification|advt\.?)\s*(?:date|dated|on)?'),
        ('application_start',r'(?:application\s+(?:start|opening)(?:\s+date)?|opening\s+date(?:\s+of\s+(?:online\s+)?applications?)?|online\s+applications?\s+(?:start|open)(?:s|ing)?(?:\s+(?:on|from))?)'),
        ('application_deadline',r'(?:last\s+date\s+for\s+applying\s+online(?:\s+is)?|application\s+(?:deadline|closing\s+date|last\s+date)|closing\s+date(?:\s+of\s+(?:online\s+)?applications?)?|last\s+date(?:\s+(?:for|of)\s+(?:(?:submission|receipt)\s+of\s+)?(?:online\s+)?applications?)?)')]:
        for m in re.finditer(r'\b'+label+r'\s*[:.-]?\s*('+DATE+r')',text,re.I):
            if kind=='publication_date' and re.search(r'\b(?:internal|previous|earlier|other)\s*$',text[max(0,m.start()-30):m.start()],re.I):continue
            add(kind,date_value(m.group(1)),m.start(1),m.end(1),'labelled_date_parser')
    # A generic Date label is a notice header date only adjacent to an explicit
    # advertisement identifier, not a candidate DOB or unrelated internal notice.
    ad_positions=[f[2] for f in fields if f[0]=='advertisement_number']
    for m in re.finditer(r'\bDate\s*:\s*('+DATE+r')',text,re.I):
        if any(0<m.start()-position<200 for position in ad_positions):add('publication_date',date_value(m.group(1)),m.start(1),m.end(1),'advertisement_header_date')
    for page in re.finditer(r'(?:^|--- Page \d+ ---)(.*?)(?=--- Page \d+ ---|\Z)',text,re.S):
        body=page.group(1)
        if re.search(r'Name\s+of\s+Post',body,re.I) and re.search(r'No[.]?\s*(?:of\s*)?Posts',body,re.I):
            total=re.search(r'(?im)^\s*Total\s+(\d{1,5})(?:[ \t]+\d+){0,5}[ \t]*$',body)
            if total:add('vacancies',int(total.group(1)),page.start(1)+total.start(1),page.start(1)+total.end(1),'labelled_vacancy_table_total')
            for q in re.finditer(r'B[.]?E\s*/\s*B[.]?Tech\s*/\s*B[.]?Sc\s*\(\s*4\s*Years\s*\)\s*Engineering\s+Graduate\s+in\s+[A-Za-z/&(). \n-]{3,250}',body,re.I):
                add('eligibility',re.sub(r'\s+',' ',q.group()).strip(),page.start(1)+q.start(),page.start(1)+q.end(),'observed_qualification_table')
    for m in re.finditer(r'\b(?:total\s+)?(?:vacancies|number\s+of\s+vacancies|no\.?\s+of\s+(?:vacancies|posts))\s*[:=-]?\s*(\d{1,5})\b',text,re.I):
        add('vacancies',int(m.group(1)),m.start(1),m.end(1))
    for m in re.finditer(r'(?im)^[ \t]*(?:job\s+title|name\s+of\s+(?:the\s+)?post|post(?:\s+name)?|position)\s*:\s*([^\n.;]{2,150})',text):
        add('job_title',re.sub(r'\s+',' ',m.group(1)).strip(),m.start(1),m.end(1))
    # A distinctive role in running text is observed, without assuming a grade or discipline.
    if not any(f[0]=='job_title' for f in fields):
        for m in re.finditer(r'\bProbationary\s+Engineer(?:s)?\b',text,re.I):
            add('job_title','Probationary Engineer',m.start(),m.end(),'observed_recruitment_role')
    for m in re.finditer(r'(?im)^[ \t]*(?:eligibility|educational\s+qualifications?|qualification)\s*:\s*([^\n]{3,600})',text):
        add('eligibility',m.group(1).strip(),m.start(1),m.end(1))
    from app.scanners.payment_context import sentence_bounds
    for m in re.finditer(r'\b(?:exempt(?:ed|ion)?|waiv(?:ed|er))\b',text,re.I):
        left,right=sentence_bounds(text,m.start(),m.end());left=max(left,m.start()-220);right=min(right,m.end()+180)
        excerpt=text[left:right]
        if re.search(r'\b(?:fee|payment|SC|ST|PwBD|PwD|category|categories|candidate)\b',excerpt,re.I):
            add('fee_exemption',excerpt.strip(),left,right,'observed_exemption_statement')
    for m in re.finditer(r'(?im)\b(?:official\s+website|company\s+website|website)\s*(?:claimed|is|:)??\s*:?\s*((?:https?://|www\.)[^\s<>]+)',text):
        value=m.group(1).rstrip(').,;');add('official_website',value,m.start(1),m.start(1)+len(value))
    patterns=[('CLAIMED_APPLICATION_GATEWAY',r'\b(?:online\s+application(?:/payment)?\s+(?:payment\s+)?gateway|application/payment\s+gateway|payment\s+gateway|application\s+portal)\b'),
        ('BANK_TRANSFER',r'\b(?:bank\s+transfer|NEFT|IMPS|wire\s+transfer)\b'),('PERSONAL_ACCOUNT',r'\b(?:personal|my|recruiter[’\x27]?s?)\s+(?:bank\s+)?account\b'),('UPI',r'\bUPI\b')]
    for channel,pattern in patterns:
        for m in re.finditer(pattern,text,re.I):add('payment_channel',channel,m.start(),m.end(),'observed_payment_instruction')
    for m in re.finditer(r'\b(?:account(?:\s+(?:number|no\.?))?|beneficiary|payee|recipient|payable\s+to|in\s+favou?r\s+of)\s*[:#-]\s*([^\n.;]{2,90})',text,re.I):
        add('payment_destination',m.group(1).strip(),m.start(1),m.end(1),'observed_payment_destination')
    for m in re.finditer(r'(?<![\w.-])[\w.-]{2,256}@(?:okaxis|okhdfcbank|oksbi|paytm|ybl|ibl|apl|axl|upi)(?![\w.-])',text,re.I):
        add('payment_destination',m.group().lower(),m.start(),m.end(),'observed_upi_destination')
    for m in re.finditer(r'(?im)^\s*(?:\d+[.]\s*)?((?:SC|ST|PwBD|ESM|EWS|OBC|General|UR)(?:\s*[/,&]\s*(?:SC|ST|PwBD|ESM|EWS|OBC|General|UR))*)\s*[-:]\s*No\s+application\s+fee[^\n]*',text):
        add('fee_exemption',m.group().strip(),m.start(),m.end(),'scoped_category_fee_exemption')
    for m in re.finditer(r'Candidates\s+belonging\s+to\s+([^\n.]{1,80})\s+category\s+are\s+required\s+to\s+pay\s+an?\s+application\s+fee',text,re.I):
        add('fee_applicability',{'categories':re.findall(r'\b(?:GEN|General|UR|EWS|OBC|SC|ST|PwBD|ESM)\b',m.group(1),re.I),'policy':'PAYMENT_REQUIRED'},m.start(),m.end(),'observed_category_fee_rule')
    for m in re.finditer(r'(?im)^\s*\d+[.]\s*(GEN|General|UR|EWS|OBC\s*\(NCL\))\s*[-:]\s*Yes[- ]*for\s*Rs[.]?\s*\d[^\n]*',text):
        prefix=text[max(0,m.start()-600):m.start()]
        if re.search(r'\b(?:pay\s+application\s+fee|application\s+fee\s*[?])',prefix,re.I):
            add('fee_applicability',{'categories':[m.group(1)],'policy':'PAYMENT_REQUIRED'},m.start(),m.end(),'scoped_fee_faq_row')
    return fields
