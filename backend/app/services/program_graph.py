"""Program overview derived only from cited submitted claims and assessment state."""
from uuid import uuid5,NAMESPACE_URL

def enrich_program_graph(graph,claims,parent):
    selected=[c for c in claims if c['claim_type'] in {'fee_policy_disclosure','claimed_collaborator','certificate_association'}]
    if not selected:return graph
    nodes={n['id']:dict(n) for n in graph['nodes']};edges={e['id']:dict(e) for e in graph['edges']}
    def ref(c):return {'source_id':c['source_id'],'source_title':'Submitted program material','claim_id':c['id'],'excerpt':c['excerpt'],**c['location']}
    def add(key,kind,label,rows,relation):
        node='program-'+str(uuid5(NAMESPACE_URL,parent+':'+key));citations=[ref(c) for c in rows]
        nodes[node]={'id':node,'type':kind,'label':label,'provenance':'Submitted claim; independent verification unresolved','citations':citations}
        eid='program-edge-'+str(uuid5(NAMESPACE_URL,parent+':'+key+':'+relation))
        edges[eid]={'id':eid,'source':parent,'target':node,'relation':relation,'relationship_status':'UNRESOLVED' if key=='verification' else 'CLAIMED','verification_status':'NOT_INDEPENDENTLY_VERIFIED','citations':citations,'evidence_ids':[]}
    types=[c for c in claims if c['claim_type']=='opportunity_type']
    if types:add('type','program',' / '.join(dict.fromkeys(str(c['value']) for c in types)),types,'describes_program')
    fees=[c for c in claims if c['claim_type']=='fee_policy_disclosure']
    if fees:add('training-fee','payment_policy','Training Fee — amount unspecified' if not any(c['claim_type']=='fee' and c['value'].get('category')=='TRAINING_FEE' for c in claims) else 'Training Fee — see cited amount',fees,'discloses_training_fee')
    partners=[c for c in claims if c['claim_type']=='claimed_collaborator']
    if partners:add('partners','partnership','Claimed Partnerships ('+str(len({c['normalized_value'] for c in partners}))+')',partners,'claims_partnerships')
    certificates=[c for c in claims if c['claim_type']=='certificate_association']
    if certificates:add('certificates','certificate','Claimed certificate association',certificates,'claims_certificate_association')
    add('verification','verification','Unresolved Verification',[],'offer_authenticity_unresolved')
    return {**graph,'nodes':list(nodes.values()),'edges':list(edges.values())}
