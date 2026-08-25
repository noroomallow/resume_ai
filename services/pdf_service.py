import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_resume_pdf(resume_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    name_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=4
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor('#6366F1'),
        spaceAfter=8
    )

    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontSize=9.5,
        leading=13,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#0F172A'),
        spaceBefore=10,
        spaceAfter=4
    )

    elements = []

    # Header Section
    elements.append(Paragraph(resume_data.get('full_name', 'Unnamed Candidate'), name_style))
    elements.append(Paragraph(resume_data.get('professional_title', ''), subtitle_style))
    
    contact_line = f"{resume_data.get('email', '')} | {resume_data.get('phone', '')} | {resume_data.get('location', '')}"
    elements.append(Paragraph(contact_line, body_style))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#E2E8F0'), spaceAfter=10))

    # Professional Summary
    if resume_data.get('summary'):
        elements.append(Paragraph("PROFESSIONAL SUMMARY", h2_style))
        elements.append(Paragraph(resume_data['summary'], body_style))

    # Experience
    if resume_data.get('experience'):
        elements.append(Paragraph("EXPERIENCE", h2_style))
        for exp in resume_data['experience']:
            title_text = f"<b>{exp.get('position')}</b> - {exp.get('company')} ({exp.get('start_date', '')} - {exp.get('end_date', '')})"
            elements.append(Paragraph(title_text, body_style))
            if exp.get('description'):
                elements.append(Paragraph(exp['description'].replace('\n', '<br/>'), body_style))

    # Education
    if resume_data.get('education'):
        elements.append(Paragraph("EDUCATION", h2_style))
        for ed in resume_data['education']:
            ed_text = f"<b>{ed.get('degree')}</b>, {ed.get('institution')} ({ed.get('start_date', '')} - {ed.get('end_date', '')})"
            elements.append(Paragraph(ed_text, body_style))

    # Skills
    if resume_data.get('skills'):
        elements.append(Paragraph("SKILLS", h2_style))
        skills_str = ", ".join([sk.get('skill_name') for sk in resume_data['skills']])
        elements.append(Paragraph(skills_str, body_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer