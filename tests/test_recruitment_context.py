import asyncio,io
from pathlib import Path
from copy import deepcopy
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.services.case_claims import extract_claims
from app.scanners.payment_scanner import analyze_payment_risk
from app.scanners.sensitive_data_scanner import analyze_sensitive_data_requests
from app.services.notice_verification import compare_notice,notice_evidence
from app.services.bayesian_evidence_engine import fuse_evidence
from app.schemas.investigation import ResearchResult,ResearchSource

client=TestClient(app)
TEXT=Path(__file__).with_name('fixtures').joinpath('bel_context_synthetic.txt').read_text()

def post(text):
    r=client.post('/api/analyze/text',json={'input_type':'text','content':text});assert r.status_code==200,r.text;return r.json()
def create_case():return client.post('/api/cases',json={'title':'Synthetic recruitment context regression'}).json()
def add(case,text):
    r=client.post('/api/cases/'+case['case_id']+'/sources',json={'input_type':'text','content':text,'expected_revision':case['revision']});assert r.status_code==200,r.text;return r.json()
def pdf(pages=16):
    from reportlab.pdfgen.canvas import Canvas
    buffer=io.BytesIO();canvas=Canvas(buffer)
    for page in range(pages):
        text=canvas.beginText(35,800);text.setFont('Helvetica',9)
        for line in TEXT.splitlines():text.textLine(line)
        canvas.drawText(text);canvas.showPage()
    canvas.save();return buffer.getvalue()

def test_a_pdf_repeated_policy_is_one_unresolved_finding():
    response=client.post('/api/analyze/pdf',files={'file':('Vacancy for BE In BEL - SYNTHETIC.pdf',pdf(),'application/pdf')})
    assert response.status_code==200,response.text
    scan=response.json();state=scan['investigation']
    assert scan['risk_level']=='UNDETERMINED' and scan['trust_score'] is None
    payments=[e for e in state['evidence'] if e['category']=='payment_risk']
    assert len(payments)==1 and payments[0]['severity']=='moderate'
    assert not any(e['severity']=='critical' for e in state['evidence'])
    assert {s['page'] for s in payments[0]['source_spans'] if s.get('page')}==set(range(1,17))
    assert state['assessment']['offer_authenticity']=='UNRESOLVED'
    assert state['claimed_organization']=='Bharat Electronics Limited'
    assert all(scan['input_content'][s['start']:s['end']]==s['text'] for s in payments[0]['source_spans'])

@pytest.mark.parametrize('currency',['₹','Rs. ','INR '])
def test_b_tax_amounts_related_only_when_explicit(currency):
    r=analyze_payment_risk(f'Application fee {currency}1,000 + GST = {currency}1,180. Pay through the application gateway.')
    amounts=r['monetary_entities']
    assert [e['category'] for e in amounts]==['APPLICATION_FEE','APPLICATION_FEE']
    assert [e['amount_role'] for e in amounts]==['BASE_FEE','TAX_INCLUSIVE_TOTAL']
    assert amounts[0]['relation_group']==amounts[1]['relation_group']
    assert len(r['flags'])==1 and r['flags'][0]['severity']=='moderate'
    unlinked=analyze_payment_risk(f'Application fee {currency}1,000. Another amount {currency}1,180.')
    assert not any(e.get('relation_group') for e in unlinked['monetary_entities'])

@pytest.mark.parametrize('text',[
    'If the employee breaches the service agreement, pay INR 2,00,000 as contractual penalty.',
    'Service-agreement breach liability is ₹2,00,000.',
    'Liquidated damages of Rs. 2,00,000 apply on breach of the service agreement.',
])
def test_c_contractual_penalty_is_not_upfront_fee(text):
    result=analyze_payment_risk(text)
    assert len(result['liability_amounts'])==1 and not result['payment_amounts']
    assert not result['elevated_payment_concern']
    claims=extract_claims('source',text,'text')
    assert any(c['claim_type']=='contractual_penalty' and c['value']['value']=='200000' for c in claims)
    assert not any(c['claim_type']=='fee' for c in claims)

