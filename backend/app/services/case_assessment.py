from copy import deepcopy
from uuid import uuid5,NAMESPACE_URL
from app.services.bayesian_evidence_engine import fuse_evidence
from app.services.cross_source_service import compare_claims,citation
from app.services.case_claims import CLAIM_TYPES
from app.core.config import settings


def case_graph(case_id,title,sources,claims,findings,evidence,research):
    nodes={case_id:{'id':case_id,'type':'case','label':title,'provenance':'Investigation case'}};edges={}
    def edge(a,b,relation,status,refs=None):
        eid=str(uuid5(NAMESPACE_URL,f'{a}:{b}:{relation}'))
        previous=edges.get(eid,{}).get('citations',[])
        refs=list({(c['source_id'],c.get('field'),c.get('start'),c.get('end')):c for c in [*previous,*(refs or [])]}.values())
        edges[eid]={'id':eid,'source':a,'target':b,'relation':relation,'relationship_status':status,
                    'verification_status':'NOT_INDEPENDENTLY_VERIFIED','citations':refs or [],'evidence_ids':[]}
    for source in sources.values():
        nodes[source['id']]={'id':source['id'],'type':'source_document','label':source['title'],
            'provenance':f"{source['input_type']} · {source['processing_status']}",
            'citations':[{'source_id':source['id'],'source_title':source['title'],'excerpt':source.get('error_message') or source.get('extracted_text','')[:300], 'field':'extracted_text'}]}
        edge(case_id,source['id'],'contains_source','OBSERVED')
    for claim in claims:
        value=claim['value']
        kind={'organization':'organization','sender_email':'email','contact_email':'email','application_url':'domain',
              'contact_number':'phone','fee':'payment'}.get(claim['claim_type'],'claim')
        key=str(uuid5(NAMESPACE_URL,f"{case_id}:{claim['claim_type']}:{claim['normalized_value']}"))
        label=str(value) if not isinstance(value,dict) else ' · '.join(f'{k}: {v}' for k,v in value.items() if v is not None)
        ref=citation(claim,sources)
        if key not in nodes:nodes[key]={'id':key,'type':kind,'label':label,'provenance':'Submitted claim; not independently verified','citations':[]}
        nodes[key]['citations'].append(ref)
        edge(claim['source_id'],key,'states_'+claim['claim_type'],'CLAIMED',[ref])
    for ev in evidence:
        if ev['category'].startswith('cross_source_'):continue
        nodes[ev['id']]={'id':ev['id'],'type':'evidence','label':ev['evidence'],'provenance':ev['source'],
            'evidence':ev,'citations':ev.get('citations',[]),'inconsistent':False}
        for ref in ev.get('citations',[]):
            if ref['source_id'] in sources:edge(ref['source_id'],ev['id'],'has_finding','OBSERVED',[ref])
    for finding in findings:
        nodes[finding['id']]={'id':finding['id'],'type':'contradiction' if 'CONTRADICTION' in finding['classification'] else 'cross_finding',
            'label':finding['description'],'provenance':finding['classification'],'citations':finding['citations'],
            'inconsistent':finding['classification']=='CONFIRMED_CONTRADICTION'}
        for ref in finding['citations']:
            edge(ref['source_id'],finding['id'],'supports_comparison',
                 'CONTRADICTED' if finding['classification']=='CONFIRMED_CONTRADICTION' else 'UNRESOLVED',[ref])
    for result in research:
        for source in result.get('sources',[]):
            nodes[source['id']]={'id':source['id'],'type':'source','label':source['title'],'provenance':source['url'],'source':source}
            edge(case_id,source['id'],'retrieved_search_context','UNRESOLVED')
    return {'nodes':list(nodes.values()),'edges':list(edges.values()),'verification_scope':'INDEPENDENT_ONLY',
        'disclaimer':'Claims and repeated documents are not independent verification. Contradictions describe disagreements in submitted claims, not proof of fraud. Search excerpts do not authenticate an offer.'}


