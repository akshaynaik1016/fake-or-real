"""Role and fee regressions use labelled synthetic examples, not company verification."""
from pathlib import Path
import io,uuid
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.scanners.org_scanner import identify_claimed_organization,organization_role_mentions
from app.scanners.payment_scanner import analyze_payment_risk
from app.services.case_claims import extract_claims
from app.core.config import settings
client=TestClient(app)
TEXT=(Path(__file__).parent/'fixtures/corizo_role_synthetic.txt').read_text()

def submit(text=TEXT):
 r=client.post('/api/analyze/text',json={'input_type':'text','content':text});assert r.status_code==200,r.text;return r.json()

def test_a_corizo_primary_partners_and_exact_claims():
 result=submit();s=result['investigation']
 assert s['claimed_organization']=='Corizo'
 assert {e['value'] for e in s['entities'] if e['type']=='domain'}=={'corizo.in'}
 assert not any('Microsoft' in e['evidence'] and 'mismatch' in e['evidence'].lower() for e in s['evidence'])
 assert not any(e['category']=='organization_verification' and 'does not match' in e['evidence'] for e in s['evidence'])
 values=lambda kind:[c['value'] for c in s['claims'] if c['claim_type']==kind]
 assert values('organization')==['Corizo']
 assert set(values('claimed_collaborator'))=={'IBM','Microsoft','Deloitte','Wipro','Cognizant','Barclays','Infosys','Genpact','Oracle'}
 assert values('opportunity_type')==['Training + Internship']
 assert values('duration_range')==[{'minimum':2,'maximum':3,'unit':'month'}]
 assert any('Wipro Dice ID' in v for v in values('certificate_association'))
 assert not any(v.get('role')=='CLAIMED_CERTIFICATE_ISSUER' for v in values('organization_role'))
 assert values('placement_promise')[0]['scope']=='PLACEMENT_ASSISTANCE' and values('placement_promise')[0]['job_guaranteed'] is None
 assert values('fee_policy_disclosure')[0]['amount'] is None
 assert s['assessment']['offer_authenticity']=='UNRESOLVED' and not s['assessment']['verified_claims']
 assert s['assessment']['state']=='UNDETERMINED' and not any(e['severity']=='critical' for e in s['evidence'])
 assert not any(c['status']=='failed' for c in result['verification_results'])
 for c in s['claims']:assert result['input_content'][c['location']['start']:c['location']['end']]==c['excerpt']
 for name in ['Exact training fee','Payment recipient','Refund policy','partnerships','certificate','placement assistance']:
  assert any(name.lower() in u.lower() for u in s['notice_review']['unknowns'])
 labels=' '.join(n['label'] for n in s['graph']['nodes'])
 for expected in ['Corizo','Training + Internship','corizo.in','Training Fee','Claimed Partnerships','Unresolved Verification']:assert expected in labels
 assert not any(e['relationship_status']=='VERIFIED' for e in s['graph']['edges'])

@pytest.mark.parametrize('company,domain',[('Microsoft','careers.microsoft.com'),('Google','careers.google.com')])
def test_b_direct_employer_stays_primary(company,domain):
 scan=submit(f'{company} internship. Website: https://{domain}')
 assert company in scan['investigation']['claimed_organization']
 assert scan['assessment']['offer_authenticity']=='UNRESOLVED'

@pytest.mark.parametrize('name',['SkillBridge Academy','Orbit Learning','Future Path Labs'])
def test_c_unknown_provider_generalizes_without_registry_entry(name):
 text=f'Greetings from {name}!!!!\nPartners: Microsoft, Wipro\nTraining and Internship program.\nTRAINING FEES ARE APPLICABLE\nhttps://provider.example'
 org=identify_claimed_organization(text);assert org['canonical_name']==name
 assert {r['display_name'] for r in organization_role_mentions(text) if r['role']=='CLAIMED_COLLABORATOR'}=={'Microsoft','Wipro'}
 assert not analyze_payment_risk(text)['elevated_payment_concern']

