"""Count one case once; keep legacy scan metrics available without changing them."""
from collections import Counter
from app.models.all_models import InvestigationCase,InvestigationSource,CaseAssessmentRevision
from app.services.assessment_semantics import integrity_view

def summarize_investigations(db,actor,scan_details):
    q=db.query(InvestigationCase)
    if actor and actor.role!='ADMIN':q=q.filter_by(user_id=actor.id)
    cases=q.all();ids=[c.id for c in cases];linked=set()
    if ids:
        linked.update(s.scan_id for s in db.query(InvestigationSource).filter(InvestigationSource.case_id.in_(ids)).all() if s.scan_id)
        # Corrections replace the current source.scan_id; historical case scans
        # must also remain excluded from standalone opportunity counts.
        for (snapshot,) in db.query(CaseAssessmentRevision.snapshot).filter(CaseAssessmentRevision.case_id.in_(ids)):
            linked.update(s['scan_id'] for s in snapshot.get('sources',[]) if s.get('scan_id'))
    assessments=[integrity_view(c.assessment)['assessment'] for c in cases if c.assessment.get('sources')]
    standalone=[s for s in scan_details if s['id'] not in linked]
    assessments.extend(s['assessment'] for s in standalone)
    overall=Counter(a['state'] for a in assessments);signals=Counter(a['risk_indicators']['label'] for a in assessments)
    return {'stats':{'opportunities_checked':len(assessments),'safe_count':0,'needs_verification':overall['UNDETERMINED'],'high_risk':overall['ELEVATED_CONCERN'],'critical_risk':0},
        'risk_distribution':[{'name':'Undetermined','value':overall['UNDETERMINED'],'color':'#f59e0b'},{'name':'Elevated concern','value':overall['ELEVATED_CONCERN'],'color':'#f43f5e'}],
        'risk_indicator_distribution':[{'name':name,'value':value} for name,value in signals.items()],
        'basis':'One active case with sources or one standalone scan. Linked current and historical case-source scans are excluded. Empty cases are not counted.',
        'case_count':sum(bool(c.assessment.get('sources')) for c in cases),'standalone_count':len(standalone)}