@pytest.mark.parametrize('text',[
    'Create a password to access your application account.',
    'Log in using your password.',
    'The system will send account credentials to your registered email.',
    'Your account credentials will be sent to your registered email.',
    'Enter your password to log in to the application account.',
])
def test_d_normal_account_instructions_are_not_theft(text):
    result=analyze_sensitive_data_requests(text)
    assert not result['has_critical'] and not result['flags']
    assert result['account_instructions']
    assert post(text)['risk_level']=='UNDETERMINED'

@pytest.mark.parametrize('text',[
    'Send your password or OTP to this recruiter.',
    'Share your login password with me.',
    'Create a password, then send it to the recruiter.',
    'Log in to the application portal. Now forward your credentials to the recruiter.',
])
def test_e_outward_credentials_are_still_critical(text):
    assert analyze_sensitive_data_requests(text)['has_critical']
    scan=post(text)
    assert scan['risk_level']=='ELEVATED CONCERN'
    assert len([e for e in scan['evidence'] if e['category']=='sensitive_data_request'])==1

@pytest.mark.parametrize('text',[
    'Pay application fee INR 1180 to my personal account: ALICE123.',
    'Transfer the application fee to the recruiter personal account.',
    'Pay contractual penalty INR 200000 before the interview to my personal account.',
])
def test_e_personal_or_upfront_destination_is_concerning(text):
    assert post(text)['risk_level']=='ELEVATED CONCERN'

def test_distinct_payment_recipients_are_not_merged():
    result=analyze_payment_risk('Pay registration fee INR 999 to personal account: ALICE123; Pay registration fee INR 999 to personal account: BOB456.')
    assert len(result['flags'])==2
    assert {f['payment_context']['recipient'] for f in result['flags']}=={'ALICE123','BOB456'}

def test_f_company_reference_is_not_offer_verification():
    scan=post(TEXT+'\nOfficial website: https://bel-india.in')
    assert scan['assessment']['offer_authenticity']=='UNRESOLVED'
    assert scan['assessment']['verification_status']=='UNRESOLVED'
    assert not scan['assessment']['verified_claims']
    assert scan['risk_level']=='UNDETERMINED'

def test_g_empty_search_does_not_verify_anything(monkeypatch):
    from app.integrations.web_research.tavily_service import TavilyService
    monkeypatch.setattr(settings,'TAVILY_API_KEY','test-only')
    monkeypatch.setattr(settings,'CASE_URL_FETCH_ENABLED',True)
    async def empty(*args,**kwargs):return ResearchResult(status='COMPLETED',sources=[],reason='Synthetic empty result')
    monkeypatch.setattr(TavilyService,'search',empty)
    case=add(create_case(),TEXT)
    response=client.post(f"/api/cases/{case['case_id']}/actions/verify_notice",json={'expected_revision':case['revision']})
    assert response.status_code==200,response.text
    updated=response.json()
    assert updated['last_action']['status']=='COMPLETED' and 'unresolved' in updated['last_action']['message']
    assert not updated['assessment']['verified_claims']
    assert all(c['status']=='UNRESOLVED' for c in updated['notice_review']['claim_results'])
    assert updated['fusion']['risk_score'] is None

def test_h_paraphrased_copies_share_one_payment_fact_and_weight():
    first=add(create_case(),'Company: AEXON TECH\nPay registration fee INR 999.')
    second=add(first,'Company: AEXON TECH\nPlease pay the registration fee of INR 999.')
    payments=[e for e in second['evidence'] if e['category']=='payment_risk']
    assert len(payments)==1 and len(payments[0]['source_ids'])==2
    assert len({r['source_id'] for r in payments[0]['citations']})==2
    assert second['fusion']['risk_score']==first['fusion']['risk_score']
    assert second['fusion']['confidence']==first['fusion']['confidence']

