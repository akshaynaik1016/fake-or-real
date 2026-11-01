"""Export the current stored case snapshot without any fresh scanner/provider calls."""
from app.services.report_generator import generate_pdf_report

def generate_case_report(snapshot):
    sections=[]
    for s in snapshot['sources']:
        sections.append(('Source: '+s['title'],[f"Type: {s['input_type']} | ID: {s['id']} | Status: {s['processing_status']} | Extraction: {s['extraction_status']}",s.get('error_message') or 'No processing error recorded.']))
    for c in snapshot['claims']:
        loc=c['location'];sections.append(('Submitted claim: '+c['claim_type'].replace('_',' '),[str(c['value']),f"Source {c['source_id']} | page {loc.get('page','not available')} | characters {loc['start']}–{loc['end']} | {c['extraction_method']}",c['excerpt']]))
    for f in snapshot['cross_source_findings']:
        sections.append((f['classification'].replace('_',' '),[f['description']]+[f"Source {c['source_id']} | page {c.get('page','not available')}: {c['excerpt']}" for c in f['citations']]))
    review=snapshot.get('notice_review') or {}
    for c in review.get('claim_results',[]):
        sections.append(('Exact notice: '+c['claim_type'].replace('_',' '),[c['status']+': '+c['reason']]+[f"Source {r['source_id']} | {r.get('url','submitted')}: {r['excerpt']}" for r in c['citations']]))
    sections.append(('Unknowns',snapshot.get('missing_information',[])+review.get('unknowns',[])))
    score=snapshot['fusion']['risk_score']
    return generate_pdf_report({'id':snapshot['case_id'],'input_type':'case','trust_score':None if score is None else 100-score,
        'risk_level':snapshot['assessment']['label'],'analysis_confidence':snapshot['fusion']['confidence'],
        'summary':snapshot['title']+'. Specific offer authenticity remains unresolved. Sources and submitted disagreements below are not independent confirmations.',
        'investigation':snapshot,'evidence':snapshot['evidence'],'verification_results':[],
        'recommended_actions':[a['title']+': '+(a.get('unavailable_reason') or a['reason']) for a in snapshot['recommendations']],
        'case_sections':sections})
