import io
import json
from copy import deepcopy
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.core.database import SessionLocal
from app.models.all_models import InvestigationCase,InvestigationSource,CrossSourceFinding,CaseAssessmentRevision
from app.services.case_claims import extract_claims
from app.services import case_url_fetcher as urls

client=TestClient(app)
POSTER='Microsoft internship\nRole: Software engineering intern\nStipend INR 15,000 per month.\nDuration: 3 months\nApply only through the official portal: https://careers.microsoft.com/jobs'
FEE='Microsoft internship. Pay a refundable registration fee of ₹999.\nRecruitment email: hr@unverified.example\nSend Aadhaar card immediately.'

def create(title='Software internship investigation'):
    r=client.post('/api/cases',json={'title':title});assert r.status_code==200,r.text;return r.json()

def add(case,text,kind='text',title='Message'):
    r=client.post('/api/cases/'+case['case_id']+'/sources',json={'input_type':kind,'content':text,'title':title,'expected_revision':case['revision']})
    assert r.status_code==200,r.text;return r.json()

def png():
    from PIL import Image
    stream=io.BytesIO();Image.new('RGB',(600,120),'white').save(stream,format='PNG');return stream.getvalue()

def upload(case,content,kind='screenshot',filename='Google_filename_only.png'):
    r=client.post('/api/cases/'+case['case_id']+'/sources/upload',data={'input_type':kind,'expected_revision':case['revision']},files={'file':(filename,content,'image/png' if kind=='screenshot' else 'application/pdf')})
    assert r.status_code==200,r.text;return r.json()

def review(case,text=None):
    source=case['sources'][-1]
    r=client.post(f"/api/cases/{case['case_id']}/sources/{source['id']}/review",json={'content':text if text is not None else source['extracted_text'],'expected_revision':case['revision']})
    assert r.status_code==200,r.text;return r.json()


def test_scenario_a_poster_extraction_review_undetermined(monkeypatch):
    import pytesseract
    monkeypatch.setattr(pytesseract,'image_to_string',lambda *a,**k:POSTER)
    case=upload(create(),png())
    assert case['sources'][0]['processing_status']=='NEEDS_REVIEW'
    assert not case['evidence'] and case['fusion']['risk_level']=='UNDETERMINED'
    case=review(case)
    assert case['sources'][0]['processing_status']=='READY'
    assert {c['claim_type'] for c in case['claims']} >= {'organization','opportunity_type','compensation','duration','role','application_url','application_method'}
    assert case['fusion']['risk_level']=='UNDETERMINED'
    assert not any(c['value']=='Google' for c in case['claims'])
    assert all(c['verification_status']=='CLAIMED' for c in case['claims'])
    assert not any(e['relationship_status']=='VERIFIED' for e in case['graph']['edges'])


def test_scenario_b_second_source_fee_updates_same_case():
    first=add(create(),POSTER,title='Poster')
    second=add(first,FEE,title='Recruiter fee request')
    assert second['case_id']==first['case_id'] and len(second['sources'])==2
    assert second['revision']>first['revision']
    assert second['fusion']['risk_level']!='UNDETERMINED'
    assert any(c['claim_type']=='fee' and c['value']['value']=='999' for c in second['claims'])
    assert any(f['kind']=='NEW_PAYMENT_REQUEST' and f['classification']=='NEW_INFORMATION' for f in second['cross_source_findings'])
    assert not any(f['kind']=='FEE_INSTRUCTION_CONFLICT' for f in second['cross_source_findings'])