def document(text):
    return {'id':'independent-doc','title':'Synthetic independently retrieved test notice','url':'https://bel-india.in/example.pdf','text':text,
        'retrieval_method':'PINNED_HTTPS_FULL_DOCUMENT','retrieved_at':'2026-11-01T00:00:00+00:00','claims':[],
        'extracted_information':text[:1000]}

def test_exact_notice_claim_corroboration_not_whole_file_authentication():
    claims=extract_claims('submitted',TEXT,'text')
    review=compare_notice(claims,[{'notice_verification':True,'independent_documents':[document(TEXT)]}])
    assert review['independent_documents']
    assert any(c['status']=='INDEPENDENTLY_CORROBORATED' and c['claim_type']=='vacancies' for c in review['claim_results'])
    assert review['offer_authenticity']=='UNRESOLVED'
    assert all(len(c['citations'])>=2 for c in review['claim_results'] if c['status']=='INDEPENDENTLY_CORROBORATED')

@pytest.mark.parametrize('changed',[
    TEXT.replace('17556/HR/All-India/2026','OTHER/HR/2026'),
    TEXT.replace('Probationary Engineer','Senior Engineer'),
    'Bharat Electronics Limited is a company. See our careers page.',
])
def test_general_or_different_notices_never_corroborate(changed):
    claims=extract_claims('submitted',TEXT,'text')
    review=compare_notice(claims,[{'notice_verification':True,'independent_documents':[document(changed)]}])
    assert not review['independent_documents']
    assert not any(c['status']!='UNRESOLVED' for c in review['claim_results'])

@pytest.mark.parametrize('url',['https://bel-india.in.attacker.example/ad','http://bel-india.in/ad','https://user@bel-india.in/ad'])
def test_untrusted_document_origin_cannot_verify(url):
    d={**document(TEXT),'url':url}
    review=compare_notice(extract_claims('submitted',TEXT,'text'),[{'notice_verification':True,'independent_documents':[d]}])
    assert not review['independent_documents']

def test_independent_contradiction_outweighs_repeated_keywords():
    claims=extract_claims('submitted',TEXT,'text')
    remote=TEXT.replace('vacancies: 350','vacancies: 351')
    review=compare_notice(claims,[{'notice_verification':True,'independent_documents':[document(remote)]}])
    contradictions=[e for e in notice_evidence(review) if e['category']=='notice_contradiction']
    assert len(contradictions)==1 and contradictions[0]['severity']=='critical'
    first=fuse_evidence(contradictions,[])
    assert first['risk_score'] is not None
    repeated=fuse_evidence(contradictions*30,[])
    assert repeated['risk_score']==first['risk_score'] and repeated['confidence']==first['confidence']

def test_all_recruitment_fields_keep_exact_provenance():
    text=TEXT+'\nOfficial website: https://bel-india.in\nRecipient: BEL Recruitment\nContact number: +91 12345 67890'
    claims=extract_claims('source',text,'pdf')
    kinds={c['claim_type'] for c in claims}
    assert kinds>={'organization','advertisement_number','publication_date','job_title','vacancies','application_deadline','eligibility','fee','fee_exemption','fee_relation','payment_channel','payment_destination','account_instruction','contractual_penalty','official_website','contact_number'}
    assert all(c['excerpt']==text[c['location']['start']:c['location']['end']] for c in claims)
    assert all(c['verification_status']=='CLAIMED' for c in claims)

def test_reimbursement_is_not_a_fee():
    r=analyze_payment_risk('Travel reimbursement of INR 1500 will be paid by the employer.')
    assert [e['value'] for e in r['reimbursements']]==['1500'] and not r['payment_amounts']

def test_bad_pdf_has_extraction_error_not_scanner_findings():
    response=client.post('/api/analyze/pdf',files={'file':('broken.pdf',b'%PDF-1.4\ninvalid','application/pdf')})
    assert response.status_code==422 and response.json()['detail']['stage']=='pdf_extraction'


