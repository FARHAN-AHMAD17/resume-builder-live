# ==============================================================================
# INSTRUCTIONS: Create a new file named template4.py and paste this code.
# This template requires an image file located at: backend/assets/template4_watermark.png
# ==============================================================================

import os
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.units import inch

def get_json_prompt():
    """Defines the JSON structure the AI must generate for this template."""
    return """
    {{
      "name": "Olivia Wilson",
      "title": "Marketing Manager",
      "contact": {{
        "phone": "+123-456-7890",
        "email": "hello@reallygreatsite.com",
        "address": "123 Anywhere St., Any City",
        "website": "www.reallygreatsite.com"
      }},
      "profile_summary": "Experienced and results-driven Marketing Manager with a proven track record in developing and executing successful marketing strategies. I am seeking a challenging role where I can contribute my skills in strategic planning, team leadership, and creative problem-solving to achieve business objectives.",
      "work_experience": [
        {{
          "company": "Borcelle Studio",
          "role": "Marketing Manager & Specialist",
          "dates": "2030 - PRESENT",
          "duties": [
            "Led the development and implementation of comprehensive marketing strategies that resulted in a 20% increase in brand visibility and a 15% growth in sales within the first year.",
            "Successfully launched and managed multiple cross-channel campaigns, including digital marketing, social media, and traditional advertising, resulting in improved customer acquisition and retention rates."
          ]
        }}
      ],
      "education": [
        {{
          "dates": "2029 - 2030",
          "university": "BORCELLE UNIVERSITY",
          "degree": "Master of Business Management",
          "details": []
        }},
        {{
          "dates": "2025 - 2029",
          "university": "BORCELLE UNIVERSITY",
          "degree": "Bachelor of Business Management",
          "details": ["GPA: 3.8 / 4.0"]
        }}
      ],
      "skills": [
        "Project Management", "Public Relations", "Teamwork", "Time Management", "Leadership"
      ],
      "languages": [
        {{"language": "English", "level": "Fluent"}},
        {{"language": "French", "level": "Fluent"}},
        {{"language": "German", "level": "Basics"}}
      ]
    }}
    """