def test_scenario_c_pdf_and_message_stipend_contradiction():
    from reportlab.pdfgen.canvas import Canvas
    buffer=io.BytesIO();pdf=Canvas(buffer);pdf.drawString(40,750,'Microsoft internship. Stipend INR 15,000 per month.');pdf.save()
    case=upload(create(),buffer.getvalue(),'pdf','unrelated_filename.pdf')
    case=review(case)
    case=add(case,'Microsoft internship. Stipend INR 25,000 per month.',title='Recruiter message')
    finding=next(f for f in case['cross_source_findings'] if f['kind']=='COMPENSATION_CONFLICT')
    assert finding['classification']=='CONFIRMED_CONTRADICTION'
    assert len({c['source_id'] for c in finding['citations']})==2
    for cite in finding['citations']:
        source=next(s for s in case['sources'] if s['id']==cite['source_id'])
        assert source[cite['field']][cite['start']:cite['end']]==cite['excerpt']
    assert any('page' in c for c in finding['citations'])


def test_scenario_d_two_identical_screenshots_do_not_raise_confidence(monkeypatch):
    import pytesseract
    monkeypatch.setattr(pytesseract,'image_to_string',lambda *a,**k:POSTER)
    case=review(upload(create(),png()))
    original=deepcopy(case['fusion'])
    case=review(upload(case,png(),filename='copy.png'))
    assert len(case['sources'])==2 and case['distinct_content_count']==1 and len(case['duplicate_sources'])==1
    assert case['fusion']['confidence']==original['confidence']
    assert case['fusion']['risk_score']==original['risk_score']
    assert case['fusion']['evidence_coverage']==original['evidence_coverage']
    assert any(f['classification']=='SUPPORTING_CLAIMS' for f in case['cross_source_findings'])


def test_scenario_e_remove_source_recomputes_and_preserves_old_revision():
    base=add(create(),'Microsoft internship. Stipend INR 15,000 per month.')
    case=add(base,'Microsoft internship. Stipend INR 25,000 per month.')
    previous=case['revision'];removed=case['sources'][-1]['id']
    r=client.request('DELETE',f"/api/cases/{case['case_id']}/sources/{removed}",json={'expected_revision':case['revision']})
    assert r.status_code==200,r.text;updated=r.json()
    assert len(updated['sources'])==1
    assert not updated['cross_source_findings']
    assert updated['fusion']['risk_level']=='UNDETERMINED'
    assert all(n['id']!=removed for n in updated['graph']['nodes'])
    old=client.get(f"/api/cases/{case['case_id']}/revisions/{previous}").json()
    assert len(old['sources'])==2 and old['cross_source_findings']
    with SessionLocal() as db:
        assert db.get(InvestigationSource,removed).removed_at is not None
        assert not db.query(CrossSourceFinding).filter_by(case_id=case['case_id'],active=True).all()


def test_scenario_f_ocr_error_is_persisted_without_findings(monkeypatch):
    import pytesseract
    def missing(*a,**k):raise pytesseract.TesseractNotFoundError()
    monkeypatch.setattr(pytesseract,'image_to_string',missing)
    case=upload(create(),png())
    source=case['sources'][0]
    assert source['processing_status']=='FAILED' and source['error_code']=='OCR_ENGINE_MISSING'
    assert not case['claims'] and not case['evidence'] and not case['cross_source_findings']
    assert case['fusion']['risk_level']=='UNDETERMINED'
    assert not source['scan_id']


def test_scenario_g_external_research_unavailable_remains_unresolved():
    case=add(create(),POSTER)
    action=next(a for a in case['recommendations'] if a['action_id']=='official_listing')
    assert action['status']=='UNAVAILABLE' and 'TAVILY_API_KEY' in action['unavailable_reason']
    response=client.post(f"/api/cases/{case['case_id']}/actions/official_listing",json={'expected_revision':case['revision']})
    assert response.status_code==409
    assert client.get('/api/cases/'+case['case_id']).json()['fusion']['risk_level']=='UNDETERMINED'


def test_all_claim_spans_are_exact_and_missing_fields_not_invented():
    text='Organization: Acme Labs\nRole: Data intern\nRecruiter: Priya Shah\nDuration: 12 weeks\nRecruitment email: priya@acme.example\nApply only via email. Phone: +91 98765 43210\nNo registration fees. Submit Aadhaar.'
    claims=extract_claims('source',text,'text')
    for c in claims:assert text[c['location']['start']:c['location']['end']]==c['excerpt']
    assert {c['claim_type'] for c in claims}>={'organization','role','recruiter_name','duration','sender_email','application_method','contact_number','fee_policy','sensitive_data_request'}
    assert not any(c['claim_type']=='compensation' for c in claims)
    assert not extract_claims('empty','','text')


