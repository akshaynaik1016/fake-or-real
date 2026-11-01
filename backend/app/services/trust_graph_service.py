"""Evidence relationships only; no inferred ownership or criminal attribution."""
from copy import deepcopy
import hashlib
import networkx as nx


def entity_id(kind: str, value: str) -> str:
    return kind+':'+hashlib.sha256(value.lower().encode()).hexdigest()[:16]


def build_trust_graph(entities: list[dict], evidence: list[dict], research: list[dict]) -> dict:
    graph=nx.MultiDiGraph()
    graph.add_node('submission',type='offer',label='Submitted opportunity',provenance='User submission')
    def edge(a,b,relation,status,ids=None,verification_status='NOT_INDEPENDENTLY_VERIFIED'):
        key=hashlib.sha256(f'{a}|{b}|{relation}'.encode()).hexdigest()[:20]
        graph.add_edge(a,b,key=key,id='edge-'+key,relation=relation,relationship_status=status,
            evidence_ids=ids or [],verification_status=verification_status)
    for entity in entities:
        graph.add_node(entity['id'],type=entity['type'],label=entity['value'],provenance=entity['provenance'])
        claim=entity['type']=='organization'
        edge('submission',entity['id'],'claims_to_represent' if claim else 'mentions','CLAIMED' if claim else 'OBSERVED')
    for ev in evidence:
        graph.add_node(ev['id'],type='evidence',label=ev['evidence'],provenance=ev['source'],evidence=deepcopy(ev),
            inconsistent=ev['category'] in {'organization_verification','identity_match'} and ev['severity'] in {'critical','high'})
        status='UNRESOLVED' if ev['origin']=='SYNTHETIC' else 'OBSERVED'
        edge('submission',ev['id'],'has_finding',status,[ev['id']],ev['verification_status'])
        for related in ev['related_entities']:
            if graph.has_node(related):
                reference=ev['verification_status'] in {'REFERENCE_MATCH','BUNDLED_REFERENCE_COMPARISON'} and ev['severity']=='verified'
                mismatch=ev['verification_status']=='REFERENCE_MISMATCH' or (
                    ev['category']=='organization_verification' and ev['severity']=='critical' and ev['origin']!='SYNTHETIC')
                state='VERIFIED' if reference else 'CONTRADICTED' if mismatch else status
                edge(ev['id'],related,'concerns',state,[ev['id']],ev['verification_status'])
    for result in research:
        for source in result.get('sources',[]):
            graph.add_node(source['id'],type='source',label=source['title'],provenance=source['url'],source=deepcopy(source))
            edge('submission',source['id'],'search_result_for_claim','UNRESOLVED',verification_status=source['verification_status'])
    return {'nodes':[{'id':n,**attrs} for n,attrs in graph.nodes(data=True)],
        'edges':[{'source':a,'target':b,**attrs} for a,b,attrs in graph.edges(data=True)],
        'disclaimer':'Observed means present in submitted or collected data. Claimed affiliations are unverified. Verified/contradicted reference comparisons do not authenticate a sender or offer. Synthetic and unverified source relationships remain unresolved.'}
