"""A–T synthetic fixtures run through real persisted cases/APIs; no live sites."""
import io,json,uuid
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.services.assessment_semantics import assessment_for
from app.services.ai_investigator import answer_investigator_query
from app.scanners.payment_scanner import analyze_payment_risk
from app.services.case_claims import extract_claims
client=TestClient(app)
DATA={r['id']:r for r in json.loads((Path(__file__).parent/'fixtures/final_demo_synthetic.json').read_text())['records']}

def create(title='Synthetic readiness investigation'):
 r=client.post('/api/cases',json={'title':title});assert r.status_code==200,r.text;return r.json()
def add(case,text,kind='text'):
 r=client.post(f"/api/cases/{case['case_id']}/sources",json={'input_type':kind,'content':text,'expected_revision':case['revision']});assert r.status_code==200,r.text;return r.json()
def content(letter):return DATA[letter]['text']
def values(case,kind):return [c['value'] for c in case['claims'] if c['claim_type']==kind]

@pytest.mark.parametrize('letter',list('ABCDEFQR'))
def test_a_f_q_r_persisted_scenarios(letter):
 case=add(create(),content(letter));a=case['assessment'];signal=a['risk_indicators']['state']
 assert a['offer_authenticity']=='UNRESOLVED' and not a['verified_claims']
 if letter in {'A','C'}:
  assert signal=='ELEVATED_CONCERN' and a['state']=='ELEVATED_CONCERN'
  assert values(case,'fee') and values(case,'compensation') and values(case,'urgency')
  assert not any(c['value']['value'] in {'45000','60000'} for c in case['claims'] if c['claim_type']=='fee')
 if letter in {'B','Q'}:
  assert signal=='NO_SIGNIFICANT_CONCERNS_OBSERVED' and a['authenticity']['state']=='UNVERIFIED'
  assert a['state']=='UNDETERMINED' and a['risk_score'] is None and case['fusion']['confidence']==0
  assert not [e for e in case['evidence'] if e['category']=='payment_risk']
  assert a['coverage']['total']>0 and a['processing']['processed']==1
 if letter=='D':
  assert a['state']=='UNDETERMINED'
  assert {v['value'] for v in values(case,'fee')}=={'1000','1180'}
  assert values(case,'tax_component')[0]['value']=='180' and values(case,'contractual_penalty')[0]['value']=='200000'
  assert values(case,'fee_exemption') and not any(f['classification']=='CONFIRMED_CONTRADICTION' for f in case['cross_source_findings'])
 if letter=='E':
  assert values(case,'organization')==['SkillBridge Academy']
  assert set(values(case,'claimed_collaborator'))=={'Microsoft','IBM','Wipro','Infosys'}
  assert not values(case,'fee') and values(case,'fee_policy_disclosure')[0]['amount'] is None
  assert a['state']=='UNDETERMINED'
 if letter=='F':
  case=add(case,DATA['F']['second_text'])
  kinds={f['kind'] for f in case['cross_source_findings']}
  assert {'COMPENSATION_CONFLICT','FEE_INSTRUCTION_CONFLICT','INTERVIEW_PROCESS_CONFLICT'}<=kinds
  for f in case['cross_source_findings']:
   if f['kind'].endswith('CONFLICT'):assert len({r['source_id'] for r in f['citations']})==2
 if letter=='R':
  assert values(case,'compensation')[0]['value']=='25000'
  assert values(case,'fee')[0]['value']=='1500' and values(case,'contractual_penalty')[0]['value']=='200000'


def pdf(text=None):
 from reportlab.pdfgen.canvas import Canvas
 b=io.BytesIO();p=Canvas(b)
 for i,line in enumerate((text or content('B')).splitlines()):p.drawString(30,750-i*22,line[:110])
 p.save();return b.getvalue()
def png():
 from PIL import Image,ImageDraw,ImageFont
 image=Image.new('RGB',(1200,600),'white');d=ImageDraw.Draw(image);font=ImageFont.load_default(size=24)
 for i,line in enumerate(content('B').splitlines()):
  # OCR is controlled in matrix tests; native recognition is covered separately.
  d.text((20,20+i*35),line[:90],fill='black',font=font)
 b=io.BytesIO();image.save(b,format='PNG');return b.getvalue()
def batch(case,include_url=False,images=0,include_pdf=False,sender=False):
 sources=[{'input_type':'text','content':content('B')+('\nSender email: hr@brightpath.example' if sender else '')}]
 if include_url:sources.append({'input_type':'url','content':'https://brightpath.example/internship'})
 files=[('files',('synthetic-notice.pdf',pdf(),'application/pdf'))] if include_pdf else []
 files.extend(('files',(f'synthetic-{i}.png',png(),'image/png')) for i in range(images))
 return client.post(f"/api/cases/{case['case_id']}/sources/batch",data={'payload':json.dumps({'expected_revision':case['revision'],'sources':sources})},files=files)