def test_missing_field_never_becomes_a_contradiction():
    case=add(create(),'Microsoft internship. Duration: 3 months')
    case=add(case,'Microsoft internship. Please see the application instructions.')
    assert not any(f['classification']=='CONFIRMED_CONTRADICTION' for f in case['cross_source_findings'])


@pytest.mark.parametrize('first,second,kind,classification',[
    ('Duration: 3 months','Duration: 6 months','DURATION_CONFLICT','CONFIRMED_CONTRADICTION'),
    ('Duration: 3 months','Duration: 12 weeks','DURATION_CONFLICT','POSSIBLE_INCONSISTENCY'),
    ('Organization: Acme Labs','Organization: Other Company','ORGANIZATION_CONFLICT','CONFIRMED_CONTRADICTION'),
    ('Recruitment email: a@one.example','Recruitment email: b@two.example','SENDER_EMAIL_CONFLICT','POSSIBLE_INCONSISTENCY'),
    ('Apply only via email.','Apply only through WhatsApp.','APPLICATION_METHOD_CONFLICT','CONFIRMED_CONTRADICTION'),
    ('No registration fees.','Pay registration fee INR 999.','FEE_INSTRUCTION_CONFLICT','CONFIRMED_CONTRADICTION'),
])
def test_cross_source_types(first,second,kind,classification):
    case=add(add(create(),first),second)
    assert any(f['kind']==kind and f['classification']==classification for f in case['cross_source_findings'])


def test_stale_revision_and_foreign_source_rejected():
    case=create();original=deepcopy(case);case=add(case,'Microsoft internship.')
    response=client.post('/api/cases/'+case['case_id']+'/sources',json={'input_type':'text','content':'other source','expected_revision':original['revision']})
    assert response.status_code==409
    foreign=add(create(),'Different source')
    response=client.request('DELETE',f"/api/cases/{case['case_id']}/sources/{foreign['sources'][0]['id']}",json={'expected_revision':case['revision']})
    assert response.status_code==404
    assert len(client.get('/api/cases/'+case['case_id']).json()['sources'])==1


def test_case_sender_action_updates_and_does_not_duplicate():
    case=add(create(),FEE);action=next(a for a in case['recommendations'] if a['action_id'].startswith('sender:'))
    before=len(case['evidence']);path=f"/api/cases/{case['case_id']}/actions/{action['action_id']}"
    response=client.post(path,json={'expected_revision':case['revision']});assert response.status_code==200,response.text
    case=response.json();assert len(case['evidence'])==before+1
    assert case['last_action']['status']=='COMPLETED'
    again=client.post(path,json={'expected_revision':case['revision']})
    assert again.json()==case


def test_removed_duplicate_primary_promotes_remaining_copy():
    case=add(add(create(),FEE),FEE)
    score=case['fusion']['risk_score'];source=case['sources'][0]
    response=client.request('DELETE',f"/api/cases/{case['case_id']}/sources/{source['id']}",json={'expected_revision':case['revision']})
    assert response.status_code==200
    assert response.json()['fusion']['risk_score']==score
    assert response.json()['duplicate_sources']=={}


def test_url_fetch_unconfigured_still_analyzes_url_without_page_claims():
    case=add(create(),'https://example.com/job','url')
    source=case['sources'][0]
    assert source['processing_status']=='READY' and source['extraction_status']=='UNAVAILABLE'
    assert 'disabled' in source['error_message']
    assert any(c['claim_type']=='application_url' for c in case['claims'])
    assert not any(c['claim_type']=='compensation' for c in case['claims'])