def mock_notice_transport(monkeypatch,remote=TEXT):
    from app.integrations.web_research.tavily_service import TavilyService
    from app.services import case_url_fetcher
    from app.documents.pdf_analyzer import analyze_pdf_document
    monkeypatch.setattr(settings,'TAVILY_API_KEY','synthetic-test-only')
    monkeypatch.setattr(settings,'CASE_URL_FETCH_ENABLED',True)
    calls={'search':0,'fetch':0}
    async def search(self,query,domains=None):
        calls['search']+=1
        assert '17556/HR/ALL-INDIA/2026' in query.upper()
        return ResearchResult(status='COMPLETED',reason='Synthetic transport fixture',sources=[ResearchSource(id='search-fixture',title='Synthetic notice',url='https://bel-india.in/example.pdf',extracted_information='Search snippet is not verification',source_type='OFFICIAL_DOMAIN',relevance=.9,retrieved_at='2026-11-01T00:00:00+00:00',claim=query)])
    async def fetch(url,allow_pdf=False,allowed_domains=None):
        calls['fetch']+=1
        assert allow_pdf and allowed_domains==['bel-india.in']
        body=analyze_pdf_document(pdf(1),'synthetic.pdf')['text'] if remote==TEXT else remote
        return {'text':body,'final_url':url,'redirect_chain':[url],'truncated':False,'content_type':'application/pdf'}
    monkeypatch.setattr(TavilyService,'search',search)
    monkeypatch.setattr(case_url_fetcher,'fetch_public_text',fetch)
    return calls

def test_case_exact_notice_action_executes_persists_and_is_idempotent(monkeypatch):
    calls=mock_notice_transport(monkeypatch)
    case=add(create_case(),TEXT)
    assert case['assessment']['verification_status']=='UNRESOLVED'
    path=f"/api/cases/{case['case_id']}/actions/verify_notice"
    response=client.post(path,json={'expected_revision':case['revision']})
    assert response.status_code==200,response.text
    case=response.json()
    assert calls=={'search':1,'fetch':1}
    assert case['assessment']['verification_status']=='INDEPENDENTLY_VERIFIED_CLAIM'
    assert case['assessment']['offer_authenticity']=='UNRESOLVED' and case['fusion']['risk_score'] is None
    edges=[e for e in case['graph']['edges'] if e.get('relationship_status')=='VERIFIED']
    assert edges and all(e['source'].startswith('independent-') for e in edges)
    again=client.post(path,json={'expected_revision':case['revision']})
    assert again.status_code==200 and again.json()==case
    assert calls=={'search':1,'fetch':1}
    stored=client.get('/api/cases/'+case['case_id']).json()
    assert stored['notice_review']==case['notice_review']
    removed=client.request('DELETE',f"/api/cases/{case['case_id']}/sources/{case['sources'][0]['id']}",json={'expected_revision':case['revision']}).json()
    assert not removed['assessment']['verified_claims'] and not removed['evidence']

def test_single_scan_exact_notice_action_and_unrelated_search_separation(monkeypatch):
    calls=mock_notice_transport(monkeypatch)
    scan=post(TEXT)
    assert calls['fetch']==0 and not scan['assessment']['verified_claims']
    response=client.post(f"/api/investigations/{scan['id']}/actions/verify_notice",json={'expected_revision':scan['investigation']['revision']})
    assert response.status_code==200,response.text
    state=response.json()
    assert calls['fetch']==1 and state['assessment']['verified_claims']
    stored=client.get('/api/scans/'+scan['id']).json()
    assert stored['assessment']['offer_authenticity']=='UNRESOLVED'
    assert all(v['claim_id'] in {c['id'] for c in stored['investigation']['claims']} for v in stored['assessment']['verified_claims'])

def test_actual_independent_contradiction_updates_case_fusion(monkeypatch):
    mock_notice_transport(monkeypatch,TEXT.replace('vacancies: 350','vacancies: 351'))
    case=add(create_case(),TEXT)
    response=client.post(f"/api/cases/{case['case_id']}/actions/verify_notice",json={'expected_revision':case['revision']})
    assert response.status_code==200,response.text
    case=response.json()
    assert case['assessment']['state']=='ELEVATED_CONCERN' and case['fusion']['risk_score'] is not None
    assert any(c['status']=='CONTRADICTED' and c['claim_type']=='vacancies' for c in case['notice_review']['claim_results'])
    assert case['assessment']['offer_authenticity']=='UNRESOLVED'

