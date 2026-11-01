from app.services.investigator_context import canonical_context
from app.services.program_claims import claim_display
from app.security.redaction import redact_sensitive_credentials

def answer_investigator_query(question,scan_detail):
    """Deterministic answers from the same persisted claims/evidence as result views."""
    ctx=canonical_context(scan_detail);q=question.casefold();refs=[];citations=[];ids=[]
    org='; '.join(ctx['organizations'])
    identity=('Claimed organization: '+org+'.') if org else 'Organization not identified in the available evidence.'
    assessment=ctx['assessment'].get('label') or 'Undetermined'
    def cite(e):
        if e.get('id') and e['id'] not in ids:ids.append(e['id'])
        if e.get('evidence') and e['evidence'] not in refs:refs.append(e['evidence'])
        citations.extend(e.get('citations') or [])
    def findings(items):
        for e in items[:4]:cite(e)
        return '\n'.join('• '+e['evidence'] for e in items[:4])
    scope='Specific offer authenticity, recruiter authorization and the applicant’s payment destination remain unresolved unless separately supported in their exact scope. Company existence, domain ownership and offer authorization are different checks.'
    if 'missing' in q:
        missing=[c['name']+': '+c.get('reason','unresolved') for c in ctx['assessment'].get('coverage',{}).get('criteria',[]) if not c.get('completed')]
        answer=identity+'\nMissing or unresolved evidence:\n'+'\n'.join('• '+x for x in (missing or ctx['unknowns'] or ['Independent confirmation of the organization, recruiter and exact offer is missing.'])[:8])
    elif 'contradict' in q or 'conflict' in q:
        conflicts=[f for f in ctx['comparisons'] if f['classification'] in {'CONFIRMED_CONTRADICTION','POSSIBLE_INCONSISTENCY'}]
        answer=identity+'\n'+('\n'.join(f['description'] for f in conflicts[:5]) or 'No comparable source contradiction is recorded. Missing fields and new information are not contradictions.')
        for f in conflicts[:5]:citations.extend(f['citations'])
    elif 'low concern' in q or 'difference' in q and 'verified' in q:
        answer=identity+'\nLow observed concern describes the inspected content: few or no suspicious signals were found. Verified claims require scoped independent evidence. A normal-looking description can remain unverified, and processing text is not authentication.'
    elif any(k in q for k in ['partner','collaborat','certificate','placement']):
        selected=[c for c in ctx['claims'] if c['claim_type'] in {'claimed_collaborator','certificate_association','placement_promise'}]
        answer=identity+'\n'+'\n'.join('• Submitted '+c['claim_type'].replace('_',' ')+': '+claim_display(c['value']) for c in selected[:12])+'\nPartnerships and certificate associations have not been authenticated. Placement-assistance wording does not establish guaranteed job placement.'
        citations.extend({'source_id':c['source_id'],'source_title':'Submitted program claim','claim_id':c['id'],'excerpt':c['excerpt'],**c['location']} for c in selected)
    elif any(k in q for k in ['next','verify','can i apply']):
        actions=ctx['recommendations'][:4]
        answer=identity+'\n'+('\n'.join('• '+a['title']+': '+(a.get('unavailable_reason') or a['reason']) for a in actions) or 'Compare the exact notice, role, fee/exemptions and payment destination using independently obtained official contact details.')
    elif any(k in q for k in ['fee','payment','deposit','bond']):
        items=[e for e in ctx['evidence'] if any(k in e.get('category','') for k in ['payment','policy','fee'])]
        answer=identity+'\n'+(findings(items) or 'No payment concern is recorded in this snapshot; missing information does not establish authorization.')+'\nTraining fees are not always fraudulent. A disclosed fee still requires checking the recipient, terms and authorization. An ordinary application fee is not proof of fraud. A contractual liability is not an upfront demand. Compare category, stage, tax basis, recipient and channel before paying.'
    elif any(k in q for k in ['company','genuine','real','legit','organization','firm']):
        items=[e for e in ctx['evidence'] if 'organization' in e.get('category','') or 'identity' in e.get('category','')]
        answer=identity+'\n'+(findings(items) or 'No independent company/domain verification is recorded here. A submitted name is a claim, not proof that this recruiter represents the company.')
    elif any(k in q for k in ['domain','url','website','dns']):
        items=[e for e in ctx['evidence'] if 'domain' in e.get('category','') or 'url' in e.get('category','')]
        answer=('Submitted domains/links: '+', '.join(ctx['domains'])+'.\n' if ctx['domains'] else 'No domain identified in the available evidence.\n')+(findings(items) or 'No domain risk result is recorded. DNS, ownership and unavailable network checks must not be assumed successful.')
    elif any(k in q for k in ['avoid','share','otp','password','aadhaar','sensitive']):
        items=[e for e in ctx['evidence'] if 'sensitive' in e.get('category','')]
        answer=(findings(items)+'\n' if items else '')+'Do not send passwords, OTPs or PINs to a recruiter. Creating or using your own application-account password is different from disclosing it. Verify the recruiter and application destination independently before sending identity documents.'
    else:
        items=[e for e in ctx['evidence'] if e.get('severity') in {'high','critical','moderate'}]
        answer=identity+'\nAssessment: '+assessment+'.\n'+(findings(items) or 'No significant concern is recorded in the available evidence. This does not establish safety.')
        conflicts=ctx['comparisons'][:2]
        for f in conflicts:
            if f['classification'] in {'CONFIRMED_CONTRADICTION','POSSIBLE_INCONSISTENCY'}:
                answer+='\n'+f['description'];citations.extend(f['citations'])
    review=ctx['notice_review'];corroborated=[c for c in review.get('claim_results',[]) if c['status']=='INDEPENDENTLY_CORROBORATED']
    if corroborated:
        answer+='\nIndependently corroborated fields in the exact-notice comparison: '+', '.join(sorted({c['claim_type'].replace('_',' ') for c in corroborated}))+'. This is limited to those fields as retrieved.'
        for c in corroborated:citations.extend(c['citations'])
    if ctx['partners']:answer+='\nClaimed collaborators: '+', '.join(ctx['partners'])+'. These are submitted associations, not the primary organizer or verified affiliations.'
    if any(c['claim_type']=='fee_policy_disclosure' for c in ctx['claims']):
        from app.services.program_claims import program_unknowns
        answer+='\n'+' '.join(program_unknowns(ctx['claims']))
    a=ctx['assessment'];risk=a.get('risk_indicators',{}).get('label','Insufficient evidence to assess');auth=a.get('authenticity',{}).get('label','Unverified')
    if not answer.startswith(identity):answer=identity+'\n'+answer
    answer+='\nRisk indicators: '+risk+'. Authenticity: '+auth+'. Overall assessment: '+assessment+'.'
    answer+='\n'+scope
    citations=list({(c.get('source_id'),c.get('claim_id'),c.get('start'),c.get('end')):c for c in citations}.values())
    return {'answer':redact_sensitive_credentials(answer),'grounded_in_evidence':True,'evidence_referenced':refs,
        'evidence_ids':ids,'citations':citations,'confidence_note':'Deterministic explanation of the current stored snapshot; no new lookup or calibrated probability.','context_revision':(scan_detail.get('investigation') or scan_detail).get('revision')}
