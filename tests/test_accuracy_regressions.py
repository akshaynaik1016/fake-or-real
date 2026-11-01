import asyncio
from copy import deepcopy
import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.scanners.payment_scanner import analyze_payment_risk

client = TestClient(app)
OFFER = '''Congratulations! You have been selected for a software engineering internship at Microsoft.

Your stipend will be ₹45,000 per month.

To confirm your position, pay a refundable registration fee of ₹999 to our recruitment coordinator.

Complete payment within 2 hours.

Send your Aadhaar card and PAN card immediately.

Recruitment email: hr@microsoft-internship-verification.example'''


def test_reported_stipend_fee_bug():
    result = analyze_payment_risk(OFFER)
    assert [e['value'] for e in result['payment_amounts']] == ['999']
    assert [(e['value'],e['category'],e['period']) for e in result['compensation_amounts']] == [('45000','STIPEND','month')]
    assert result['detected_amounts'] == ['999']
    payment_text = ' '.join(f['message'] for f in result['flags'])
    assert '₹999' in payment_text and '45,000' not in payment_text
    for entity in result['monetary_entities']:
        assert OFFER[entity['start']:entity['end']] == entity['raw']
        assert OFFER[entity['label_start']:entity['label_end']] == entity['label']


@pytest.mark.parametrize('currency', ['₹', 'Rs. ', 'INR '])
@pytest.mark.parametrize('template', [
    'Stipend {c}45,000 per month. Registration fee {c}999.',
    'Registration fee {c}999. Stipend {c}45,000 per month.',
    'Stipend {c}45,000 per month; registration fee {c}999.',
    'Stipend {c}45,000 per month, pay registration fee {c}999.',
    'Stipend {c}45,000 per month and registration fee {c}999.',
    '{c}999 registration fee; {c}45,000 monthly stipend.',
    'Stipend {c}45,000 registration fee {c}999.',
])
def test_amount_order_and_currency_context(currency, template):
    text = template.format(c=currency)
    r = analyze_payment_risk(text)
    assert [e['value'] for e in r['payment_amounts']] == ['999']
    assert [e['value'] for e in r['compensation_amounts']] == ['45000']
    assert all(text[e['start']:e['end']] == e['raw'] for e in r['monetary_entities'])


@pytest.mark.parametrize('label,category', [('registration fee','REGISTRATION_FEE'),
    ('security deposit','SECURITY_DEPOSIT'), ('refundable deposit','REFUNDABLE_DEPOSIT'),
    ('processing fee','PROCESSING_FEE'),('training fee','TRAINING_FEE')])
def test_fee_categories(label, category):
    r = analyze_payment_risk(f'Stipend ₹45,000. Pay {label} of ₹999.')
    assert [(e['value'],e['category']) for e in r['payment_amounts']] == [('999',category)]


@pytest.mark.parametrize('label,category', [('salary','SALARY'),('stipend','STIPEND'),
    ('scholarship','SCHOLARSHIP'),('bonus','OTHER_COMPENSATION'),('allowance','OTHER_COMPENSATION')])
def test_compensation_is_not_payment(label, category):
    r = analyze_payment_risk(f'Your {label} is INR 1,50,000 per year.')
    assert not r['payment_detected']
    assert r['compensation_amounts'][0]['value'] == '150000'
    assert r['compensation_amounts'][0]['category'] == category


@pytest.mark.parametrize('text', ['Fee ₹999 or ₹1499.', '₹999. Registration fee required.',
    '₹45000 and ₹999. Pay a fee.', 'Amounts ₹999 and ₹45000.', 'Salary or fee ₹999.', 'Fee ₹999 or 1499.', 'Fee ₹999–1499.'])
def test_ambiguous_amounts_do_not_get_guessed(text):
    r = analyze_payment_risk(text)
    assert not r['payment_amounts']
    assert not r['detected_amounts']
    assert not any('₹999' in f['message'] or '₹45000' in f['message'] for f in r['flags'])


def test_multiple_distinct_fees_have_distinct_spans():
    text='Salary ₹45,000. Registration fee ₹999; training fee INR 2500; refundable deposit Rs. 499.'
    r=analyze_payment_risk(text)
    assert [e['value'] for e in r['payment_amounts']] == ['999','2500','499']
    assert [e['value'] for e in r['compensation_amounts']] == ['45000']
    for f in r['flags']:
        for span in f['source_spans']:
            assert text[span['start']:span['end']] == span['text']