def test_client_metadata_or_two_uploads_cannot_declare_independence():
    response=client.post('/api/analyze/text',json={'input_type':'text','content':TEXT,'metadata':{'notice_verification':True,'independent_documents':[document(TEXT)]}})
    assert response.status_code==200 and not response.json()['assessment']['verified_claims']
    case=add(add(create_case(),TEXT),TEXT)
    assert not case['assessment']['verified_claims']
    assert not any(e.get('relationship_status')=='VERIFIED' for e in case['graph']['edges'])
    assert len([e for e in case['cross_source_findings'] if e['kind']=='NEW_PAYMENT_REQUEST'])==1

def test_exact_notice_disabled_retrieval_does_not_spend_budget(monkeypatch):
    monkeypatch.setattr(settings,'TAVILY_API_KEY','synthetic-test-only')
    monkeypatch.setattr(settings,'CASE_URL_FETCH_ENABLED',False)
    case=add(create_case(),TEXT)
    action=next(a for a in case['recommendations'] if a['action_id']=='verify_notice')
    assert action['status']=='UNAVAILABLE' and 'disabled' in action['unavailable_reason']
    response=client.post(f"/api/cases/{case['case_id']}/actions/verify_notice",json={'expected_revision':case['revision']})
    assert response.status_code==409
    assert client.get('/api/cases/'+case['case_id']).json()['research_calls']==0

class FetchResponse:
    def __init__(self,body=b'',status=200,headers=None):self.body=io.BytesIO(body);self.status=status;self.headers=headers or {'Content-Type':'application/pdf','Content-Length':str(len(body))}
    def getheader(self,key,default=None):return self.headers.get(key,default)
    def read(self,size):return self.body.read(size)
class FetchConnection:
    sock=None
    def __init__(self,response):self.response=response
    def request(self,*args,**kwargs):pass
    def getresponse(self):return self.response
    def close(self):pass

def test_bounded_fetch_can_parse_official_pdf_and_blocks_outside_redirect(monkeypatch):
    from app.services import case_url_fetcher as urls
    monkeypatch.setattr(urls,'validate_and_resolve_url',lambda url,resolve_dns=True:(True,url,['93.184.216.34']))
    opened=[]
    def connect(parsed,address,timeout):opened.append(parsed.hostname);return FetchConnection(FetchResponse(pdf(1)))
    monkeypatch.setattr(urls,'open_connection',connect)
    result=urls.fetch_public_text_sync('https://bel-india.in/example.pdf',allow_pdf=True,allowed_domains=['bel-india.in'])
    assert '17556/HR/All-India/2026' in result['text'] and result['content_type']=='application/pdf'
    monkeypatch.setattr(urls,'open_connection',lambda *args:FetchConnection(FetchResponse(status=302,headers={'Location':'https://attacker.example/doc'})))
    with pytest.raises(urls.URLFetchError,match='boundary'):
        urls.fetch_public_text_sync('https://bel-india.in/example.pdf',allow_pdf=True,allowed_domains=['bel-india.in'])

@pytest.mark.parametrize('response,code',[
    (FetchResponse(b'not pdf'),'URL_PDF_NO_TEXT'),
    (FetchResponse(headers={'Content-Type':'application/pdf','Content-Length':str(2*1024*1024+1)}),'URL_TOO_LARGE'),
])
def test_pdf_verification_fetch_errors_are_explicit(monkeypatch,response,code):
    from app.services import case_url_fetcher as urls
    monkeypatch.setattr(urls,'validate_and_resolve_url',lambda url,resolve_dns=True:(True,url,['93.184.216.34']))
    monkeypatch.setattr(urls,'open_connection',lambda *args:FetchConnection(response))
    with pytest.raises(urls.URLFetchError) as error:urls.fetch_public_text_sync('https://bel-india.in/example.pdf',allow_pdf=True,allowed_domains=['bel-india.in'])
    assert error.value.code==code