def assess_case(case,sources,claims):
    source_map={s['id']:s for s in sources}
    groups={};duplicates={};canonical=[]
    for source in sources:
        fingerprint=source.get('content_hash') if source['processing_status']=='READY' else None
        if fingerprint and fingerprint in groups:duplicates[source['id']]=groups[fingerprint]
        else:
            canonical.append(source)
            if fingerprint:groups[fingerprint]=source['id']
    findings=compare_claims(case.id,claims,source_map)
    evidence=[];checks=[];dedup={}
    for source in canonical:
        if source['processing_status']!='READY':
            checks.append({'name':source['title']+' processing','completed':False,'reason':source.get('error_message') or source['processing_status']})
            continue
        state=source['analysis']
        checks.extend([{**c,'name':source['title']+' · '+c['name']} for c in state.get('coverage_checks',[])])
        if source['input_type']=='url':checks.append({'name':source['title']+' page retrieval','completed':source['extraction_status']=='SUCCESS','reason':source.get('error_message') or 'Page retrieval not performed'})
        for original in state.get('evidence',[]):
            ev=deepcopy(original);ev['id']=str(uuid5(NAMESPACE_URL,f"case:{case.id}:{source['content_hash']}:{original['id']}"))
            refs=[]
            for span in original.get('source_spans',[]):
                refs.append({'source_id':source['id'],'source_title':source['title'],'field':'extracted_text','excerpt':span['text'],'start':span['start'],'end':span['end'],**({'page':span['page']} if span.get('page') else {})})
            if not refs:
                observed=original.get('observed_value','');start=source['extracted_text'].find(observed) if observed else -1
                refs=[{'source_id':source['id'],'source_title':source['title'],'field':'extracted_text' if start>=0 else 'scanner_output',
                       'excerpt':observed if start>=0 else original['evidence'],**({'start':start,'end':start+len(observed)} if start>=0 else {})}]
            ev['source_id']=source['id'];ev['source_ids']=[source['id']];ev['citations']=refs;ev['related_entities']=[];dedup[ev['id']]=ev
    from app.services.evidence_service import group_evidence
    evidence=group_evidence(list(dedup.values()),across_sources=True)
    for finding in findings:
        if finding['classification'] not in {'CONFIRMED_CONTRADICTION','POSSIBLE_INCONSISTENCY'}:continue
        evidence.append({'id':'fusion-'+finding['id'],'category':'cross_source_'+finding['kind'].lower(),
            'severity':'high' if finding['classification']=='CONFIRMED_CONTRADICTION' else 'moderate',
            'evidence':finding['description'],'source':'Deterministic cross-source comparison','confidence':0.9,
            'origin':'DETERMINISTIC_RULE','verification_status':'OBSERVED_CLAIM_DISAGREEMENT',
            'correlation_group':'payment' if finding['kind']=='FEE_INSTRUCTION_CONFLICT' else 'cross_source_'+finding['kind'].lower(),
            'explanation':'Comparison of cited submitted claims; no external authenticity judgment.',
            'citations':finding['citations'],'source_ids':list(dict.fromkeys(c['source_id'] for c in finding['citations'])),
            'claim_type':finding['kind'],'extraction_method':'deterministic_claim_comparison','provenance_kind':'RULE_OUTPUT','original_excerpt':None,'extracted_value':[c['excerpt'] for c in finding['citations']],'related_entities':[]})
    from app.services.notice_verification import compare_notice,notice_evidence,notice_action
    notice_review=compare_notice(claims,case.research_results)
    from app.services.program_claims import program_unknowns
    notice_review['unknowns']+=program_unknowns(claims)
    evidence.extend(notice_evidence(notice_review))
    fusion=fuse_evidence(evidence,checks)
    strong_concern=any(e['severity'] in {'high','critical'} and e.get('origin') not in {'SYNTHETIC','EXTERNAL_SOURCE','AI_INTERPRETATION'} and e.get('verification_status') not in {'UNKNOWN','UNAVAILABLE','SYNTHETIC'} for e in evidence)
    if fusion['risk_level']=='INSUFFICIENT_INFORMATION' or not strong_concern:
        fusion.update(risk_level='UNDETERMINED',risk_score=None)
        fusion['explanation'].append('Reassuring submitted claims or reference-domain matches alone do not establish sufficient evidence for a case-level safety classification.')
    missing=[kind for kind in CLAIM_TYPES if not any(c['claim_type']==kind for c in claims)]
    unknowns=['Missing '+kind.replace('_',' ')+' claim' for kind in missing]
    recommendations=[]
    def rec(action,title,reason,rank=80,automatic=False,available=True,unavailable=None):
        recommendations.append({'action_id':action,'title':title,'reason':reason,'priority':'HIGH' if rank>=80 else 'MEDIUM',
            'ranking_score':rank,'execution_type':'AUTOMATED' if automatic else 'MANUAL',
            'status':'AVAILABLE' if available else 'UNAVAILABLE','unavailable_reason':unavailable,
            'instructions':reason,'required_information':[],'expected_outcomes':['Additional recorded evidence or an explicit unresolved result; no automatic authenticity guarantee.']})
    for source in canonical:
        for action in source.get('analysis',{}).get('recommendations',[]):
            if action['action_id']=='verify_sender_domain':
                recommendation=deepcopy(action);recommendation['action_id']='sender:'+source['id'];recommendation['title']=source['title']+': '+action['title']
                recommendations.append(recommendation)
    if any(c['claim_type']=='fee' for c in claims):rec('confirm_fee','Confirm whether the fee is authorized','Pause payment. Contact the organization through independently sourced official details and ask about this exact fee.',100)
    if any(f['classification'] in {'CONFIRMED_CONTRADICTION','POSSIBLE_INCONSISTENCY'} for f in findings):rec('resolve_conflicts','Resolve conflicting opportunity terms','Ask the organization through an independently sourced contact to confirm the role, stipend, duration and application channel in writing.',95)
    exact_action=notice_action(claims,case.research_calls,research=case.research_results)
    if exact_action:recommendations.append(exact_action)
    orgs=list(dict.fromkeys(c['value'] for c in claims if c['claim_type']=='organization'))
    if len(orgs)==1:
        completed=any(r.get('status')=='COMPLETED' and r.get('organization')==orgs[0] for r in case.research_results)
        available=bool(settings.TAVILY_API_KEY) and case.research_calls<3 and not completed
        rec('official_listing','Search independent official-listing context','Search the claimed organization careers/offer context. A search mention does not authenticate the specific offer.',85,True,available,
            'Search already performed; inspect its sources.' if completed else 'Case search budget exhausted.' if case.research_calls>=3 else 'TAVILY_API_KEY is not configured.' if not settings.TAVILY_API_KEY else None)
        if completed:recommendations[-1]['status']='COMPLETED'
    if not any(s['input_type']=='pdf' and s['processing_status']=='READY' for s in sources):rec('request_letter','Request an official offer letter','Obtain a written offer and verify it through a contact found independently of the recruiter.',70)
    if any(c['claim_type']=='application_url' for c in claims):rec('verify_url','Verify the application URL','Type the independently known official careers address and compare the application route. Avoid login/payment links supplied only by the recruiter.',80)
    if not sources:rec('add_source','Add the original opportunity source','Add a poster, offer letter, email, URL or message. Missing evidence cannot establish safety.',90)
    status='NEEDS_EVIDENCE' if not sources else 'NEEDS_REVIEW' if any(s['processing_status']=='NEEDS_REVIEW' for s in sources) else 'PARTIAL' if unknowns or fusion['unknowns'] else 'ACTIVE'
    from app.services.recruitment_graph import enrich_recruitment_graph
    from app.services.assessment_semantics import assessment_for
    from app.services.program_graph import enrich_program_graph
    graph=enrich_program_graph(enrich_recruitment_graph(case_graph(case.id,case.title,source_map,claims,findings,evidence,case.research_results),claims,notice_review,case.id),claims,case.id)
    return {'source_limits':{'url':max(1,settings.CASE_MAX_URLS),'pdf':max(1,settings.CASE_MAX_PDFS)},'coverage_checks':checks,'notice_review':notice_review,'assessment':assessment_for(fusion,evidence,claims,{'sources':sources,'coverage_checks':checks,'notice_review':notice_review,'research':case.research_results,'recommendations':recommendations}),'case_id':case.id,'title':case.title,'revision':case.revision,'status':status,'fusion':fusion,'sources':sources,
        'claims':claims,'cross_source_findings':findings,'evidence':evidence,'missing_information':unknowns,
        'duplicate_sources':duplicates,'distinct_content_count':len([s for s in canonical if s['processing_status']=='READY']),
        'recommendations':sorted(recommendations,key=lambda a:-a.get('ranking_score',0)),
        'research':case.research_results,'research_calls':case.research_calls,
        'graph':graph}
