"""Synthetic regression inputs; no live providers or authenticity ground truth."""
import io,json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.services.ai_investigator import answer_investigator_query
from app.services.case_claims import extract_claims
from app.services.recruitment_consistency import internal_policy_findings
client=TestClient(app)
POSTER='Organization: Acme Labs\nPosition: Data Intern\nStipend INR 45000 per month.'

def create():
    r=client.post('/api/cases',json={'title':'Synthetic opportunity investigation'});assert r.status_code==200,r.text;return r.json()
def png():
    from PIL import Image
    b=io.BytesIO();Image.new('RGB',(800,120),'white').save(b,format='PNG');return b.getvalue()
def pdf():
    from reportlab.pdfgen.canvas import Canvas
    b=io.BytesIO();c=Canvas(b);c.drawString(40,740,POSTER.replace('\n','. '));c.save();return b.getvalue()
def batch(case,kinds,images=1):
    sources=[{'input_type':k,'content':'https://example.com/jobs' if k=='url' else POSTER} for k in kinds if k in {'text','url'}]
    files=[]
    if 'pdf' in kinds:files.append(('files',('notice.pdf',pdf(),'application/pdf')))
    if 'screenshot' in kinds:files.extend(('files',(f'poster{i}.png',png(),'image/png')) for i in range(images))
    return client.post(f"/api/cases/{case['case_id']}/sources/batch",data={'payload':json.dumps({'expected_revision':case['revision'],'sources':sources})},files=files)
def review_all(case):
    for source in list(case['sources']):
        if source['processing_status']!='NEEDS_REVIEW':continue
        r=client.post(f"/api/cases/{case['case_id']}/sources/{source['id']}/review",json={'content':source['extracted_text'],'expected_revision':case['revision']});assert r.status_code==200,r.text;case=r.json()
    return case
@pytest.mark.parametrize('kinds,images',[(('text',),0),(('url',),0),(('pdf',),0),(('screenshot',),1),(('url','text'),0),(('pdf','screenshot'),3),(('url','pdf','text','screenshot'),5),(('pdf','text','screenshot'),3),(('url','text','screenshot'),3),(('url','pdf','text'),0)])
def test_optional_combinations_share_one_case_and_review(kinds,images,monkeypatch):
    import pytesseract
    monkeypatch.setattr(pytesseract,'image_to_string',lambda *a,**k:POSTER)
    case=create();r=batch(case,kinds,images);assert r.status_code==200,r.text;case=r.json()
    expected=len([k for k in kinds if k!='screenshot'])+images
    assert len(case['sources'])==expected and all(s['case_id']==case['case_id'] for s in case['sources'])
    case=review_all(case)
    assert all(s['processing_status']=='READY' for s in case['sources'])
    assert case['assessment']['offer_authenticity']=='UNRESOLVED'
    assert not any(e.get('verification_status')=='INDEPENDENTLY_VERIFIED' for e in case['evidence'])

def test_batch_empty_is_rejected_and_no_sources_added():
    case=create();assert batch(case,(),0).status_code==422
    assert not client.get('/api/cases/'+case['case_id']).json()['sources']
def test_six_images_rejected_in_bulk_and_existing_route(monkeypatch):
    import pytesseract
    monkeypatch.setattr(pytesseract,'image_to_string',lambda *a,**k:POSTER)
    case=create();assert batch(case,('screenshot',),6).status_code==422
    case=batch(case,('screenshot',),5).json();assert len(case['sources'])==5
    path=f"/api/cases/{case['case_id']}/sources/upload"
    r=client.post(path,data={'input_type':'screenshot','expected_revision':case['revision']},files={'file':('six.png',png(),'image/png')});assert r.status_code==422
    case=client.request('DELETE',f"/api/cases/{case['case_id']}/sources/{case['sources'][-1]['id']}",json={'expected_revision':case['revision']}).json()
    assert batch(case,('screenshot',),1).status_code==200

def test_partial_failure_is_retained_and_other_source_processed(monkeypatch):
    from app.services import case_url_fetcher as fetcher
    monkeypatch.setattr(settings,'CASE_URL_FETCH_ENABLED',True)
    async def unavailable(*a,**k):raise fetcher.URLFetchError('URL_TIMEOUT','Remote source timed out')
    monkeypatch.setattr(fetcher,'fetch_public_text',unavailable)
    case=batch(create(),('url','text')).json()
    assert {s['processing_status'] for s in case['sources']}=={'READY','FAILED'}
    assert any(s['error_code']=='URL_TIMEOUT' for s in case['sources']) and case['claims']
    assert case['assessment']['offer_authenticity']=='UNRESOLVED'