def review(case):
 for s in list(case['sources']):
  if s['processing_status']=='NEEDS_REVIEW':
   r=client.post(f"/api/cases/{case['case_id']}/sources/{s['id']}/review",json={'content':s['extracted_text'],'expected_revision':case['revision']});assert r.status_code==200,r.text;case=r.json()
 return case
@pytest.mark.parametrize('letter',list('GHIJKLM'))
def test_g_m_multisource_pipeline(letter,monkeypatch):
 import pytesseract
 from app.services import case_url_fetcher as fetcher
 monkeypatch.setattr(pytesseract,'image_to_string',lambda *a,**k:content('B'))
 monkeypatch.setattr(settings,'CASE_URL_FETCH_ENABLED',True)
 async def fetch(*a,**k):
  if letter=='K':raise fetcher.URLFetchError('URL_TIMEOUT','Synthetic provider timeout')
  return {'text':content('B'),'final_url':'https://brightpath.example/internship','redirect_chain':['https://brightpath.example/internship'],'content_type':'text/plain','truncated':False}
 monkeypatch.setattr(fetcher,'fetch_public_text',fetch)
 case=create();r=batch(case,letter in 'HJK',6 if letter=='L' else 5 if letter in 'IJ' else 2 if letter=='M' else 0,letter in 'IJK',letter=='J')
 if letter=='L':
  assert r.status_code==422 and '5' in r.text
  assert not client.get('/api/cases/'+case['case_id']).json()['sources'];return
 assert r.status_code==200,r.text;case=review(r.json())
 expected={'G':1,'H':2,'I':7,'J':8,'K':3,'M':3}[letter]
 assert len(case['sources'])==expected and len({s['case_id'] for s in case['sources']})==1
 assert sum(s['processing_status']=='FAILED' for s in case['sources'])==(1 if letter=='K' else 0)
 assert case['assessment']['offer_authenticity']=='UNRESOLVED'
 if letter in 'IJM':assert case['duplicate_sources'] and not case['assessment']['verified_claims']
 if letter=='M':
  one=add(create(),content('B'))
  assert case['fusion']['confidence']==one['fusion']['confidence']==0

QUESTIONS=['Is this internship genuine?','Why is it suspicious?','What evidence is missing?','Is the company real?','Are training fees always fraudulent?','What should I verify before paying?','What is the difference between low concern and verified?','Which sources contradict each other?']
def test_n_all_eight_investigator_questions():
 case=add(add(create(),content('F')),DATA['F']['second_text'])
 for question in QUESTIONS:
  r=client.post(f"/api/cases/{case['case_id']}/investigate",json={'question':question});assert r.status_code==200,r.text;a=r.json()
  assert 'BluePeak Technologies' in a['answer'] and 'None' not in a['answer']
  assert a['context_revision']==case['revision'] and 'Authenticity:' in a['answer']
  assert set(a['evidence_ids'])<={e['id'] for e in case['evidence']}
  assert all(c['source_id'] in {s['id'] for s in case['sources']} for c in a['citations'])
  if 'contradict' in question:assert len({c['source_id'] for c in a['citations']})==2

def test_o_twenty_evidence_graph_and_all_citations():
 demands='\n'.join(f'Pay registration fee INR {1000+i} to account: RECIPIENT{i} immediately.' for i in range(22))
 case=add(create(),'SYNTHETIC STRESS TEST, NOT A REAL OFFER\nOrganization: Synthetic Stress Labs\nInternship.\n'+demands)
 assert len(case['evidence'])>=20 and len(case['graph']['nodes'])>=20
 assert not any(e['relationship_status']=='VERIFIED' for e in case['graph']['edges'])

def test_p_exact_document_unavailable_is_not_performed(monkeypatch):
 monkeypatch.setattr(settings,'CASE_URL_FETCH_ENABLED',False);monkeypatch.setattr(settings,'OFFICIAL_NOTICE_FETCH_ENABLED',False)
 case=add(create(),'SYNTHETIC BEL-STYLE TEST\nOrganization: Bharat Electronics Limited\nAdvertisement number: BEL/TEST/2026\nPosition: Engineer')
 a=next(a for a in case['recommendations'] if a['action_id']=='verify_notice')
 assert a['status']=='UNAVAILABLE' and not case['notice_review']['independent_documents']
 assert case['assessment']['authenticity']['state']=='VERIFICATION_UNAVAILABLE' and not case['assessment']['authenticity']['performed']