def test_partner_domain_is_not_compared_as_primary_ownership():
 scan=submit('Organization: Google\nPartners: Microsoft\nTraining and Internship.\nPartner website: https://careers.microsoft.com')
 assert scan['investigation']['claimed_organization']=='Google LLC / Alphabet Inc.'
 assert not any('does not match analyzed domain' in e['evidence'] for e in scan['evidence'])
 assert next(c for c in scan['verification_results'] if c['check_name']=='Organization')['status']=='warning'

def test_partner_only_message_does_not_invent_a_primary():
 assert identify_claimed_organization('Partners: Microsoft, Wipro\nTraining program.') is None

@pytest.mark.parametrize('fee',['TRAINING FEES ARE APPLICABLE','Training fee INR 5000.','The training fee is Rs. 5000.'])
def test_training_disclosure_is_unresolved_not_critical(fee):
 result=analyze_payment_risk(fee)
 assert result['payment_detected'] and not result['elevated_payment_concern']
 assert all(f['severity']=='moderate' for f in result['flags'])
 if 'APPLICABLE' in fee:assert not result['payment_amounts']

@pytest.mark.parametrize('demand',['Pay training fee INR 999 to my personal account.','Pay training fee INR 999 immediately before the interview.','Training fees are applicable. Pay to my personal UPI account now.'])
def test_strong_training_payment_warnings_are_preserved(demand):
 result=analyze_payment_risk(demand)
 assert result['elevated_payment_concern'] and any(f['severity']=='critical' for f in result['flags'])

def test_d_compensation_training_fee_and_registration_remain_separate():
 scan=submit('Greetings from Orbit Learning!\nStipend INR 45000 per month. Training fee INR 5000. Pay registration fee INR 999 to my personal account.')
 money=scan['investigation']['monetary_entities']
 assert any(m['value']=='45000' and m['role']=='COMPENSATION' for m in money)
 assert any(m['value']=='5000' and m['category']=='TRAINING_FEE' for m in money)
 assert any(m['value']=='999' and m['category']=='REGISTRATION_FEE' for m in money)
 assert not any('45000' in e['evidence'] for e in scan['evidence'] if e['category']=='payment_risk')

@pytest.mark.parametrize('text,scope',[('Placement Assistance (100% Guarantee)','PLACEMENT_ASSISTANCE'),('Guaranteed job placement','JOB_PLACEMENT')])
def test_placement_promises_keep_their_actual_scope(text,scope):
 claims=extract_claims('source',text,'text')
 assert next(c for c in claims if c['claim_type']=='placement_promise')['value']['scope']==scope


def test_n_chat_result_and_reports_share_primary_not_partner():
 from pypdf import PdfReader
 scan=submit();answer=client.post('/api/ai/investigate',json={'scan_id':scan['id'],'question':'Is this company genuine?'}).json()
 assert 'Claimed organization: Corizo' in answer['answer'] and 'Claimed collaborators:' in answer['answer']
 assert 'None' not in answer['answer']
 question=client.post('/api/ai/investigate',json={'scan_id':scan['id'],'question':'Are these partnerships and certificates genuine?'}).json()
 assert 'not been authenticated' in question['answer'] and question['citations']
 r=client.get(f"/api/reports/{scan['id']}/pdf");assert r.status_code==200
 text='\n'.join(p.extract_text() for p in PdfReader(io.BytesIO(r.content)).pages)
 assert 'Corizo' in text and 'Microsoft Corporation does not match' not in text and 'Disclosed training fee' in text
 assert client.get('/api/scans/'+scan['id']).json()['investigation']['claimed_organization']=='Corizo'


def test_dashboard_categories_are_stored_report_counts_with_explicit_scope():
 category='synthetic-regression-'+uuid.uuid4().hex
 for i in range(2):
  r=client.post('/api/community/reports',json={'scam_category':category,'organization_name':'Synthetic fixture','description':('[Synthetic demo report] ' if i else '')+'Not a confirmed incident','evidence_text':'Synthetic test report','upvotes':25});assert r.status_code==200,r.text
 dashboard=client.get('/api/dashboard').json()
 bar=next(b for b in dashboard['charts']['category_distribution'] if b['category']==category)
 assert bar['count']==2 and bar['synthetic_count']==1 and bar['submitted_count']==1
 assert 'not confirmed incidents' in dashboard['data_scope']['reports']
 assert sum(b['count'] for b in dashboard['charts']['category_distribution'])==dashboard['stats']['reports_submitted']