def build(resume_data):
    """Builds the 'Olivia Wilson' clean, modern resume."""
    story = []
    styles = getSampleStyleSheet()
    grey = HexColor("#4D4D4D")

    # --- Define Styles ---
    styles.add(ParagraphStyle(name='MainName', fontName='Helvetica', fontSize=36, textColor=black, alignment=1, spaceAfter=6))
    styles.add(ParagraphStyle(name='MainTitle', fontName='Helvetica', fontSize=10, textColor=grey, letterSpacing=2, alignment=1))
    styles.add(ParagraphStyle(name='LeftHeader', fontName='Helvetica-Bold', fontSize=11, textColor=black, spaceAfter=10))
    styles.add(ParagraphStyle(name='LeftSubHeader', fontName='Helvetica-Bold', fontSize=10, textColor=black, spaceAfter=2))
    styles.add(ParagraphStyle(name='LeftText', fontName='Helvetica', fontSize=9, textColor=grey, leading=12))
    styles.add(ParagraphStyle(name='RightHeader', fontName='Helvetica-Bold', fontSize=11, textColor=black, spaceAfter=10))
    styles.add(ParagraphStyle(name='RightCompany', fontName='Helvetica-Bold', fontSize=10, textColor=black))
    styles.add(ParagraphStyle(name='RightRole', fontName='Helvetica', fontSize=9, textColor=grey, spaceAfter=4))
    styles.add(ParagraphStyle(name='RightDates', fontName='Helvetica', fontSize=9, textColor=grey, alignment=2))
    styles.add(ParagraphStyle(name='RightBullet', leftIndent=12, firstLineIndent=-12, spaceAfter=4, textColor=grey, leading=14))

    # ==================================================
    #                BUILD HEADER
    # ==================================================
    header_content = [
        Paragraph(resume_data.get('name', '').upper(), styles['MainName']),
        Paragraph(resume_data.get('title', '').upper(), styles['MainTitle']),
    ]
    try:
        backend_root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        image_path = os.path.join(backend_root_dir, 'assets', 'template4_watermark.png')
        if not os.path.exists(image_path):
            raise FileNotFoundError("Watermark image not found.")
        
        # Create a table to layer the text over the image
        watermark_img = Image(image_path, width=2.5*inch, height=1.2*inch)
        header_table = Table(
            [[[watermark_img], header_content]], 
            colWidths='100%',
            style=[
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]
        )
        story.append(header_table)
    except Exception as e:
        print(f"WARNING: Could not load watermark for template 4. Error: {e}")
        story.extend(header_content) # Add text without watermark as a fallback

    story.append(Spacer(1, 0.2*inch))
    story.append(HRFlowable(width="100%", thickness=0.5, color=grey))
    story.append(Spacer(1, 0.2*inch))

    # ==================================================
    #                BUILD BODY (Two Columns)
    # ==================================================
    left_col_content = []
    right_col_content = []

    # --- Populate Left Column ---
    contact = resume_data.get('contact', {})
    if contact:
        left_col_content.append(Paragraph("CONTACT", styles['LeftHeader']))
        contact_icons = {'phone': '&#9742;', 'email': '&#9993;', 'address': '&#128205;', 'website': '&#127760;'}
        for key in ['phone', 'email', 'address', 'website']:
            if contact.get(key):
                icon = contact_icons.get(key, '')
                text = f"{icon} &nbsp; {contact[key]}"
                left_col_content.append(Paragraph(text, styles['LeftText']))
                left_col_content.append(Spacer(1, 6))
        left_col_content.append(Spacer(1, 0.2*inch))
        left_col_content.append(HRFlowable(width="90%", thickness=0.5, color=HexColor('#CCCCCC')))
        left_col_content.append(Spacer(1, 0.2*inch))
        
    education = resume_data.get('education', [])
    if education:
        left_col_content.append(Paragraph("EDUCATION", styles['LeftHeader']))
        for edu in education:
            if isinstance(edu, dict):
                left_col_content.append(Paragraph(edu.get('dates', ''), styles['LeftText']))
                left_col_content.append(Paragraph(edu.get('university', '').upper(), styles['LeftSubHeader']))
                left_col_content.append(Paragraph(edu.get('degree', ''), styles['LeftText']))
                for detail in edu.get('details', []):
                    left_col_content.append(Paragraph(f"• {detail}", styles['RightBullet']))
                left_col_content.append(Spacer(1, 0.2*inch))
        left_col_content.append(HRFlowable(width="90%", thickness=0.5, color=HexColor('#CCCCCC')))
        left_col_content.append(Spacer(1, 0.2*inch))

    skills = resume_data.get('skills', [])
    if skills:
        left_col_content.append(Paragraph("SKILLS", styles['LeftHeader']))
        for skill in skills:
            left_col_content.append(Paragraph(f"• {skill}", styles['RightBullet']))
        left_col_content.append(Spacer(1, 0.2*inch))
        left_col_content.append(HRFlowable(width="90%", thickness=0.5, color=HexColor('#CCCCCC')))
        left_col_content.append(Spacer(1, 0.2*inch))
        
    languages = resume_data.get('languages', [])
    if languages:
        left_col_content.append(Paragraph("LANGUAGES", styles['LeftHeader']))
        for lang in languages:
            if isinstance(lang, dict):
                text = f"• {lang.get('language', '')}: {lang.get('level', '')}"
                left_col_content.append(Paragraph(text, styles['RightBullet']))

    # --- Populate Right Column ---
    if resume_data.get('profile_summary'):
        right_col_content.append(Paragraph("PROFILE SUMMARY", styles['RightHeader']))
        right_col_content.append(Paragraph(resume_data.get('profile_summary', ''), styles['LeftText']))
        right_col_content.append(Spacer(1, 0.2*inch))
        right_col_content.append(HRFlowable(width="100%", thickness=0.5, color=HexColor('#CCCCCC')))
        right_col_content.append(Spacer(1, 0.2*inch))

    experience = resume_data.get('work_experience', [])
    if experience:
        right_col_content.append(Paragraph("WORK EXPERIENCE", styles['RightHeader']))
        for job in experience:
            if isinstance(job, dict):
                # Create a table to align dates to the right
                job_header_table = Table(
                    [[Paragraph(job.get('company', '').upper(), styles['RightCompany']), Paragraph(job.get('dates', ''), styles['RightDates'])]],
                    colWidths=['70%', '30%']
                )
                right_col_content.append(job_header_table)
                right_col_content.append(Paragraph(job.get('role', ''), styles['RightRole']))
                for duty in job.get('duties', []):
                    right_col_content.append(Paragraph(f"• {duty}", styles['RightBullet']))
                right_col_content.append(Spacer(1, 0.2*inch))

    # --- Assemble Main Body Table ---
    body_table = Table(
        [[left_col_content, right_col_content]],
        colWidths=[2.5*inch, 5.0*inch],
        splitByRow=1
    )
    body_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LINEAFTER', (0, 0), (0, -1), 0.5, grey),
        ('RIGHTPADDING', (0, 0), (0, -1), 15),
        ('LEFTPADDING', (1, 0), (1, -1), 15),
    ]))
    story.append(body_table)

    return story