def image_bytes():
    from PIL import Image
    stream=io.BytesIO(); Image.new('RGB',(320,80),'white').save(stream,format='PNG'); return stream.getvalue()


def mock_ocr(monkeypatch,text):
    import pytesseract
    monkeypatch.setattr(pytesseract,'image_to_string',lambda *args,**kwargs:text)


def extract(client,filename='Google_filename_is_not_identity.png'):
    response=client.post('/api/analyze/screenshot/extract',files={'file':(filename,image_bytes(),'image/png')})
    assert response.status_code==200,response.text
    return response.json()


def test_fee_evidence_retains_only_correct_payment_spans_through_api():
    response=client.post('/api/analyze/text',json={'input_type':'text','content':OFFER})
    assert response.status_code==200,response.text
    state=response.json()['investigation']
    assert state['monetary_entities'][0]['category']=='STIPEND'
    fees=[e for e in state['evidence'] if e['category']=='payment_risk']
    assert fees and all('45,000' not in e['evidence'] and '45,000' not in e['observed_value'] for e in fees)
    for evidence in fees:
        for span in evidence['source_spans']:
            assert response.json()['input_content'][span['start']:span['end']]==span['text']


def test_checklist_all_execution_states_and_summary():
    from app.services.verification_service import verification_summary
    checks=[{'status':'failed'}]+[{'status':s} for s in ['warning','unavailable','not_performed','unavailable','not_performed','warning','unavailable','not_performed']]
    summary=verification_summary(checks)
    assert summary['text']=='1 failed · 8 unresolved · 0 verified'
    assert summary['unavailable']==3 and summary['not_performed']==3
    assert verification_summary([])['failed']==0
    assert verification_summary([{'status':'passed'}])['verified']==1


def test_unavailable_checks_are_not_failures_in_real_scan():
    result=client.post('/api/analyze/text',json={'input_type':'text','content':'Please see https://example.com for the role.'}).json()
    checks={c['check_name']:c for c in result['verification_results']}
    assert checks['Domain']['status']=='unavailable'
    assert checks['SSL']['status']=='unavailable'
    assert checks['Threat Intelligence']['status']=='unavailable'
    assert checks['Document']['status']=='not_performed'
    assert checks['Phone']['status']=='not_performed'
    assert checks['Payment']['status']=='verified'


def test_graph_relationship_states_and_unique_source_edges():
    from app.services.trust_graph_service import build_trust_graph
    entities=[{'id':'org','type':'organization','value':'Microsoft','provenance':'Submitted claim'},
              {'id':'email','type':'email','value':'hr@example.com','provenance':'Submitted email'}]
    ev={'id':'ref','category':'identity_match','severity':'high','evidence':'Reference mismatch','source':'Reference',
        'origin':'DETERMINISTIC_RULE','verification_status':'REFERENCE_MISMATCH','related_entities':['email']}
    source={'id':'src','title':'Search result','url':'https://example.com','verification_status':'NOT_INDEPENDENTLY_VERIFIED'}
    graph=build_trust_graph(entities,[ev],[{'sources':[source]},{'sources':[source]}])
    assert len([e for e in graph['edges'] if e['target']=='src'])==1
    assert {e['relationship_status'] for e in graph['edges']} >= {'CLAIMED','OBSERVED','CONTRADICTED','UNRESOLVED'}
    ev.update(id='match',severity='verified',verification_status='REFERENCE_MATCH')
    assert any(e['relationship_status']=='VERIFIED' for e in build_trust_graph(entities,[ev],[])['edges'])
    assert graph==build_trust_graph(entities,[{**ev,'id':'ref','severity':'high','verification_status':'REFERENCE_MISMATCH'}],[{'sources':[source]},{'sources':[source]}])


def test_extract_preview_does_not_run_scanners_and_does_not_use_filename(monkeypatch):
    mock_ocr(monkeypatch,'Microsoft internship stipend ₹45,000/month. Registration fee ₹999.')
    import app.api.v1.endpoints.analyze as analyze
    async def forbidden(*args,**kwargs): raise AssertionError('Preview must not run forensic scanners')
    monkeypatch.setattr(analyze,'execute_full_scan',forbidden)
    result=extract(client)
    assert result['status']=='SUCCESS' and '₹999' in result['extracted_text']
    assert result['filename']=='Google_filename_is_not_identity.png'
    assert result['review_token']