@pytest.mark.parametrize('target',['http://127.0.0.1/','http://169.254.169.254/','http://localhost/','file:///etc/passwd','https://public.example:22/'])
def test_blocked_url_source_does_not_connect(target):
    case=create()
    response=client.post('/api/cases/'+case['case_id']+'/sources',json={'input_type':'url','content':target,'expected_revision':case['revision']})
    assert response.status_code==422


class Response:
    def __init__(self,status=200,headers=None,body=b'<h1>Internship</h1>'):
        self.status=status;self.headers=headers or {'Content-Type':'text/html'};self.body=io.BytesIO(body)
    def getheader(self,k,default=None):return self.headers.get(k,default)
    def read(self,n):return self.body.read(n)
class Connection:
    sock=None
    def __init__(self,response):self.response=response
    def request(self,*a,**k):pass
    def getresponse(self):return self.response
    def close(self):pass


def test_url_fetch_pins_validated_ip_and_rejects_private_redirect(monkeypatch):
    actual=urls.validate_and_resolve_url
    def resolve(url,resolve_dns=True):
        if 'public.example' in url:return True,url,['93.184.216.34']
        return actual(url,resolve_dns=resolve_dns)
    monkeypatch.setattr(urls,'validate_and_resolve_url',resolve)
    opened=[]
    def connect(parsed,address,timeout):
        opened.append((parsed.hostname,address));return Connection(Response(302,{'Location':'http://127.0.0.1/internal'}))
    monkeypatch.setattr(urls,'open_connection',connect)
    with pytest.raises(urls.URLFetchError,match='blocked'):urls.fetch_public_text_sync('https://public.example/job')
    assert opened==[('public.example','93.184.216.34')]


@pytest.mark.parametrize('response,code',[(Response(headers={'Content-Type':'text/html','Content-Length':'9999999'}),'URL_TOO_LARGE'),
    (Response(headers={'Content-Type':'application/octet-stream'}),'URL_CONTENT_TYPE'),
    (Response(body=b'x'*(urls.MAX_BYTES+1)),'URL_TOO_LARGE'),
    (Response(headers={'Content-Type':'text/html','Content-Encoding':'gzip'}),'URL_ENCODING_UNSUPPORTED')])
def test_url_fetch_size_and_type_limits(monkeypatch,response,code):
    monkeypatch.setattr(urls,'validate_and_resolve_url',lambda *a,**k:(True,a[0],['93.184.216.34']))
    monkeypatch.setattr(urls,'open_connection',lambda *a,**k:Connection(response))
    with pytest.raises(urls.URLFetchError) as exc:urls.fetch_public_text_sync('https://public.example')
    assert exc.value.code==code


def test_case_owner_enforced_outside_demo(monkeypatch):
    import uuid
    token=client.post('/api/auth/register',json={'email':uuid.uuid4().hex+'@example.com','password':'long-test-password'}).json()['access_token']
    headers={'Authorization':'Bearer '+token}
    anonymous=create()
    monkeypatch.setattr(settings,'DEMO_MODE',False)
    assert client.get('/api/cases/'+anonymous['case_id'],headers=headers).status_code==404
    own=client.post('/api/cases',headers=headers,json={'title':'Owned case'}).json()
    assert client.get('/api/cases/'+own['case_id'],headers=headers).status_code==200
    assert client.get('/api/cases/'+own['case_id']).status_code==401


def test_fetched_url_content_reuses_scanners_with_original_url(monkeypatch):
    monkeypatch.setattr(settings,'CASE_URL_FETCH_ENABLED',True)
    async def fetch(url):return {'text':'Microsoft internship. Stipend INR 15,000 per month.','final_url':url,'redirect_chain':[url],'truncated':False,'bytes_read':100}
    monkeypatch.setattr(urls,'fetch_public_text',fetch)
    case=add(create(),'https://example.com/careers','url')
    source=case['sources'][0]
    assert source['processing_status']=='READY' and source['extraction_status']=='SUCCESS'
    assert source['analysis']['baseline']['primary_domain']=='example.com'
    assert any(c['claim_type']=='compensation' for c in case['claims'])


