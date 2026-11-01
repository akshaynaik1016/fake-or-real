"""One canonical snapshot projection for scan and case deterministic chat. No extraction."""
def canonical_context(detail):
    state=detail.get('investigation') or detail
    claims=state.get('claims') or []
    def unique(kind):return list(dict.fromkeys(str(c['value']) for c in claims if c['claim_type'] in kind and isinstance(c.get('value'),str) and c['value'].strip()))
    organizations=unique({'organization'})
    legacy=state.get('claimed_organization') or detail.get('claimed_organization')
    if not organizations and legacy and str(legacy).lower() not in {'none','null','undefined'}:organizations=[str(legacy)]
    domains=unique({'domain','application_url','official_website'})
    domains+= [e['value'] for e in state.get('entities',[]) if e['type']=='domain' and e.get('value') and e['value'] not in domains]
    return {'organizations':organizations,'title':state.get('title') or next(iter(unique({'job_title','role'})),None),
        'partners':unique({'claimed_collaborator'}),'certificates':unique({'certificate_association'}),'domains':domains,'senders':unique({'sender_email','contact_email'}),'claims':claims,
        'evidence':state.get('evidence',detail.get('evidence',[])), 'comparisons':state.get('cross_source_findings',[]),
        'assessment':state.get('assessment') or detail.get('assessment') or {},'research':state.get('research',[]),
        'notice_review':state.get('notice_review') or {},'sources':state.get('sources',[]),
        'recommendations':state.get('recommendations') or [],'unknowns':state.get('missing_information',[])}