def test_corrected_ocr_text_passes_to_actual_scanners(monkeypatch):
    mock_ocr(monkeypatch,'Microsoft internship. Registration fee ₹45,000.')
    preview=extract(client)
    corrected='Microsoft internship. Stipend ₹45,000/month. Registration fee ₹999.'
    result=client.post('/api/analyze/screenshot/reviewed',json={'content':corrected,'review_token':preview['review_token']})
    assert result.status_code==200,result.text
    detail=result.json(); state=detail['investigation']
    assert detail['input_type']=='screenshot' and detail['input_content']==corrected
    assert state['claimed_organization']=='Microsoft Corporation'
    assert state['document_extraction']['user_corrected'] is True
    assert state['document_extraction']['filename']=='Google_filename_is_not_identity.png'
    assert [e['value'] for e in state['monetary_entities'] if e['role']=='PAYMENT']==['999']
    assert all('Google_filename' not in e['evidence'] for e in state['evidence'])


def test_direct_screenshot_api_preserves_compatibility_and_ignores_filename(monkeypatch):
    mock_ocr(monkeypatch,'Microsoft internship. Pay registration fee ₹999.')
    response=client.post('/api/analyze/screenshot',files={'file':('Google-offer.png',image_bytes(),'image/png')})
    assert response.status_code==200,response.text
    state=response.json()['investigation']
    assert state['claimed_organization']=='Microsoft Corporation'
    assert state['document_extraction']['reviewed'] is False


def test_empty_ocr_is_not_an_engine_error_and_can_be_manually_corrected(monkeypatch):
    mock_ocr(monkeypatch,'  \n')
    preview=extract(client)
    assert preview['status']=='EMPTY' and preview['error_code']=='OCR_NO_TEXT'
    assert preview['extracted_text']==''
    direct=client.post('/api/analyze/screenshot',files={'file':('blank.png',image_bytes(),'image/png')})
    assert direct.status_code==422 and direct.json()['detail']['stage']=='ocr'
    response=client.post('/api/analyze/screenshot/reviewed',json={'content':'Microsoft role. Pay ₹999 registration fee.','review_token':preview['review_token']})
    assert response.status_code==200,response.text
    assert response.json()['investigation']['document_extraction']['ocr_status']=='EMPTY'


def test_ocr_missing_engine_has_specific_error(monkeypatch):
    import pytesseract
    def missing(*args,**kwargs): raise pytesseract.TesseractNotFoundError()
    monkeypatch.setattr(pytesseract,'image_to_string',missing)
    preview=extract(client)
    assert preview['status']=='UNAVAILABLE' and preview['error_code']=='OCR_ENGINE_MISSING'
    assert not preview['extracted_text']


def test_scanner_error_is_distinct_from_ocr_error(monkeypatch):
    mock_ocr(monkeypatch,'Microsoft role with ₹999 registration fee.')
    preview=extract(client)
    import app.api.v1.endpoints.analyze as analyze
    async def failed(*args,**kwargs): raise RuntimeError('internal provider key must never leak')
    monkeypatch.setattr(analyze,'execute_full_scan',failed)
    result=client.post('/api/analyze/screenshot/reviewed',json={'content':preview['extracted_text'],'review_token':preview['review_token']})
    assert result.status_code==500 and result.json()['detail']['stage']=='forensics'
    assert result.json()['detail']['code']=='SCANNER_ERROR'
    assert 'internal provider key' not in result.text


def test_invalid_review_token_and_empty_corrected_text_rejected(monkeypatch):
    mock_ocr(monkeypatch,'Role text.')
    preview=extract(client)
    assert client.post('/api/analyze/screenshot/reviewed',json={'content':'text','review_token':'forged-token-value'}).status_code==422
    assert client.post('/api/analyze/screenshot/reviewed',json={'content':'   ','review_token':preview['review_token']}).status_code==422