def test_fee_tax_or_category_uncertainty_is_not_independent_authentication():
    submitted=TEXT.replace('INR 1,000 + GST = INR 1,180','INR 999')
    review=compare_notice(extract_claims('submitted',submitted,'text'),[{'notice_verification':True,'independent_documents':[document(TEXT)]}])
    fee_results=[c for c in review['claim_results'] if c['claim_type']=='fee']
    assert fee_results and all(c['status'] in {'UNRESOLVED','POSSIBLE_INCONSISTENCY'} for c in fee_results)
    fees=[e for e in notice_evidence(review) if e['claim_type']=='fee']
    assert fees and all(e['verification_status']!='INDEPENDENTLY_VERIFIED' for e in fees)

def test_explicitly_comparable_fee_totals_can_be_contradicted():
    base='Organization: Bharat Electronics Limited\nAdvertisement number: 17556/HR/All-India/2026\nJob title: Probationary Engineer\n'
    submitted=base+'Application fee for all candidates is INR 999 including GST.'
    remote=base+'Application fee for all candidates is INR 1180 including GST.'
    review=compare_notice(extract_claims('submitted',submitted,'text'),[{'notice_verification':True,'independent_documents':[document(remote)]}])
    fee=next(c for c in review['claim_results'] if c['claim_type']=='fee')
    assert fee['status']=='CONTRADICTED' and len(fee['citations'])==2


@pytest.mark.parametrize('text',[
    'Candidates are required to log on to the website and enter their credentials to download their call letter.',
    'Application Sequence Number, password and all other communication will be sent on the same registered e-mail ID.',
    'User-Id and password will be sent through e-mail / SMS on registered E-Mail and Mobile Number.',
])
def test_real_world_account_instruction_phrasings(text):
    result=analyze_sensitive_data_requests(text)
    assert not result['has_critical'] and result['account_instructions']

@pytest.mark.parametrize('text',[
    'Candidates will be redirected to the application payment gateway to deposit the fee.',
    'Last Date of submission of Online Application with Fee through Debit/Credit Card.',
    'Guidelines for remittance of fee after completing the application.',
])
def test_application_policy_variants_are_not_critical(text):
    scan=post(text)
    assert scan['risk_level']=='UNDETERMINED'
    assert not any(e['severity']=='critical' for e in scan['evidence'])

def test_passport_size_photo_and_company_portfolio_are_not_identity_requests():
    result=analyze_sensitive_data_requests('A Government Enterprise with a portfolio of products. Please upload one recent passport size photograph.')
    assert not result['flags'] and not result['has_medium']

def test_category_exemptions_do_not_become_a_global_no_fee_claim():
    text='Do I need to pay application fee?\n1. EWS - Yes-forRs.1000/- + GST\n2. SC - No application fee\n3. ST - No application fee'
    claims=extract_claims('source',text,'text')
    assert not any(c['claim_type']=='fee_policy' and c['value']=='NO_FEES' for c in claims)
    assert any(c['claim_type']=='fee_exemption' for c in claims)
    money=analyze_payment_risk(text)['monetary_entities']
    assert money and money[0]['value']=='1000' and money[0]['category']=='APPLICATION_FEE'

def test_internal_fee_scope_inconsistency_is_cited_and_not_proof_of_fraud():
    text='Candidates belonging to GEN/EWS/OBC category are required to pay an application fee of INR 1180.\nSC/ST/EWS candidates are exempted from payment of application fee.'
    scan=post(text);evidence=[e for e in scan['evidence'] if e['category']=='recruitment_policy_conflict']
    assert len(evidence)==1 and evidence[0]['observed_value']=='EWS'
    assert evidence[0]['severity']=='moderate' and len(evidence[0]['citations'])==2
    assert scan['risk_level']=='UNDETERMINED' and scan['assessment']['offer_authenticity']=='UNRESOLVED'

