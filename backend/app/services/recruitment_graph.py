"""Recruitment relationships with exact citations; no inferred employer authorization."""
from uuid import uuid5,NAMESPACE_URL
from app.services.case_claims import normalize

def enrich_recruitment_graph(graph,claims,review,parent):
    if not any(c['claim_type']=='advertisement_number' for c in claims):return graph
    nodes={n['id']:dict(n) for n in graph['nodes']};edges={e['id']:dict(e) for e in graph['edges']};claim_nodes={}
    def edge(a,b,relation,status,refs):
        key=str(uuid5(NAMESPACE_URL,f'{a}:{b}:{relation}'))
        edges[key]={'id':key,'source':a,'target':b,'relation':relation,'relationship_status':status,
            'verification_status':'SCOPED_INDEPENDENT_COMPARISON' if status in {'VERIFIED','CONTRADICTED'} else 'NOT_INDEPENDENTLY_VERIFIED','citations':refs,'evidence_ids':[]}
    for c in claims:
        key=str(uuid5(NAMESPACE_URL,f"{parent}:{c['claim_type']}:{c.get('normalized_value',normalize(c['value']))}"))
        if c['claim_type']=='organization':
            existing=next((n['id'] for n in nodes.values() if n.get('type')=='organization' and normalize(n.get('label',''))==normalize(c['value'])),None)
            if existing:key=existing
        kind='notice' if c['claim_type']=='advertisement_number' else 'payment' if c['claim_type'] in {'fee','fee_relation','payment_destination'} else 'organization' if c['claim_type']=='organization' else 'claim'
        value=c['value'];label=c['claim_type'].replace('_',' ')+': '+(str(value) if not isinstance(value,dict) else ' · '.join(str(v) for v in value.values() if v is not None))
        citation={'source_id':c['source_id'],'source_title':'Submitted recruitment material','claim_id':c['id'],'excerpt':c['excerpt'],**c['location']}
        nodes.setdefault(key,{'id':key,'type':kind,'label':label,'provenance':'Submitted claim; not independent verification','citations':[]})
        nodes[key].setdefault('citations',[])
        if kind=='notice':nodes[key]['type']='notice'
        if citation not in nodes[key]['citations']:nodes[key]['citations'].append(citation)
        claim_nodes[c['id']]=key
        source=c['source_id'] if c['source_id'] in nodes else parent
        edge(source,key,'states_'+c['claim_type'],'CLAIMED',nodes[key]['citations'])
    notice_ids=[claim_nodes[c['id']] for c in claims if c['claim_type']=='advertisement_number']
    for c in claims:
        if c['claim_type']=='organization':
            for notice in set(notice_ids):edge(claim_nodes[c['id']],notice,'organization_named_in_notice','CLAIMED',nodes[claim_nodes[c['id']]]['citations'])
        if c['claim_type'] in {'fee','fee_relation','payment_channel','payment_destination','job_title','vacancies','application_deadline'}:
            for notice in set(notice_ids):edge(notice,claim_nodes[c['id']],'notice_states_'+c['claim_type'],'CLAIMED',nodes[claim_nodes[c['id']]]['citations'])
    for document in review.get('independent_documents',[]):
        nodes[document['id']]={'id':document['id'],'type':'source','label':document['title'],'provenance':document['url'],'source':document}
        edge(parent,document['id'],'independently_retrieved_exact_notice','OBSERVED',[])
    for comparison in review.get('claim_results',[]):
        if comparison['status'] not in {'INDEPENDENTLY_CORROBORATED','CONTRADICTED'}:continue
        key=claim_nodes.get(comparison['claim_id'])
        if not key:continue
        for citation in comparison['citations']:
            if citation['source_id'] in nodes and citation.get('url'):
                edge(citation['source_id'],key,'corroborates_scoped_claim' if comparison['status']=='INDEPENDENTLY_CORROBORATED' else 'contradicts_scoped_claim',
                    'VERIFIED' if comparison['status']=='INDEPENDENTLY_CORROBORATED' else 'CONTRADICTED',comparison['citations'])
    return {**graph,'nodes':list(nodes.values()),'edges':list(edges.values()),'verification_scope':'INDEPENDENT_ONLY'}
