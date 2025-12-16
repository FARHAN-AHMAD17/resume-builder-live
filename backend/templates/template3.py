# ==============================================================================
# INSTRUCTIONS: This is the final, fully polished version of template3.py.
# It fixes the line height of the name to prevent words from merging.
# ==============================================================================

import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import inch
from reportlab.platypus.flowables import KeepInFrame

def get_json_prompt():
    # ✅ UPGRADED to the universal structure
    return """
    {{
      "name": "Farhan Ahmad",
      "title": "Machine Learning Engineer",
      "contact": {{ "phone": "+92 331 5733553", "email": "frhanahmd665@gmail.com", "address": "Islamabad, Pakistan", "website": "linkedin.com/in/farhanahmad" }},
      "profile_summary": "A highly motivated Machine Learning Engineer...",
      "work_experience": [{{ "company": "Systems Limited", "role": "Cloud Intern", "dates": "2025", "duties": ["..."] }}],
      "education": [{{ "dates": "2020-2024", "university": "Bahria University", "degree": "Bachelors of AI", "details": ["CGPA: 3.8"] }}],
      "skills": {{ "Technical Skills": ["Python", "TensorFlow"], "Soft Skills": ["Leadership"] }},
      "languages": [{{ "language": "English", "level": "Fluent" }}]
    }}
    """

def build(resume_data):
    """Builds the 'Kai Carter' modern, graphic-heavy resume."""
    story = []
    styles = getSampleStyleSheet()
    
    # --- Define Styles ---
    # ✅ THE FIX IS HERE: Added 'leading=34' to ensure proper line spacing for the large font.
    styles.add(ParagraphStyle(name='HeaderName', fontName='Helvetica-Bold', fontSize=28, textColor=white, leading=34, spaceAfter=14))
    
    styles.add(ParagraphStyle(name='HeaderTitle', fontName='Helvetica', fontSize=10, textColor=white, letterSpacing=2))
    styles.add(ParagraphStyle(name='HeaderContactTitle', fontName='Helvetica-Bold', fontSize=10, textColor=white, spaceBefore=20, spaceAfter=4))
    styles.add(ParagraphStyle(name='HeaderContactKey', fontName='Helvetica-Bold', fontSize=9, textColor=white))
    styles.add(ParagraphStyle(name='HeaderContactVal', fontName='Helvetica', fontSize=9, textColor=white))
    styles.add(ParagraphStyle(name='T3_BodyHeader', fontName='Helvetica-Bold', fontSize=11, spaceAfter=8))
    styles.add(ParagraphStyle(name='T3_BodyCompany', fontName='Helvetica-Bold', fontSize=10, spaceAfter=2))
    styles.add(ParagraphStyle(name='T3_BodyDates', fontName='Helvetica', fontSize=9, textColor=HexColor("#555555"), spaceAfter=4))
    styles.add(ParagraphStyle(name='T3_BodyText', fontName='Helvetica', fontSize=9.5, leading=12))
    styles.add(ParagraphStyle(name='T3_BodyListItem', fontName='Helvetica', fontSize=9.5, leading=14))

    # All the rendering logic below is correct and does not need to be changed.
    header_left_content = [
        Paragraph(resume_data.get('name', '').upper(), styles['HeaderName']),
        Paragraph(resume_data.get('title', '').upper(), styles['HeaderTitle']),
        Paragraph("CONTACT", styles['HeaderContactTitle']),
    ]
    contact_data = []
    contact = resume_data.get('contact', {})
    for key in ["Phone", "Website", "Email"]:
        if contact.get(key):
            row = [Paragraph(f"{key.upper()}:", styles['HeaderContactKey']), Paragraph(contact[key], styles['HeaderContactVal'])]
            contact_data.append(row)
    if contact_data:
        contact_table = Table(contact_data, colWidths=[0.8*inch, 2.5*inch])
        header_left_content.append(contact_table)
    
    header_right_content = []
    try:
        backend_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        image_path = os.path.join(backend_root_dir, 'assets', 'template3_graphic.png')
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found at expected path: {image_path}")
        img = Image(image_path, width=2.5*inch, height=1.5*inch)
        img.hAlign = 'RIGHT'
        header_right_content.append(img)
    except Exception as e:
        print(f"FATAL ERROR: Could not load template3_graphic.png. Error: {e}")
        error_message = Paragraph("!! GRAPHIC MISSING !!", styles['Normal'])
        header_right_content.append(error_message)

    header_table = Table([[header_left_content, header_right_content]], colWidths=['50%', '50%'],
        style=[
            ('BACKGROUND', (0, 0), (-1, -1), black), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 15), ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 10), ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ])
    story.append(header_table)

    left_col_content = []
    right_col_content = []

    if resume_data.get('profile'):
        left_col_content.append(Paragraph("PROFILE", styles['T3_BodyHeader']))
        left_col_content.append(Paragraph(resume_data.get('profile', ''), styles['T3_BodyText']))
        left_col_content.append(Spacer(1, 0.3*inch))
    experience = resume_data.get('work_experience', [])
    if experience:
        left_col_content.append(Paragraph("WORK EXPERIENCE", styles['T3_BodyHeader']))
        for job in experience:
            if isinstance(job, dict):
                company_role = f"{job.get('company', '').upper()}, {job.get('role', '').upper()}"
                left_col_content.append(Paragraph(company_role, styles['T3_BodyCompany']))
                left_col_content.append(Paragraph(job.get('dates', ''), styles['T3_BodyDates']))
                left_col_content.append(Paragraph(job.get('duties', ''), styles['T3_BodyText']))
                left_col_content.append(Spacer(1, 0.2*inch))
    
    education = resume_data.get('education', [])
    if education:
        right_col_content.append(Paragraph("EDUCATION", styles['T3_BodyHeader']))
        for edu in education:
            if isinstance(edu, dict):
                right_col_content.append(Paragraph(edu.get('university', '').upper(), styles['T3_BodyCompany']))
                right_col_content.append(Paragraph(edu.get('dates', ''), styles['T3_BodyDates']))
                right_col_content.append(Paragraph(edu.get('details', '').replace('\n', '<br/>'), styles['T3_BodyText']))
                right_col_content.append(Spacer(1, 0.2*inch))
    
    skills = resume_data.get('skills', [])[:10]  # Limit to first 10 skills
    if skills:
        right_col_content.append(Spacer(1, 0.3*inch))
        right_col_content.append(Paragraph("SKILLS", styles['T3_BodyHeader']))
        for skill in skills:
            right_col_content.append(Paragraph(skill, styles['T3_BodyListItem']))
            
    hobbies = resume_data.get('hobbies', [])
    if hobbies:
        right_col_content.append(Spacer(1, 0.3*inch))
        right_col_content.append(Paragraph("HOBBIES", styles['T3_BodyHeader']))
        for hobby in hobbies:
            right_col_content.append(Paragraph(hobby, styles['T3_BodyListItem']))

    left_col_framed = KeepInFrame(4.5 * inch, 10 * inch, left_col_content)
    right_col_framed = KeepInFrame(2.5 * inch, 10 * inch, right_col_content)
    
    body_table = Table([[left_col_framed, right_col_framed]], colWidths=[4.8*inch, 2.7*inch],
        style=[
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (0, 0), 25), ('RIGHTPADDING', (0, 0), (0, 0), 15),
            ('LEFTPADDING', (1, 0), (1, 0), 15), ('RIGHTPADDING', (1, 0), (1, 0), 25),
            ('TOPPADDING', (0, 0), (-1, -1), 25),
            ('LINEAFTER', (0, 0), (0, -1), 1, black),
        ])
    story.append(body_table)

    return story