def test_actual_user_pdf_regression_when_supplied():
    import os,hashlib
    source=os.getenv('BEL_REGRESSION_PDF')
    if not source:pytest.skip('Set BEL_REGRESSION_PDF to run the unbundled original-document regression')
    file=Path(source)
    assert file.is_file()
    assert hashlib.sha256(file.read_bytes()).hexdigest()=='5f4ffad40045db812cac1cddd0c54a0d7e3a36d46a8e7371972277a8e9e2652c'
    response=client.post('/api/analyze/pdf',files={'file':(file.name,file.read_bytes(),'application/pdf')})
    assert response.status_code==200,response.text
    scan=response.json();state=scan['investigation']
    assert scan['risk_level']=='UNDETERMINED' and scan['trust_score'] is None
    assert not any(e['severity']=='critical' for e in state['evidence'])
    assert len([e for e in state['evidence'] if e['category']=='payment_risk'])==1
    assert not any(e['category']=='sensitive_data_request' and e['severity']=='critical' for e in state['evidence'])
    assert any(m['value']=='200000' and m['role']=='CONTRACTUAL_LIABILITY' for m in state['monetary_entities'])
    assert {m['value'] for m in state['monetary_entities'] if m['role']=='PAYMENT'}=={'1000','1180'}
    values=lambda kind:[c['value'] for c in state['claims'] if c['claim_type']==kind]
    assert values('vacancies')==[350]
    assert '2026-10-28' in values('publication_date') and '2026-11-18' in values('application_deadline')
    assert values('eligibility')
    assert not values('fee_policy')
    assert state['assessment']['offer_authenticity']=='UNRESOLVED' and not state['assessment']['verified_claims']
    ews=next(e for e in state['evidence'] if e['category']=='recruitment_policy_conflict' and e['observed_value']=='EWS')
    assert {5,11,13,15} <= {r.get('page') for r in ews['citations']}
    for evidence in state['evidence']:
        for s in evidence['source_spans']:assert scan['input_content'][s['start']:s['end']]==s['text']


def test_exact_notice_retrieval_attempts_are_bounded_on_failure(monkeypatch):
    from app.services.notice_verification import retrieve_notice
    from app.services import case_url_fetcher
    from app.integrations.web_research.tavily_service import TavilyService
    monkeypatch.setattr(settings,'CASE_URL_FETCH_ENABLED',True)
    calls=[]
    async def search(*args,**kwargs):return ResearchResult(status='COMPLETED',sources=[ResearchSource(id=str(i),title='Synthetic source',url=f'https://bel-india.in/{i}.pdf',extracted_information='snippet',source_type='OFFICIAL_DOMAIN',relevance=.5,retrieved_at='2026-11-01T00:00:00+00:00',claim='test') for i in range(5)])
    async def unavailable(url,**kwargs):calls.append(url);raise case_url_fetcher.URLFetchError('URL_UNAVAILABLE','Synthetic retrieval failure')
    monkeypatch.setattr(TavilyService,'search',search);monkeypatch.setattr(case_url_fetcher,'fetch_public_text',unavailable)
    result=asyncio.run(retrieve_notice(extract_claims('source',TEXT,'text')))
    assert len(calls)==2 and len(result['retrieval_errors'])==2
    assert not result['independent_documents'] and 'unresolved' in result['reason']


def test_known_company_and_gateway_text_never_bypass_explicit_harm():
    scan=post(TEXT+'\nOfficial website: https://bel-india.in\nSend your OTP to this recruiter. Pay application fee INR 1180 to my personal account: ALICE123.')
    assert scan['risk_level']=='ELEVATED CONCERN'
    assert scan['assessment']['offer_authenticity']=='UNRESOLVED'
    assert any(e['category']=='payment_risk' and e['severity']=='critical' for e in scan['evidence'])
    assert any(e['category']=='sensitive_data_request' and e['severity']=='critical' for e in scan['evidence'])