def test_next_check_unavailable_reason_and_duplicate_prevention():
    result=client.post('/api/analyze/text',json={'input_type':'text','content':OFFER}).json()
    sid=result['id']; initial=result['investigation']; original_ids={e['id'] for e in initial['evidence']}
    research=next(a for a in initial['recommendations'] if a['action_id']=='research_warnings')
    assert research['status']=='UNAVAILABLE' and 'TAVILY_API_KEY' in research['unavailable_reason']
    unavailable=client.post(f'/api/investigations/{sid}/actions/research_warnings',json={'expected_revision':1})
    assert unavailable.status_code==409 and 'TAVILY_API_KEY' in unavailable.json()['detail']
    path=f'/api/investigations/{sid}/actions/verify_sender_domain'
    updated=client.post(path,json={'expected_revision':1})
    assert updated.status_code==200,updated.text
    state=updated.json(); added=[e for e in state['evidence'] if e['id'] not in original_ids]
    assert len(added)==1 and added[0]['category']=='identity_match'
    assert added[0]['observed_value']=='hr@microsoft-internship-verification.example'
    assert state['last_change']['after']==state['fusion']
    assert any(n['id']==added[0]['id'] for n in state['graph']['nodes'])
    repeated=client.post(path,json={'expected_revision':2})
    assert repeated.json()==state
    ids=[e['id'] for e in state['evidence']]
    assert len(ids)==len(set(ids))
    reloaded=client.get(f'/api/scans/{sid}').json()
    assert reloaded['investigation']==state
    assert next(c for c in reloaded['verification_results'] if c['check_name']=='Email')['status']=='failed'


@pytest.mark.parametrize('exception,code', [(RuntimeError('Tesseract process timeout'),'OCR_TIMEOUT'),(RuntimeError('engine failed'),'OCR_ENGINE_ERROR')])
def test_ocr_failure_causes_remain_distinct(monkeypatch,exception,code):
    import pytesseract
    def fail(*args,**kwargs): raise exception
    monkeypatch.setattr(pytesseract,'image_to_string',fail)
    result=extract(client)
    assert result['status']=='UNAVAILABLE' and result['error_code']==code
    assert not result['extracted_text']


def test_real_native_ocr_then_forensic_scanners():
    import shutil
    if not shutil.which('tesseract'): pytest.skip('Native Tesseract not installed; mocked pipeline tests still run')
    from PIL import Image,ImageDraw,ImageFont
    image=Image.new('RGB',(1900,600),'white')
    ImageDraw.Draw(image).multiline_text((60,50),
        'Microsoft software engineering internship\nStipend INR 45,000 per month.\nPay a refundable registration fee of INR 999.\nSend Aadhaar card and PAN card.',
        font=ImageFont.load_default(size=46),fill='black',spacing=28)
    stream=io.BytesIO(); image.save(stream,format='PNG')
    preview=client.post('/api/analyze/screenshot/extract',files={'file':('Google_filename_only.png',stream.getvalue(),'image/png')})
    assert preview.status_code==200,preview.text
    extraction=preview.json(); assert extraction['status']=='SUCCESS'
    assert '45,000' in extraction['extracted_text'] and '999' in extraction['extracted_text']
    response=client.post('/api/analyze/screenshot/reviewed',json={'content':extraction['extracted_text'],'review_token':extraction['review_token']})
    assert response.status_code==200,response.text
    state=response.json()['investigation']
    assert state['claimed_organization']=='Microsoft Corporation'
    assert [e['value'] for e in state['monetary_entities'] if e['role']=='PAYMENT']==['999']
    assert [e['value'] for e in state['monetary_entities'] if e['role']=='COMPENSATION']==['45000']
    assert state['document_extraction']['user_corrected'] is False


def test_compensation_periods_stay_local_to_their_amounts():
    r=analyze_payment_risk('Salary ₹45,000 per month bonus ₹5,000 per year. Registration fee ₹999.')
    assert [(e['value'],e['period']) for e in r['compensation_amounts']]==[('45000','month'),('5000','year')]


@pytest.mark.parametrize('text',['Registration fee is INR 0.','No registration fee of ₹999 is required.','Without a registration fee of Rs. 999.'])
def test_negated_or_zero_fees_do_not_become_payment_demands(text):
    assert not analyze_payment_risk(text)['payment_detected']


def test_fee_label_cannot_steal_salary_amount_due_to_nearest_distance():
    text='Your promised stipend will definitely be ₹45,000 registration fee must be paid as INR 999.'
    r=analyze_payment_risk(text)
    assert [e['value'] for e in r['compensation_amounts']]==['45000']
    assert [e['value'] for e in r['payment_amounts']]==['999']


def test_competing_salary_and_fee_labels_remain_unresolved():
    assert not analyze_payment_risk('Salary ₹999 fee.')['payment_amounts']
