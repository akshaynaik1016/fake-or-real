import io
from html import escape
from datetime import timezone
from datetime import datetime
from typing import Dict, Any
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

def generate_pdf_report(scan_data: Dict[str, Any]) -> bytes:
    """
    Generates a professional cybersecurity audit report PDF using reportlab.
    Includes scan metadata, trust score, risk level, verification checklist,
    critical evidence, and safe next steps.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0d1527')
    )
    
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=colors.HexColor('#06b6d4')
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#334155')
    )
    
    table_header_style = ParagraphStyle(
        'TableHeaderStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=colors.white
    )
    
    story = []
    
    # Header & Branding
    story.append(Paragraph("UNMASK — DIGITAL TRUST & SAFETY AUDIT REPORT", title_style))
    story.append(Paragraph("Don't trust. Verify. | Evidence-Based Opportunity Assessment", subtitle_style))
    story.append(Spacer(1, 15))
    
    # Metadata Table
    trust_score = scan_data.get("trust_score")
    risk_level = scan_data.get("risk_level", "UNDETERMINED")
    confidence = scan_data.get("analysis_confidence", 0)
    
    meta_data = [
        [Paragraph("<b>Report ID:</b>", body_style), Paragraph(escape(str(scan_data.get("id", "N/A"))), body_style),
         Paragraph("<b>Date/Time:</b>", body_style), Paragraph(datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"), body_style)],
        [Paragraph("<b>Concern index:</b>", body_style), Paragraph("Not scored" if trust_score is None else f"{100-trust_score}/100", body_style),
         Paragraph("<b>Risk Level:</b>", body_style), Paragraph(f"<b>{risk_level}</b>", body_style)],
        [Paragraph("<b>Confidence:</b>", body_style), Paragraph(f"{confidence}/100 (heuristic)", body_style),
         Paragraph("<b>Target Type:</b>", body_style), Paragraph(str(scan_data.get("input_type", "Text")).upper(), body_style)],
    ]
    meta_table = Table(meta_data, colWidths=[100, 160, 100, 160])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    assessment=(scan_data.get('investigation') or {}).get('assessment') or scan_data.get('assessment') or {}
    if assessment.get('risk_indicators'):
        story.append(Paragraph('OBSERVED RISK SIGNALS: '+escape(assessment['risk_indicators']['label']),styles['Heading3']))
        story.append(Paragraph(escape(assessment['risk_indicators']['explanation']),body_style))
        story.append(Paragraph('AUTHENTICITY: '+escape(assessment['authenticity']['label']),styles['Heading3']))
        story.append(Paragraph(escape(assessment['authenticity']['explanation']),body_style))
        coverage=assessment['coverage']
        story.append(Paragraph(escape(f"Coverage: {coverage['percent']}% | completed {coverage['completed'] if coverage['completed'] is not None else 'not recorded'} / {coverage['total'] if coverage['total'] is not None else 'not recorded'} recorded check slots. Source processing and extraction are separate from independent corroboration."),body_style))
        story.append(Paragraph(escape(assessment['confidence_explanation']),body_style))
    # Summary
    story.append(Paragraph("<b>EXECUTIVE FORENSIC SUMMARY</b>", styles['Heading3']))
    summary_text = scan_data.get("summary", "Analysis completed.")
    story.append(Paragraph(escape(summary_text or ""), body_style))
    story.append(Spacer(1, 15))
    
    investigation = scan_data.get("investigation") or {}
    from app.services.program_claims import claim_display
    identity_claims=[c for c in investigation.get('claims',[]) if c['claim_type'] in {'organization','organization_role','claimed_collaborator','opportunity_type','duration_range','certificate_association','placement_promise','fee_policy_disclosure'}]
    if identity_claims:
        story.append(Paragraph('SUBMITTED ORGANIZATION AND PROGRAM CLAIMS',styles['Heading3']))
        for claim in identity_claims:
            loc=claim['location']
            story.append(Paragraph(escape(claim['claim_type'].replace('_',' ')+': '+claim_display(claim['value'])),body_style))
            story.append(Paragraph(escape(f"Submitted, not independently verified | source {claim['source_id']} | page {loc.get('page','unavailable')} | characters {loc['start']}-{loc['end']} | {claim['excerpt']}"),body_style))
        story.append(Spacer(1,12))
    fusion = investigation.get("fusion") or {}
    story.append(Paragraph("<b>EVIDENCE FUSION — " + escape(fusion.get("assessment_mode", "UNAVAILABLE")) + "</b>", styles['Heading3']))
    for line in [f"Risk: {fusion.get('risk_level', 'UNKNOWN')} | Risk index: {'Not scored' if fusion.get('risk_score') is None else fusion.get('risk_score')} | Evidence reliability (heuristic): {fusion.get('confidence', 0)} | Coverage: {fusion.get('evidence_coverage', 0)}%",
                 "Specific offer authenticity remains unresolved. Heuristic scores are not calibrated probabilities."] + fusion.get("unknowns", []):
        story.append(Paragraph(escape(line), body_style))
    for result in investigation.get("research", []):
        story.append(Paragraph(escape("Research: " + result["status"] + " — " + result.get("reason", "")), body_style))
        for source in result.get("sources", []):
            story.append(Paragraph(escape(source["title"] + " | " + source["url"] + " | " + source["verification_status"]), body_style))
    story.append(Spacer(1, 15))
    # Additive case export: stored source statuses, claims and exact citations.
    for heading,lines in scan_data.get('case_sections',[]):
        story.append(Paragraph(escape(heading),styles['Heading3']))
        for line in lines:story.append(Paragraph(escape(str(line)),body_style))
        story.append(Spacer(1,6))
    # Verification Checklist Table
    story.append(Paragraph("<b>VERIFICATION CHECKLIST (RECORDED CHECKS)</b>", styles['Heading3']))
    checklist_data = [
        [Paragraph("<b>Verification Check</b>", table_header_style),
         Paragraph("<b>Status</b>", table_header_style),
         Paragraph("<b>Forensic Notes</b>", table_header_style)]
    ]
    for check in scan_data.get("verification_results", [])[:9]:
        status_label = check.get("status", "warning").upper()
        checklist_data.append([
            Paragraph(escape(check.get("check_name", "")), body_style),
            Paragraph(f"<b>{status_label}</b>", body_style),
            Paragraph(escape((check.get("details") or "")[:160]), body_style)
        ])
    
    if len(checklist_data)==1:
        checklist_data.append([Paragraph("No case-level checklist recorded",body_style),Paragraph("NOT RECORDED",body_style),Paragraph("See recorded coverage slots and preserved per-source investigations. No independent check is implied by this empty checklist.",body_style)])
    checklist_table = Table(checklist_data, colWidths=[120, 80, 320])
    checklist_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#94a3b8')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(checklist_table)
    story.append(Spacer(1, 15))
    
    # Critical Evidence Findings
    story.append(Paragraph("<b>KEY OBSERVED EVIDENCE</b>", styles['Heading3']))
    if not scan_data.get("evidence"):
        story.append(Paragraph("No qualifying concern recorded. This does not establish safety or authenticity.",body_style))
    for ev in scan_data.get("evidence", []):
        severity_label="REFERENCE OBSERVATION" if ev.get("severity")=="verified" else ev.get("severity","MODERATE").upper()
        ev_title = f"[{severity_label}] {ev.get('category', '').replace('_', ' ').title()}"
        story.append(Paragraph(f"<b>{escape(ev_title)}</b>: {escape(ev.get('evidence', ''))}", body_style))
        story.append(Paragraph(escape(f"ID: {ev.get('id', 'legacy')} | Source: {ev.get('source', '')} | {ev.get('verification_status', 'UNKNOWN')}"), body_style))
        if ev.get("explanation"):
            story.append(Paragraph(f"<i>Why it matters:</i> {escape(ev.get('explanation'))}", body_style))
        story.append(Spacer(1, 4))
        
    story.append(Spacer(1, 10))
    
    # Safety Recommendations
    story.append(Paragraph("<b>RECOMMENDED SAFETY ACTIONS</b>", styles['Heading3']))
    for action in scan_data.get("recommended_actions", [])[:5]:
        story.append(Paragraph(f"• {escape(action)}", body_style))
        
    story.append(Spacer(1, 15))
    story.append(Paragraph("<i>Disclaimer: The trust score is an algorithmic aid to decision-making based on available signals, not a legal certificate of authenticity or fraud. Verify high-impact decisions independently.</i>", ParagraphStyle('Disc', parent=styles['Normal'], fontSize=8, textColor=colors.gray)))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()