def test_s_existing_bel_style_fixture_and_reports():
 from pypdf import PdfReader
 fixture=(Path(__file__).parent/'fixtures/bel_context_synthetic.txt').read_text()
 case=add(create(),fixture)
 assert values(case,'advertisement_number') and values(case,'fee_exemption')
 r=client.get(f"/api/cases/{case['case_id']}/report/pdf");assert r.status_code==200
 text='\n'.join(p.extract_text() for p in PdfReader(io.BytesIO(r.content)).pages)
 assert 'AUTHENTICITY:' in text and 'OBSERVED RISK SIGNALS:' in text
 assert 'Risk index: Not scored' in text and 'Risk score: None' not in text
 assert 'No case-level checklist recorded' in ' '.join(text.split()) and '9-POINT AUDIT' not in text


def test_t_existing_feature_routes_and_historical_revision_compatibility():
 paths=app.openapi()['paths']
 for p in ['/api/analyze/text','/api/analyze/url','/api/analyze/pdf','/api/analyze/screenshot','/api/cases','/api/dashboard','/api/scans','/api/compare','/api/community/reports','/api/ai/investigate','/api/emergency/analyze','/api/reports/{scan_id}/pdf','/api/trust-passport/{scan_id}']:assert p in paths
 case=add(create(),content('B'));old_revision=case['revision'];case=add(case,content('A'))
 old=client.get(f"/api/cases/{case['case_id']}/revisions/{old_revision}").json()
 assert old['assessment']['state']=='UNDETERMINED' and old['assessment']['risk_indicators']['state']=='NO_SIGNIFICANT_CONCERNS_OBSERVED'
 assert case['assessment']['state']=='ELEVATED_CONCERN'


def test_positive_no_fee_wording_does_not_increase_confidence():
 a=add(create(),content('B'));b=add(create(),content('B').replace('No application, registration or training fee. No payment required.',''))
 assert a['fusion']['confidence']==b['fusion']['confidence']==0
 assert a['assessment']['processing']['processed']==1

def test_dashboard_counts_case_once_after_additions_and_corrections(monkeypatch):
 import pytesseract
 monkeypatch.setattr(pytesseract,'image_to_string',lambda *a,**k:content('B'))
 before=client.get('/api/dashboard').json()['investigation_stats']['opportunities_checked']
 case=create();assert client.get('/api/dashboard').json()['investigation_stats']['opportunities_checked']==before
 case=add(case,content('B'));case=add(case,content('E'))
 r=client.post(f"/api/cases/{case['case_id']}/sources/upload",data={'input_type':'screenshot','expected_revision':case['revision']},files={'file':('synthetic.png',png(),'image/png')});assert r.status_code==200;case=review(r.json())
 source=case['sources'][-1]
 r=client.post(f"/api/cases/{case['case_id']}/sources/{source['id']}/review",json={'content':source['extracted_text']+'\nAdditional submitted claim.','expected_revision':case['revision']});assert r.status_code==200
 after=client.get('/api/dashboard').json()
 assert after['investigation_stats']['opportunities_checked']==before+1
 assert after['stats']['opportunities_checked']>=after['investigation_stats']['opportunities_checked']

def test_sparse_or_url_only_evidence_does_not_get_reassuring_signal_label():
 for text,kind in [('Hello','text'),('https://unknown.example','url')]:
  case=add(create(),text,kind)
  assert case['assessment']['risk_indicators']['state']=='INSUFFICIENT_EVIDENCE_TO_ASSESS'


def test_tax_wording_never_reassigns_known_compensation():
 text='Stipend INR 1000 plus GST INR 180, total application fee INR 1180.'
 amounts=analyze_payment_risk(text)['monetary_entities']
 assert next(e for e in amounts if e['value']=='1000')['role']=='COMPENSATION'


def test_demo_reference_does_not_assert_a_genuine_offer():
 cases=client.get('/api/demo/cases').json();assert all(c['synthetic'] for c in cases)
 reference=next(c for c in cases if c['id']=='demo-genuine-tcs-opportunity')
 assert reference['expected_risk']=='UNDETERMINED' and 'Synthetic' in reference['title']
 assert 'Authentic enterprise' not in reference['description']


@pytest.mark.parametrize('text,detected',[
 ('No registration fee,\nsecurity deposit,\nor training fee is required.',False),
 ('No registration fee.\nPay security deposit INR 999.',True),
 ('No registration fee\nTraining fee INR 1500 applies.',True),
])
def test_wrapped_fee_negation_does_not_leak_into_new_demands(text,detected):
 assert analyze_payment_risk(text)['payment_detected']==detected
