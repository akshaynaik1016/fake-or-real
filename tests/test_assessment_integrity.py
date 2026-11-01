import asyncio,io,json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.services.assessment_semantics import assessment_for
from app.evaluation.runner import dataset,run_scenario,metrics
client=TestClient(app)

@pytest.mark.parametrize('scenario',dataset()['scenarios'],ids=lambda s:s['id'])
def test_labeled_synthetic_benchmark(scenario):
    with SessionLocal() as db:result=asyncio.run(run_scenario(db,scenario))
    assert result['synthetic'] and result['passed'],[c for c in result['checks'] if not c['passed']]

@pytest.mark.parametrize('scenario_id',['poster-aexon','stipend-fee','stipend-conflict'])
def test_evidence_challenge_uses_persisted_pipeline(scenario_id):
    response=client.post('/api/challenge/run/'+scenario_id)
    assert response.status_code==200,response.text
    result=response.json();assert result['passed']
    stored=client.get('/api/cases/'+result['case']['case_id']).json()
    assert stored['claims']==result['actual']['claims']
    assert stored['assessment']==result['actual']['assessment']
    listed=next(c for c in client.get('/api/cases').json() if c['id']==stored['case_id'])
    assert listed['assessment']['state']==stored['assessment']['state']
    revisions=client.get('/api/cases/'+stored['case_id']+'/revisions').json()
    assert revisions[0]['assessment']['state']==stored['assessment']['state']
    for source in stored['sources']:
        scan=client.get('/api/scans/'+source['scan_id']).json()
        assert scan['investigation']['claims']
        assert all(c['source_id']==scan['id'] for c in scan['investigation']['claims'])
    assert client.post('/api/challenge/run/not-a-scenario').status_code==404

def test_benchmark_metrics_are_separate_and_count_abstained_positives():
    def row(gold,actual,tp=1,fp=0,fn=0):return {'passed':gold==actual,'expected':{'state':gold},'actual':{'assessment':{'state':actual}},'extraction_counts':{'tp':tp,'fp':fp,'fn':fn}}
    r=metrics([row('ELEVATED_CONCERN','ELEVATED_CONCERN'),row('UNDETERMINED','ELEVATED_CONCERN',0,1,1),row('ELEVATED_CONCERN','UNDETERMINED'),row('UNDETERMINED','UNDETERMINED')])
    assert r['concern_detection']=={'tp':1,'fp':1,'fn':1,'tn':1,'precision':.5,'recall':.5,'false_positive_rate':.5,'abstention_rate':.5,'expected_state_match_rate':.5}
    assert r['extraction']['precision']==.75 and r['extraction']['recall']==.75
    assert metrics([])['concern_detection']['precision'] is None

def test_no_automatic_rule_can_promote_an_offer_or_unscoped_claim():
    fake={'id':'x','severity':'verified','origin':'DETERMINISTIC_RULE','verification_status':'INDEPENDENTLY_VERIFIED','verified_claim_id':'claim','verification_scope':'company exists','source':'bundled'}
    assert assessment_for({},[fake])['verification_status']=='UNRESOLVED'
    independent={**fake,'origin':'EXTERNAL_SOURCE'}
    scoped=assessment_for({},[independent],[{'id':'claim'}])
    assert scoped['verification_status']=='INDEPENDENTLY_VERIFIED_CLAIM'
    assert scoped['offer_authenticity']=='UNRESOLVED' and scoped['state']=='UNDETERMINED'
    assert assessment_for({},[{**independent,'verified_claim_id':None}])['verification_status']=='UNRESOLVED'

