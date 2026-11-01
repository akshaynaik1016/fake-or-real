"""Reproducible synthetic evaluations through the persisted case investigation pipeline."""
import json
from pathlib import Path
from collections import Counter
from app.schemas.cases import CaseSourceCreate
from app.services import case_service
from app.services.case_claims import normalize

def dataset():
    return json.loads(Path(__file__).with_name('scenarios.json').read_text())

def evaluate_expectations(scenario,case):
    gold=scenario['expected']
    def key(kind,value):return kind+':'+normalize(value)
    scope=set(gold['extraction_scope'])
    expected=Counter(key(c['type'],c['value']) for c in gold['claims'])
    actual=Counter(key(c['claim_type'],c['value']) for c in case['claims'] if c['claim_type'] in scope)
    tp=sum((expected&actual).values());fp=sum((actual-expected).values());fn=sum((expected-actual).values())
    by_source={s['id']:s for s in case['sources']}
    provenance=all(c['excerpt']==by_source[c['source_id']][c['location']['field']][c['location']['start']:c['location']['end']]
        and c['verification_status']=='CLAIMED' for c in case['claims'])
    citations=all(ref['excerpt']==by_source[ref['source_id']][ref['field']][ref['start']:ref['end']]
        for finding in case['cross_source_findings'] for ref in finding['citations'])
    checks=[{'name':'Assessment state','expected':gold['state'],'actual':case['assessment']['state'],'passed':case['assessment']['state']==gold['state']},
        {'name':'Focused extraction','expected':dict(expected),'actual':dict(actual),'passed':expected==actual},
        {'name':'Exact claim and comparison provenance','expected':True,'actual':provenance and citations,'passed':provenance and citations},
        {'name':'Offer verification remains unresolved','expected':'UNRESOLVED','actual':case['assessment']['offer_authenticity'],'passed':case['assessment']['offer_authenticity']=='UNRESOLVED'}]
    if gold.get('cross_kind'):
        matches=[f for f in case['cross_source_findings'] if f['kind']==gold['cross_kind']]
        checks.append({'name':'Cited cross-source finding','expected':gold['cross_kind'],'actual':[f['kind'] for f in matches],'passed':bool(matches)})
    if 'duplicates' in gold:
        checks.append({'name':'Duplicate content grouping','expected':gold['duplicates'],'actual':len(case['duplicate_sources']),'passed':len(case['duplicate_sources'])==gold['duplicates']})
    if scenario['id'].startswith('search-'):
        available=case['research'][-1]['status']=='SEARCH_UNAVAILABLE'
        checks.append({'name':'Injected external failure unresolved','expected':'SEARCH_UNAVAILABLE','actual':case['research'][-1]['status'],'passed':available})
    return {'checks':checks,'passed':all(c['passed'] for c in checks),'extraction_counts':{'tp':tp,'fp':fp,'fn':fn}}

async def run_scenario(db,scenario,actor=None):
    case=case_service.create_case(db,'[Synthetic] '+scenario['id'],actor)
    for source in scenario['sources']:
        req=CaseSourceCreate(**source,expected_revision=case['revision'])
        case=await case_service.add_text_source(db,case_service.owned_case(db,case['case_id'],actor),req)
    if scenario['id'].startswith('search-'):
        # Fault injection is explicit and confined to this evaluator; no network.
        from app.integrations.web_research.tavily_service import TavilyService
        import httpx
        def timeout(request):raise httpx.ReadTimeout('Synthetic evaluation timeout',request=request)
        adapter=TavilyService(api_key='synthetic-evaluation-only',transport=httpx.MockTransport(timeout)) if scenario['id']=='search-timeout' else TavilyService(api_key='')
        result=await adapter.search('AEXON TECH official internship')
        record=case_service.owned_case(db,case['case_id'],actor)
        record.research_results=[{**result.model_dump(),'organization':'AEXON TECH','injected_condition':scenario['id']}]
        case=case_service.record_revision(db,record,'SYNTHETIC_PROVIDER_CONDITION')
    outcome=evaluate_expectations(scenario,case)
    return {'scenario_id':scenario['id'],'synthetic':True,'expected':scenario['expected'],
        'actual':{'assessment':case['assessment'],'claims':case['claims'],'cross_source_findings':case['cross_source_findings']},
        **outcome,'case':case}

def metrics(results):
    positive=lambda s:s=='ELEVATED_CONCERN'
    tp=fp=fn=tn=abstentions=0
    for r in results:
        gold=positive(r['expected']['state']);pred=positive(r['actual']['assessment']['state'])
        tp+=int(gold and pred);fp+=int(not gold and pred);fn+=int(gold and not pred);tn+=int(not gold and not pred)
        abstentions+=int(r['actual']['assessment']['state']=='UNDETERMINED')
    divide=lambda n,d:None if not d else round(n/d,6)
    extraction={k:sum(r['extraction_counts'][k] for r in results) for k in ['tp','fp','fn']}
    extraction.update(precision=divide(extraction['tp'],extraction['tp']+extraction['fp']),recall=divide(extraction['tp'],extraction['tp']+extraction['fn']))
    return {'dataset_size':len(results),'synthetic':True,'scenario_passes':sum(r['passed'] for r in results),
        'concern_detection':{'tp':tp,'fp':fp,'fn':fn,'tn':tn,'precision':divide(tp,tp+fp),'recall':divide(tp,tp+fn),
            'false_positive_rate':divide(fp,fp+tn),'abstention_rate':divide(abstentions,len(results)),
            'expected_state_match_rate':divide(tp+tn,len(results))},'extraction':extraction,
        'limitations':['Synthetic regression examples; no real-world fraud accuracy claim.',
            'Positive label means an observable concern warrants investigation, not confirmed fraud.',
            'Negative label means abstain. TN means no escalation, not an authentic offer.',
            'Recall counts abstained positive examples as missed concerns. Metrics are descriptive on this fixed dataset.',
            'Extraction is exact multiset matching only within each scenario\'s annotated types; unannotated types are not scored.',
            'OCR-noise cases replay transcripts; OCR image recognition is tested separately.',
            'Same development team authored labels and rules; no independent held-out corpus or statistical calibration.']}
