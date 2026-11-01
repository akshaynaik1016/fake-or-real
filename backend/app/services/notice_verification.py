"""Exact-advertisement corroboration from bounded, independently retrieved documents.

Search snippets, user uploads and a domain/reference match cannot enter this path
as independent corroboration. Every comparison retains both original excerpts.
"""
from copy import deepcopy
from datetime import datetime,timezone
import hashlib
import re
from urllib.parse import urlsplit
from uuid import uuid5,NAMESPACE_URL
from app.core.config import settings
from app.agents.investigation_orchestrator import organization_reference
from app.services.case_claims import extract_claims,normalize

NOTICE_FIELDS={'organization','advertisement_number','job_title','publication_date','vacancies','application_start','application_deadline','fee','fee_exemption','payment_destination','payment_channel','eligibility','official_website'}

def values(claims,kind):return list({normalize(c['value']):c['value'] for c in claims if c['claim_type']==kind}.values())
def anchors(claims):
    org=values(claims,'organization');ad=values(claims,'advertisement_number');role=values(claims,'job_title') or values(claims,'role')
    if len(org)!=1 or len(ad)!=1 or len(role)!=1:return None
    return {'organization':org[0],'advertisement_number':ad[0],'job_title':role[0]}

def trusted_host(url,domains):
    try:
        p=urlsplit(url);host=(p.hostname or '').lower().rstrip('.')
        return p.scheme=='https' and not p.username and not p.password and any(host==d or host.endswith('.'+d) for d in domains if '/' not in d)
    except ValueError:return False

def notice_action(claims,calls,history=(),research=()):
    target=anchors(claims)
    if not target:return None
    reference=organization_reference(target['organization']) or {}
    reason='Match this advertisement number, organization and position against a full independently retrieved notice, then compare dates, vacancies, fee and destination.'
    unavailable='No trusted organization website reference is available.' if not reference.get('official_domains') else 'TAVILY_API_KEY is not configured.' if not settings.TAVILY_API_KEY else 'Official document retrieval is disabled. Enable OFFICIAL_NOTICE_FETCH_ENABLED for bounded trusted-host checks, or compare the fields manually.' if not (settings.CASE_URL_FETCH_ENABLED or settings.OFFICIAL_NOTICE_FETCH_ENABLED) else 'Research budget exhausted.' if calls>=settings.MAX_RESEARCH_CALLS else None
    signature=normalize(target)
    completed=any(r.get('notice_verification') and r.get('target_signature')==signature and r.get('status')=='COMPLETED' for r in research)
    return {'action_id':'verify_notice','title':'Verify this exact recruitment advertisement','reason':reason,'priority':'HIGH','ranking_score':105,
        'execution_type':'AUTOMATED','status':'COMPLETED' if completed else 'UNAVAILABLE' if unavailable else 'AVAILABLE',
        'unavailable_reason':'Exact-notice check already ran; inspect the dated claim comparisons. Unresolved claims remain unknown.' if completed else unavailable,
        'instructions':'Open the independently established official careers site. A matching company name or general search result is insufficient.',
        'required_information':['One organization, advertisement number and job title','Tavily and bounded public retrieval'],
        'expected_outcomes':['Scoped corroborated/contradicted claims or an explicit unresolved reason; never automatic authentication of the submitted file.']}