def test_decimal_formatting_is_not_a_compensation_contradiction():
    case=add(add(create(),'Stipend INR 15,000 per month.'),'Stipend INR 15000.00 per month.')
    assert not any(f['kind']=='COMPENSATION_CONFLICT' for f in case['cross_source_findings'])


def test_same_amount_with_different_periods_is_not_confirmed_comparable():
    case=add(add(create(),'Stipend INR 15,000 per month.'),'Stipend INR 15,000 per year.')
    finding=next(f for f in case['cross_source_findings'] if f['kind']=='COMPENSATION_CONFLICT')
    assert finding['classification']=='POSSIBLE_INCONSISTENCY'


def test_case_research_completion_does_not_authenticate_claims(monkeypatch):
    from app.integrations.web_research.tavily_service import TavilyService
    from app.schemas.investigation import ResearchResult,ResearchSource
    monkeypatch.setattr(settings,'TAVILY_API_KEY','mock-key')
    async def research(self,query,official_domains=None):
        return ResearchResult(status='COMPLETED',query=query,reason='Retrieved context, not offer authentication',sources=[ResearchSource(
            id='mock-source',title='Careers',url='https://careers.microsoft.com',extracted_information='Careers page',retrieved_at='2026-11-01T00:00:00Z',source_type='OFFICIAL_DOMAIN',relevance=.9,claim=query)])
    monkeypatch.setattr(TavilyService,'search',research)
    case=add(create(),POSTER)
    response=client.post(f"/api/cases/{case['case_id']}/actions/official_listing",json={'expected_revision':case['revision']})
    assert response.status_code==200,response.text
    result=response.json()
    assert result['last_action']['status']=='COMPLETED' and result['research_calls']==1
    assert result['fusion']['risk_level']=='UNDETERMINED'
    assert not result.get('running_action')
    assert not any(e['relationship_status']=='VERIFIED' for e in result['graph']['edges'])
    assert next(a for a in result['recommendations'] if a['action_id']=='official_listing')['status']=='COMPLETED'


def test_case_research_failure_exposes_reason_without_fake_findings(monkeypatch):
    from app.integrations.web_research.tavily_service import TavilyService
    from app.schemas.investigation import ResearchResult
    monkeypatch.setattr(settings,'TAVILY_API_KEY','mock-key')
    async def unavailable(self,query,official_domains=None):return ResearchResult(status='SEARCH_UNAVAILABLE',reason='Mock provider unavailable')
    monkeypatch.setattr(TavilyService,'search',unavailable)
    case=add(create(),POSTER);before=deepcopy(case['evidence'])
    for _ in range(3):
        response=client.post(f"/api/cases/{case['case_id']}/actions/official_listing",json={'expected_revision':case['revision']})
        assert response.status_code==200,response.text;case=response.json()
        assert case['last_action']['status']=='UNAVAILABLE'
        assert case['evidence']==before
    assert case['research_calls']==3
    assert next(a for a in case['recommendations'] if a['action_id']=='official_listing')['status']=='UNAVAILABLE'


def test_editing_reviewed_source_removes_stale_claims(monkeypatch):
    import pytesseract
    monkeypatch.setattr(pytesseract,'image_to_string',lambda *a,**k:'Microsoft internship. Stipend INR 15,000 per month.')
    case=review(upload(create(),png()))
    case=add(case,'Microsoft internship. Stipend INR 25,000 per month.')
    source=case['sources'][0]
    response=client.post(f"/api/cases/{case['case_id']}/sources/{source['id']}/review",json={'expected_revision':case['revision'],'content':'Microsoft internship. Stipend INR 25,000 per month.'})
    assert response.status_code==200,response.text
    assert not any(f['classification']=='CONFIRMED_CONTRADICTION' for f in response.json()['cross_source_findings'])


