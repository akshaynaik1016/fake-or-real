"""Additive observed-risk and scoped-authenticity views. Never changes fusion math."""
INELIGIBLE={'SYNTHETIC','EXTERNAL_SOURCE','AI_INTERPRETATION'}

def dimensions(fusion,evidence,claims,context,verified):
    ctx=context or {};checks=ctx.get('coverage_checks',[]);sources=ctx.get('sources',[])
    # Offer content must have actually been inspected; a URL string, missing OCR
    # or historical metadata alone cannot support a reassuring text assessment.
    informative=any(c.get('claim_type') in {'opportunity_type','role','job_title','compensation'} for c in claims)
    if sources:
        processed=[s for s in sources if s['processing_status']=='READY']
        readable=any(s['input_type']!='url' or s.get('extraction_status')=='SUCCESS' for s in processed)
    else:
        processed=[];kind=ctx.get('baseline',{}).get('input_type')
        readable=kind in {'text','email','pdf','screenshot','image'}
    inspection_checks=checks or [c for s in processed for c in s.get('analysis',{}).get('coverage_checks',[])]
    inspected=informative and readable and (any(c.get('completed') and ('Content rules' in c['name'] or 'Payment and sensitive' in c['name']) for c in inspection_checks))
    observed=[e for e in evidence if e.get('origin') not in INELIGIBLE and e.get('verification_status') not in {'UNKNOWN','UNAVAILABLE','SYNTHETIC'} and e.get('severity') in {'moderate','high','critical'}]
    state='ELEVATED_CONCERN' if any(e['severity'] in {'high','critical'} for e in observed) else 'SOME_CONCERNS_OBSERVED' if observed else 'NO_SIGNIFICANT_CONCERNS_OBSERVED' if inspected else 'INSUFFICIENT_EVIDENCE_TO_ASSESS'
    labels={'ELEVATED_CONCERN':'Elevated concern','SOME_CONCERNS_OBSERVED':'Some concerns observed','NO_SIGNIFICANT_CONCERNS_OBSERVED':'No significant concerns observed','INSUFFICIENT_EVIDENCE_TO_ASSESS':'Insufficient evidence to assess'}
    explanation=('No significant suspicious indicators were identified in the submitted opportunity description. However, the organization, recruiter and specific opportunity have not been independently authenticated.' if state=='NO_SIGNIFICANT_CONCERNS_OBSERVED' else 'Recorded concerns warrant investigation; they do not prove fraud.' if observed else 'Readable opportunity content or recorded content-check execution is insufficient. Missing evidence is not safety evidence.')
    contradictions=[e for e in evidence if e.get('verification_status')=='INDEPENDENTLY_CORROBORATED_CONTRADICTION' and e.get('citations') and e.get('source')]
    review=ctx.get('notice_review') or {};research=ctx.get('research',[])
    unavailable=any(a.get('action_id')=='verify_notice' and a.get('status')=='UNAVAILABLE' for a in ctx.get('recommendations',[])) or any(r.get('notice_verification') and not r.get('independent_documents') for r in research)
    auth_state='INDEPENDENT_CONTRADICTION' if contradictions else 'SCOPED_CORROBORATION' if verified else 'VERIFICATION_UNAVAILABLE' if unavailable else 'UNVERIFIED'
    auth_labels={'INDEPENDENT_CONTRADICTION':'Specific claims contradicted by independently retrieved evidence','SCOPED_CORROBORATION':'Independently corroborated within stated scope','VERIFICATION_UNAVAILABLE':'Verification unavailable','UNVERIFIED':'Unverified'}
    auth_explanation=('Cited independently retrieved evidence contradicts specific claims; inspect both sources and their scope. This does not establish which recruiter is authorized or prove fraud.' if contradictions else 'Only the cited field comparisons have independent support. Matching fields do not authenticate the uploaded file, recruiter or payment destination.' if verified else 'No independent corroboration obtained for this opportunity. The organization, recruiter and payment destination remain unverified. Company existence and search snippets do not authenticate the offer.')
    completed=sum(bool(c.get('completed')) for c in checks)
    return {'risk_indicators':{'state':state,'label':labels[state],'explanation':explanation,'evidence_ids':[e['id'] for e in observed],'scope':'Observable submitted-content and recorded evidence signals; not authenticity.'},
        'authenticity':{'state':auth_state,'label':auth_labels[auth_state],'offer_status':'UNVERIFIED','verified_claims':verified,'contradicted_evidence_ids':[e['id'] for e in contradictions],
            'explanation':auth_explanation,
            'performed':bool(verified or contradictions or review.get('independent_documents'))},
        'processing':{'submitted':len(sources) if sources else None,'processed':len(processed) if sources else None,'failed':sum(s['processing_status']=='FAILED' for s in sources),
            'awaiting_review':sum(s['processing_status']=='NEEDS_REVIEW' for s in sources),'claims_extracted':len(claims),'content_checks_recorded':bool(inspected),
            'extraction_note':'Text/claims extracted or reviewed; extraction is not independent corroboration.'},
        'coverage':{'completed':completed if checks else None,'total':len(checks) if checks else None,'percent':fusion.get('evidence_coverage',0),'criteria':checks,
            'meaning':'Completed recorded checks / applicable recorded check slots. Includes content processing; not a percentage of authenticity or a required-input checklist.'},
        'confidence_explanation':'Heuristic reliability index: distinct eligible evidence correlation groups and rule reliability weights, capped at 95; conflicting groups reduce it. Zero can mean no contributing risk/reference evidence, not failed text processing or a fraud probability. Independent corroboration is reported separately.'}