def test_invalid_file_mime_does_not_discard_other_source():
    case=create();r=client.post(f"/api/cases/{case['case_id']}/sources/batch",data={'payload':json.dumps({'expected_revision':case['revision'],'sources':[{'input_type':'text','content':POSTER}]})},files=[('files',('fake.pdf',b'not pdf','application/pdf'))])
    assert r.status_code==200,r.text
    assert {s['processing_status'] for s in r.json()['sources']}=={'READY','FAILED'}

def test_limits_stale_revision_and_case_isolation(monkeypatch):
    monkeypatch.setattr(settings,'CASE_MAX_URLS',1)
    case=create();updated=batch(case,('url',)).json()
    assert batch(updated,('url',)).status_code==422
    assert batch(case,('text',)).status_code==409
    other=batch(create(),('text',)).json()
    assert not ({s['id'] for s in other['sources']}&{s['id'] for s in updated['sources']})
    assert all(c['source_id'] in {s['id'] for s in other['sources']} for c in other['claims'])

def test_chat_uses_canonical_claims_even_if_legacy_context_missing():
    claims=extract_claims('s','Organization: Bharat Electronics Limited\nPosition: Probationary Engineer','text')
    detail={'claimed_organization':None,'investigation':{'revision':7,'claimed_organization':None,'claims':claims,'evidence':[]}}
    result=answer_investigator_query('Is this company genuine?',detail)
    assert 'Bharat Electronics Limited' in result['answer']
    assert not any(x in result['answer'] for x in ['None','null','undefined'])
    assert result['context_revision']==7

def test_missing_organization_and_unavailable_domain_are_honest():
    for q in ['Is the organization genuine?','Why is the domain risky?','Is this safe?']:
        result=answer_investigator_query(q,{})
        assert not any(x in result['answer'] for x in ['None','null','undefined'])
        assert 'unresolved' in result['answer']

def test_case_chat_and_unified_report_use_current_stored_snapshot():
    from pypdf import PdfReader
    case=batch(create(),('text',)).json();path=f"/api/cases/{case['case_id']}"
    result=client.post(path+'/investigate',json={'question':'Is this company genuine?'});assert result.status_code==200
    assert 'Acme Labs' in result.json()['answer'] and result.json()['context_revision']==case['revision']
    report=client.get(path+'/report/pdf');assert report.status_code==200 and report.headers['content-type']=='application/pdf'
    text='\n'.join(p.extract_text() for p in PdfReader(io.BytesIO(report.content)).pages)
    assert 'Acme Labs' in text and 'Specific offer authenticity remains unresolved' in text
    assert case['sources'][0]['id'] in text and 'READY' in text
    assert client.get(path).json()['revision']==case['revision']

HEADER='Organization: Acme Labs\nAdvertisement number: ACME/2026/1\nPosition: Engineer\n'
@pytest.mark.parametrize('text,expected',[
 ('Candidates belonging to General category are required to pay an application fee. SC/ST candidates are exempted from payment of application fee.',False),
 ('EWS candidates must pay an application fee. EWS candidates are exempted from payment of application fee.',True),
])
def test_fee_categories_do_not_imply_unscoped_contradiction(text,expected):
    findings=internal_policy_findings(extract_claims('s',HEADER+text,'text'))
    assert bool(findings)==expected
    assert not any(f['verification_status']=='OBSERVED_POLICY_CONTRADICTION' for f in findings)
    if findings:assert 'Possible inconsistency' in findings[0]['evidence']

def test_explicit_same_scope_contradiction_retains_both_excerpts():
    text=HEADER+'For all applicants in this category, EWS candidates must pay an application fee.\nFor all applicants in this category, EWS candidates are exempted from payment of application fee.'
    findings=internal_policy_findings(extract_claims('s',text,'text'))
    assert len(findings)==1 and findings[0]['verification_status']=='OBSERVED_POLICY_CONTRADICTION'
    assert len(findings[0]['citations'])==2
    assert all(text[c['start']:c['end']]==c['excerpt'] for c in findings[0]['citations'])