async def retrieve_notice(claims):
    from app.integrations.web_research.tavily_service import TavilyService
    from app.services.case_url_fetcher import fetch_public_text,URLFetchError
    target=anchors(claims)
    if not target:return {'status':'SEARCH_UNAVAILABLE','reason':'Exact notice identifiers are missing or ambiguous.','sources':[],'independent_documents':[],'notice_verification':True}
    reference=organization_reference(target['organization']) or {};domains=reference.get('official_domains',[])
    common={'notice_verification':True,'target_signature':normalize(target),'organization':target['organization'],'independent_documents':[]}
    if not (settings.CASE_URL_FETCH_ENABLED or settings.OFFICIAL_NOTICE_FETCH_ENABLED) or not domains:
        return {**common,'status':'SEARCH_UNAVAILABLE','reason':'Bounded retrieval or trusted domain reference unavailable; exact claims remain unresolved.','sources':[]}
    query=f'"{target["advertisement_number"]}" {target["organization"]} {target["job_title"]}'[:250]
    search=await TavilyService().search(query,domains)
    result={**search.model_dump(),**common};errors=[];attempts=0
    for source in search.sources:
        if attempts>=2:break
        if not trusted_host(source.url,domains):continue
        attempts+=1
        try:
            fetched=await fetch_public_text(source.url,allow_pdf=True,allowed_domains=domains)
            if fetched.get('truncated') or not trusted_host(fetched['final_url'],domains):
                errors.append('A retrieved document was truncated or redirected outside the trusted website; it was not used for corroboration.');continue
            from app.security.redaction import redact_sensitive_credentials
            text=redact_sensitive_credentials(fetched['text']);fingerprint=hashlib.sha256(text.encode()).hexdigest()
            sid='independent-'+str(uuid5(NAMESPACE_URL,fetched['final_url']+':'+fingerprint))
            document={'id':sid,'url':fetched['final_url'],'title':source.title,'text':text,'content_hash':fingerprint,
                'retrieved_at':datetime.now(timezone.utc).isoformat(),'retrieval_method':'PINNED_HTTPS_FULL_DOCUMENT',
                'redirect_chain':fetched['redirect_chain'],'trusted_domains':domains,
                'claims':extract_claims(sid,text,'pdf' if fetched.get('content_type')=='application/pdf' else 'url'),
                'extracted_information':text[:1000],'source_type':'OFFICIAL_DOMAIN','verification_status':'INDEPENDENTLY_RETRIEVED_CONTEXT'}
            result['independent_documents'].append(document)
        except URLFetchError as exc:errors.append(exc.code+': '+str(exc))
    result['retrieval_errors']=errors
    if not result['independent_documents']:
        result['reason']=search.reason+' No complete matching official document was retrieved; specific claims remain unresolved.'
    else:result['reason']='Full official-host documents retrieved. Only exact-notice, scoped claim comparisons may be corroborated; the submitted file remains unauthenticated.'
    return result

def ref(claim,title=None,url=None):
    return {'source_id':claim['source_id'],'source_title':title or 'Submitted recruitment material','claim_id':claim['id'],
        'excerpt':claim['excerpt'],**claim['location'],**({'url':url} if url else {})}