def test_context_roles_do_not_create_false_organization_conflicts_in_cases():
 case=client.post('/api/cases',json={'title':'Synthetic provider investigation'}).json()
 for text in [TEXT,'Greetings from Corizo!!!!\nPartners: Microsoft\nTraining and Internship program.']:
  r=client.post(f"/api/cases/{case['case_id']}/sources",json={'input_type':'text','content':text,'expected_revision':case['revision']});assert r.status_code==200;case=r.json()
 assert {c['value'] for c in case['claims'] if c['claim_type']=='organization'}=={'Corizo'}
 assert not any(f['kind']=='ORGANIZATION_CONFLICT' for f in case['cross_source_findings'])
 assert len([f for f in case['cross_source_findings'] if f['kind']=='CLAIM_CONTEXT'])<=2
 assert case['assessment']['offer_authenticity']=='UNRESOLVED'
 r=client.post(f"/api/cases/{case['case_id']}/investigate",json={'question':'Is this company genuine?'});assert 'Claimed organization: Corizo' in r.json()['answer']


@pytest.mark.parametrize('with_url,fail_url',[(False,False),(True,False),(True,True)])
def test_h_i_j_all_optional_files_and_five_images(with_url,fail_url,monkeypatch):
 import pytesseract
 from test_reliable_workspace import create,batch,review_all,POSTER
 from app.services import case_url_fetcher as fetcher
 monkeypatch.setattr(pytesseract,'image_to_string',lambda *a,**k:POSTER)
 if fail_url:
  monkeypatch.setattr(settings,'CASE_URL_FETCH_ENABLED',True)
  async def unavailable(*a,**k):raise fetcher.URLFetchError('URL_TIMEOUT','Synthetic unavailable URL')
  monkeypatch.setattr(fetcher,'fetch_public_text',unavailable)
 kinds=('text','pdf','screenshot')+(('url',) if with_url else ())
 r=batch(create(),kinds,5);assert r.status_code==200,r.text;case=review_all(r.json())
 assert len(case['sources'])==7+int(with_url)
 assert sum(s['input_type']=='screenshot' for s in case['sources'])==5
 assert sum(s['processing_status']=='FAILED' for s in case['sources'])==int(fail_url)
 assert sum(s['processing_status']=='READY' for s in case['sources'])==len(case['sources'])-int(fail_url)
 assert len(case['duplicate_sources'])>=4
 assert case['assessment']['offer_authenticity']=='UNRESOLVED'
 if fail_url:assert any(s['error_code']=='URL_TIMEOUT' for s in case['sources'])


def test_all_distinct_roles_remain_claimed_and_do_not_change_primary():
 text='Organization: Orbit Academy\nEmployer: Microsoft\nTraining provider: Orbit Academy\nPartners: Wipro\nCertificate issuer: Acme Certificates\nRecruiter: Priya Shah\nDomain owner: Website Services\nPayment recipient: Example Payments'
 roles=organization_role_mentions(text)
 assert identify_claimed_organization(text)['canonical_name']=='Orbit Academy'
 assert {r['role'] for r in roles}>={'PRIMARY_ORGANIZER','CLAIMED_EMPLOYER','CLAIMED_TRAINING_PROVIDER','CLAIMED_COLLABORATOR','CLAIMED_CERTIFICATE_ISSUER','CLAIMED_DOMAIN_OWNER','PAYMENT_RECIPIENT'}
 assert all(r['verification_status']=='CLAIMED' for r in roles)
 claims=extract_claims('s',text,'text');assert any(c['claim_type']=='recruiter_name' for c in claims)


def test_excerpt_without_duration_or_certificate_does_not_infer_missing_fields():
 text='Greetings from New Academy!!!!\nWe collaborate with Companies [Microsoft, Wipro].\nTraining and Internship program. TRAINING FEES ARE APPLICABLE. https://academy.example'
 claims=extract_claims('s',text,'text')
 assert not any(c['claim_type'] in {'duration_range','certificate_association','placement_promise'} for c in claims)
 assert not any(c['claim_type']=='fee' for c in claims)