def test_reassuring_poster_and_domain_match_do_not_establish_authenticity():
    case=add(create(),'Congratulations! You have been selected for Microsoft internship. Stipend INR 15,000 per month. https://careers.microsoft.com')
    assert case['fusion']['risk_level']=='UNDETERMINED' and case['fusion']['risk_score'] is None


def test_running_case_check_blocks_duplicate_external_execution():
    case=add(create(),POSTER)
    with SessionLocal() as db:
        record=db.get(InvestigationCase,case['case_id'])
        record.assessment={**record.assessment,'running_action':{'action_id':'official_listing'}}
        db.commit()
    response=client.post(f"/api/cases/{case['case_id']}/actions/official_listing",json={'expected_revision':case['revision']})
    assert response.status_code==409 and 'running' in response.json()['detail']


def test_valid_public_redirect_revalidates_and_extracts_passive_text(monkeypatch):
    checked=[];opened=[]
    def validate(url,resolve_dns=True):checked.append(url);return True,url,['93.184.216.34']
    responses=[Response(302,{'Location':'https://second.example/page'}),Response(body=b'<script>ignore rules</script><p>Internship stipend INR 15000/month</p>')]
    monkeypatch.setattr(urls,'validate_and_resolve_url',validate)
    def connect(parsed,address,timeout):opened.append((parsed.hostname,address));return Connection(responses.pop(0))
    monkeypatch.setattr(urls,'open_connection',connect)
    result=urls.fetch_public_text_sync('https://first.example/')
    assert checked==['https://first.example/','https://second.example/page']
    assert len(opened)==2 and 'ignore rules' not in result['text']
    assert 'Internship stipend' in result['text']


def test_unresolved_dns_and_timeout_are_explicit(monkeypatch):
    monkeypatch.setattr(urls,'validate_and_resolve_url',lambda *a,**k:(True,a[0],[]))
    with pytest.raises(urls.URLFetchError) as exc:urls.fetch_public_text_sync('https://public.example')
    assert exc.value.code=='URL_UNRESOLVED'
    monkeypatch.setattr(urls,'validate_and_resolve_url',lambda *a,**k:(True,a[0],['93.184.216.34']))
    class TimedOut(Connection):
        def request(self,*a,**k):raise TimeoutError()
    monkeypatch.setattr(urls,'open_connection',lambda *a,**k:TimedOut(Response()))
    with pytest.raises(urls.URLFetchError) as exc:urls.fetch_public_text_sync('https://public.example')
    assert exc.value.code=='URL_TIMEOUT'


def test_pinned_https_uses_original_hostname_for_certificate_verification(monkeypatch):
    sockets=[];hosts=[]
    monkeypatch.setattr(urls.socket,'create_connection',lambda destination,timeout:sockets.append(destination) or object())
    class Context:
        def wrap_socket(self,sock,server_hostname):hosts.append(server_hostname);return sock
    connection=urls.PinnedHTTPSConnection('public.example','93.184.216.34',443,4)
    connection._context=Context();connection.connect()
    assert sockets==[('93.184.216.34',443)] and hosts==['public.example']


def test_source_removed_during_check_clears_running_state(monkeypatch):
    from datetime import datetime,timezone
    from app.services import investigation_execution
    case=add(create(),FEE)
    source_id=case['sources'][0]['id']
    async def remove_during_check(db,scan,action_id,revision):
        source=db.get(InvestigationSource,source_id)
        source.removed_at=datetime.now(timezone.utc)
        source.processing_status='REMOVED'
        db.commit()
        return source.analysis
    monkeypatch.setattr(investigation_execution,'execute_recommendation',remove_during_check)
    response=client.post(f"/api/cases/{case['case_id']}/actions/sender:{source_id}",json={'expected_revision':case['revision']})
    assert response.status_code==200,response.text
    result=response.json()
    assert not result.get('running_action') and not result['sources'] and not result['evidence']
    assert result['last_action']['status']=='UNAVAILABLE' and 'removed' in result['last_action']['message']
    assert result['fusion']['risk_level']=='UNDETERMINED'