def test_api_views_share_abstention_and_research_integrity():
    scan=client.post('/api/analyze/text',json={'input_type':'text','content':'AEXON TECH\nINTERNSHIP PROGRAM\nStipend INR 15000 per month.'}).json()
    assert scan['risk_level']=='UNDETERMINED' and scan['trust_score'] is None
    assert scan['investigation']['claimed_organization']=='AEXON TECH'
    assert scan['investigation']['research'][0]['status']=='SEARCH_UNAVAILABLE'
    assert scan['assessment']['offer_authenticity']=='UNRESOLVED'
    assert scan['created_at'].endswith(('+00:00','Z'))
    assert not any(c['status']=='verified' for c in scan['verification_results'])
    assert all(e['source_id']==scan['id'] for e in scan['evidence'])
    fetched=client.get('/api/scans/'+scan['id']).json()
    listed=next(s for s in client.get('/api/scans').json() if s['id']==scan['id'])
    passport=client.get('/api/trust-passport/'+scan['id']).json()
    dash=client.get('/api/dashboard').json()
    recent=next(s for s in dash['recent_scans'] if s['id']==scan['id'])
    for view in [fetched,listed,passport,recent]:
        assert view['risk_level']=='UNDETERMINED' and view['trust_score'] is None
        assert view['assessment']['offer_authenticity']=='UNRESOLVED'
    assert dash['stats']['safe_count']==0
    pdf=client.get('/api/reports/'+scan['id']+'/pdf')
    assert pdf.status_code==200
    from pypdf import PdfReader
    text=' '.join(p.extract_text() for p in PdfReader(io.BytesIO(pdf.content)).pages)
    assert 'UNDETERMINED' in text and '100/100' not in text and 'LOW RISK' not in text
    saved=client.post('/api/reports/'+scan['id']+'/save').json()
    assert saved['report_data']['assessment']['offer_authenticity']=='UNRESOLVED'
    comparison=client.post('/api/compare',json={'scan_id_a':scan['id'],'scan_id_b':scan['id']}).json()
    assert comparison['safer_choice'].startswith('Undetermined')

def test_aexon_native_screenshot_extraction_review_and_provenance():
    from PIL import Image,ImageDraw,ImageFont
    import pytesseract
    # A real native OCR integration test, separate from transcript benchmarks.
    try:pytesseract.get_tesseract_version()
    except Exception:pytest.skip('Native Tesseract unavailable')
    try:font=ImageFont.truetype('/System/Library/Fonts/Supplemental/Arial.ttf',40)
    except OSError:font=ImageFont.load_default(size=40)
    image=Image.new('RGB',(1300,400),'white');draw=ImageDraw.Draw(image)
    for y,line in enumerate(['AEXON TECH','INTERNSHIP PROGRAM','Stipend INR 15000 per month']):draw.text((45,40+y*90),line,font=font,fill='black')
    stream=io.BytesIO();image.save(stream,format='PNG')
    response=client.post('/api/analyze/screenshot/extract',files={'file':('Google_filename.png',stream.getvalue(),'image/png')})
    assert response.status_code==200,response.text
    extracted=response.json();assert 'AEXON TECH' in extracted['extracted_text']
    response=client.post('/api/analyze/screenshot/reviewed',json={'content':extracted['extracted_text'],'review_token':extracted['review_token']})
    assert response.status_code==200,response.text
    result=response.json();assert result['investigation']['claimed_organization']=='AEXON TECH'
    assert result['risk_level']=='UNDETERMINED'
    org=next(c for c in result['investigation']['claims'] if c['claim_type']=='organization')
    assert org['excerpt']=='AEXON TECH' and org['verification_status']=='CLAIMED'


def test_historical_integrity_view_does_not_mutate_original_snapshot():
    from copy import deepcopy
    from app.services.assessment_semantics import integrity_view
    original={'fusion':{'risk_level':'LOW','risk_score':12},'evidence':[],'baseline':{'verification_results':[{'status':'verified'}]}}
    previous=deepcopy(original);view=integrity_view(original)
    assert original==previous
    assert view['fusion']['risk_score'] is None and view['baseline']['verification_results'][0]['status']=='completed'
    assert view['assessment']['offer_authenticity']=='UNRESOLVED'

def test_deterministic_investigator_explains_abstention_without_fake_score():
    from app.services.ai_investigator import answer_investigator_query
    response=answer_investigator_query('Why is this suspicious?',{'risk_level':'UNDETERMINED','trust_score':None,'evidence':[]})
    assert 'unresolved' in response['answer'] and 'None/100' not in response['answer']