def test_different_applicant_conditions_are_not_contradictory():
    text=HEADER+'EWS candidates must pay an application fee if resident of North district.\nEWS candidates are exempted from payment of application fee if resident of South district.'
    assert not internal_policy_findings(extract_claims('s',text,'text'))

def test_official_only_switch_does_not_enable_arbitrary_urls(monkeypatch):
    from app.services.notice_verification import notice_action
    monkeypatch.setattr(settings,'OFFICIAL_NOTICE_FETCH_ENABLED',True);monkeypatch.setattr(settings,'CASE_URL_FETCH_ENABLED',False);monkeypatch.setattr(settings,'TAVILY_API_KEY','synthetic-test-key')
    text='Organization: Bharat Electronics Limited\nAdvertisement number: BEL/2026/1\nPosition: Engineer'
    assert notice_action(extract_claims('s',text,'text'),0)['status']=='AVAILABLE'
    case=batch(create(),('url',)).json();assert case['sources'][0]['extraction_status']=='UNAVAILABLE'


def test_new_case_routes_enforce_owner_and_authentication(monkeypatch):
    import uuid
    monkeypatch.setattr(settings,'DEMO_MODE',False)
    def headers():
        r=client.post('/api/auth/register',json={'email':uuid.uuid4().hex+'@example.com','password':'synthetic-long-password'});assert r.status_code==200,r.text
        return {'Authorization':'Bearer '+r.json()['access_token']}
    owner,other=headers(),headers()
    r=client.post('/api/cases',json={'title':'Private synthetic opportunity'},headers=owner);assert r.status_code==200;case=r.json();path='/api/cases/'+case['case_id']
    for suffix,method,payload in [('/investigate','POST',{'question':'Is it genuine?'}),('/report/pdf','GET',None)]:
        for auth,status in [(other,404),({},401)]:
            r=client.request(method,path+suffix,json=payload,headers=auth);assert r.status_code==status,r.text
    payload={'payload':json.dumps({'expected_revision':case['revision'],'sources':[{'input_type':'text','content':POSTER}]})}
    assert client.post(path+'/sources/batch',data=payload,headers=other).status_code==404
    assert client.post(path+'/sources/batch',data=payload).status_code==401
    assert client.post(path+'/sources/batch',data=payload,headers=owner).status_code==200
    assert client.get(path+'/report/pdf',headers=owner).status_code==200

def test_case_revisions_and_duplicate_evidence_survive_batch_additions():
    first=batch(create(),('text',)).json()
    before=first['fusion'];later=batch(first,('text',)).json()
    assert len(later['duplicate_sources'])==1
    assert later['fusion']['risk_score']==before['risk_score'] and later['fusion']['confidence']==before['confidence']
    old=client.get(f"/api/cases/{later['case_id']}/revisions/{first['revision']}").json()
    assert len(old['sources'])==1 and len(later['sources'])==2

def test_case_chat_citations_reference_actual_evidence():
    case=create();r=client.post(f"/api/cases/{case['case_id']}/sources",json={'input_type':'text','content':'Organization: Acme Labs. Pay registration fee INR 999 to my personal account.','expected_revision':case['revision']});assert r.status_code==200;case=r.json()
    answer=client.post(f"/api/cases/{case['case_id']}/investigate",json={'question':'Why is this fee risky?'}).json()
    assert answer['evidence_ids'] and set(answer['evidence_ids'])<={e['id'] for e in case['evidence']}
    assert answer['citations'] and all(c['source_id'] in {s['id'] for s in case['sources']} for c in answer['citations'])
    assert '999' in answer['answer'] and '45000' not in answer['answer']

def test_single_scan_chat_uses_same_organization_as_result():
    r=client.post('/api/analyze/text',json={'input_type':'text','content':'Organization: Bharat Electronics Limited\nPosition: Probationary Engineer'});assert r.status_code==200;scan=r.json()
    answer=client.post('/api/ai/investigate',json={'scan_id':scan['id'],'question':'Is this company genuine?'});assert answer.status_code==200
    assert 'Bharat Electronics Limited' in answer.json()['answer'] and 'None' not in answer.json()['answer']


def test_optional_sender_field_is_a_claim_not_authorization():
    claims=extract_claims('s','Sender email: recruiter@unverified.example','text')
    assert any(c['claim_type']=='sender_email' and c['value']=='recruiter@unverified.example' for c in claims)
    assert all(c['verification_status']=='CLAIMED' for c in claims)