def compare_notice(claims,research):
    target=anchors(claims);results=[];documents=[];reasons=[]
    if not target:return {'claim_results':[],'independent_documents':[],'unknowns':['An exact comparison needs one unambiguous organization, advertisement number and job title.']}
    reference=organization_reference(target['organization']) or {};domains=reference.get('official_domains',[])
    for attempt in research:
        if not attempt.get('notice_verification'):continue
        for document in attempt.get('independent_documents',[]):
            if document.get('retrieval_method')!='PINNED_HTTPS_FULL_DOCUMENT' or not trusted_host(document.get('url',''),domains):continue
            # Re-extract from retained fetched text, never trust a source-provided
            # "verified" flag or a stale externally submitted claim list.
            dc=extract_claims(document['id'],document['text'],'pdf' if '--- Page' in document['text'] else 'url')
            da=anchors(dc)
            if not da or normalize(da)!=normalize(target):
                reasons.append('Retrieved official-host material did not uniquely match the exact advertisement, organization and job title.');continue
            documents.append({**document,'claims':dc})
    for claim in claims:
        if claim['claim_type'] not in NOTICE_FIELDS:continue
        corroborated=[];contradicted=[];possible=[]
        for document in documents:
            candidates=[c for c in document['claims'] if c['claim_type']==claim['claim_type']]
            matches=[c for c in candidates if normalize(c['value'])==normalize(claim['value'])]
            if matches:corroborated.extend((document,c) for c in matches)
            elif candidates and claim['claim_type']=='fee':
                value=claim['value'];same=[c for c in candidates if c['value'].get('currency')==value.get('currency') and c['value'].get('category')==value.get('category')]
                # A stated base/total relationship prevents a false contradiction.
                relations=[c['value'] for c in [*claims,*document['claims']] if c['claim_type']=='fee_relation']
                from decimal import Decimal
                related=lambda c:any(r['currency']==value['currency'] and {Decimal(value['value']),Decimal(c['value']['value'])}<={Decimal(r['base']),Decimal(r['total'])} for r in relations)
                different=[c for c in same if not related(c) and Decimal(c['value']['value'])!=Decimal(value['value'])]
                if different:
                    totals=[c for c in different if c['value'].get('amount_role')=='TAX_INCLUSIVE_TOTAL']
                    if value.get('applicability')=='ALL' and value.get('amount_role')=='TAX_INCLUSIVE_TOTAL' and len(totals)==1 and totals[0]['value'].get('applicability')=='ALL':contradicted.append((document,totals[0]))
                    else:possible.append((document,different[0]))
            elif candidates and len({normalize(c['value']) for c in candidates})==1 and claim['claim_type'] in {'publication_date','vacancies','application_deadline','application_start','payment_destination'}:
                # Ambiguous raw numeric dates are not asserted as contradictions.
                if 'date' in claim['claim_type'] or claim['claim_type'] in {'application_start','application_deadline'}:
                    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}',str(claim['value'])) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}',str(candidates[0]['value'])):continue
                contradicted.append((document,candidates[0]))
        status='CONTRADICTED' if contradicted else 'INDEPENDENTLY_CORROBORATED' if corroborated else 'POSSIBLE_INCONSISTENCY' if possible else 'UNRESOLVED'
        supports=contradicted or corroborated or possible
        citations=[ref(claim)]+[ref(c,d['title'],d['url']) for d,c in supports]
        key=str(uuid5(NAMESPACE_URL,'notice:'+claim['id']+status+':'.join(d['id'] for d,c in supports)))
        results.append({'id':key,'claim_id':claim['id'],'claim_type':claim['claim_type'],'value':claim['value'],'status':status,'citations':citations,
            'scope':f"{claim['claim_type'].replace('_',' ')} for advertisement {target['advertisement_number']} as retrieved; not authenticity of the uploaded file, recruiter or payment transaction.",
            'reason':'The same exact advertisement on an independently retrieved official-host document states a different value.' if contradicted else 'The stated value matches an independently retrieved exact-notice document.' if corroborated else 'An independently retrieved exact notice states a different fee; category, exemptions or tax basis are not sufficiently comparable to assert a verified contradiction.' if possible else 'No complete independently retrieved exact-notice source supports or contradicts this specific claim.'})
    if not documents:reasons.append('No full official-host document uniquely matching this exact advertisement was independently retrieved. General search context does not verify it.')
    return {'target':target,'claim_results':results,'independent_documents':documents,'unknowns':list(dict.fromkeys(reasons)),
        'offer_authenticity':'UNRESOLVED','manual_verification':{'official_domains':domains,'authority_reason':reference.get('reference_url') or 'Bundled organization domain reference; does not authenticate the notice.','fields':[{'claim_type':c['claim_type'],'value':c['value'],'source_id':c['source_id'],'excerpt':c['excerpt']} for c in claims if c['claim_type'] in NOTICE_FIELDS]}}

def notice_evidence(review):
    grouped={}
    for result in review['claim_results']:
        if result['status']=='UNRESOLVED':continue
        key='notice:'+result['claim_type']+':'+normalize(result['value'])+':'+result['status']
        if key in grouped:
            grouped[key]['citations'].extend(result['citations']);continue
        contradiction=result['status']=='CONTRADICTED';possible=result['status']=='POSSIBLE_INCONSISTENCY'
        grouped[key]={'id':result['id'],'category':'notice_contradiction' if contradiction else 'notice_possible_inconsistency' if possible else 'notice_corroboration',
            'severity':'critical' if contradiction else 'moderate' if possible else 'low','evidence':result['reason']+' '+result['claim_type'].replace('_',' ')+': '+str(result['value']),
            'source':'Exact-notice comparison of independently retrieved official material','confidence':0.95,
            'explanation':result['scope'],'timestamp':datetime.now(timezone.utc).isoformat(),'observed_value':str(result['value']),
            'origin':'DETERMINISTIC_RULE' if contradiction or possible else 'EXTERNAL_SOURCE',
            'verification_status':'INDEPENDENTLY_CORROBORATED_CONTRADICTION' if contradiction else 'UNRESOLVED' if possible else 'INDEPENDENTLY_VERIFIED',
            'verified_claim_id':None if contradiction or possible else result['claim_id'],'verification_scope':result['scope'],
            'claim_type':result['claim_type'],'extracted_value':result['value'],'extraction_method':'exact_notice_claim_comparison',
            'source_spans':[],'source_id':result['citations'][0]['source_id'],'original_excerpt':result['citations'][0]['excerpt'],'citations':result['citations'],'source_ids':list(dict.fromkeys(c['source_id'] for c in result['citations'])),
            'provenance_kind':'INDEPENDENT_CLAIM_COMPARISON','correlation_group':'independent_notice_contradiction' if contradiction else 'payment' if possible else 'independent_notice_corroboration','fact_key':key}
    return list(grouped.values())
