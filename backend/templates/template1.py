# ==============================================================================
# FINAL, UPGRADED version of template1.py
# ==============================================================================
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import black
from reportlab.lib.units import inch

def get_json_prompt():
    # ✅ UPGRADED: Now uses a dictionary for 'contact' and 'skills'
    return """
    {{
      "name": "Farhan Ahmad",
      "contact": {{ "Location": "Islamabad, Pakistan", "Email": "frhanahmd665@gmail.com", "Phone": "+92 331 5733553", "LinkedIn": "linkedin.com/in/farhanahmad" }},
      "summary": "A highly motivated Machine Learning Engineer...",
      "experience": [{{ "role": "Machine Learning Engineer", "company": "TechLogix | 2022 - Present | Islamabad", "duties": ["..."] }}],
      "projects": [{{ "role": "AI Resume Optimizer", "company": "Python, Flask, React", "duties": ["..."] }}],
      "education": [{{ "degree": "Bachelors of Artificial Intelligence", "university": "Bahria University | 2022" }}],
      "skills": {{ "Technical Skills": ["Python", "TensorFlow", "PyTorch"], "Soft Skills": ["Leadership", "Problem Solving"] }}
    }}
    """

def build(resume_data):
    # This build function is now robust and handles the new structure.
    styles = getSampleStyleSheet(); styles.add(ParagraphStyle(name='HeaderName', fontSize=28, leading=34, alignment=1, spaceBottom=6, fontName='Helvetica')); styles.add(ParagraphStyle(name='HeaderContact', fontSize=10, leading=12, alignment=1, spaceBottom=20)); styles.add(ParagraphStyle(name='SectionHeader', fontSize=10, fontName='Helvetica-Bold', leading=14, spaceBottom=8, spaceBefore=6)); styles.add(ParagraphStyle(name='EntryHeader', fontSize=12, fontName='Helvetica-Bold', leading=14)); styles.add(ParagraphStyle(name='EntrySubHeader', fontSize=11, fontName='Helvetica-Oblique', spaceBottom=6)); styles.add(ParagraphStyle(name='BulletPoint', leftIndent=20, firstLineIndent=-10, spaceBottom=2, leading=14)); styles.add(ParagraphStyle(name='RightAlign', alignment=2)); styles.add(ParagraphStyle(name='SkillCategory', fontName='Helvetica-Bold', fontSize=9.5, spaceBefore=4))
    story = []
    story.append(Paragraph(resume_data.get("name", "Full Name"), styles['HeaderName']))
    # ✅ FIX: Handle the new 'contact' dictionary
    contact_dict = resume_data.get("contact", {})
    contact_info = " | ".join(filter(None, [contact_dict.get('Location'), contact_dict.get('Email'), contact_dict.get('Phone'), contact_dict.get('LinkedIn')]))
    story.append(Paragraph(contact_info, styles['HeaderContact']))
    def add_line(): story.extend([Table([['']], colWidths='100%', style=[('LINEBELOW', (0,0), (-1,-1), 1, black)]), Spacer(1, 4)])
    if resume_data.get("summary"): add_line(); story.append(Paragraph("PROFESSIONAL SUMMARY", styles['SectionHeader'])); story.append(Paragraph(resume_data.get("summary", ""), styles['Normal']))
    if resume_data.get("education"):
        add_line(); story.append(Paragraph("EDUCATION", styles['SectionHeader']))
        for edu in resume_data.get("education", []):
            if not isinstance(edu, dict): continue
            university_raw = edu.get("university", ""); university, year_info = "", ""
            if isinstance(university_raw, str) and '|' in university_raw: parts = university_raw.split('|'); university = parts[0].strip(); year_info = parts[1].strip() if len(parts) > 1 else ""
            else: university = str(university_raw)
            table = Table([[ [Paragraph(university, styles['EntryHeader']), Paragraph(edu.get("degree", ""), styles['EntrySubHeader'])], [Paragraph(str(year_info), styles['RightAlign'])] ]], colWidths=[4.5*inch, 2.5*inch])
            story.append(table); story.append(Spacer(1, 10))
    if resume_data.get("experience"):
        add_line(); story.append(Paragraph("EXPERIENCE", styles['SectionHeader']))
        for job in resume_data.get("experience", []):
            if not isinstance(job, dict): continue
            company_raw = job.get("company", ""); company, date, location = "", "", ""
            if isinstance(company_raw, str) and '|' in company_raw: parts = company_raw.split('|'); company = parts[0].strip(); date = parts[1].strip() if len(parts) > 1 else ""; location = parts[2].strip() if len(parts) > 2 else ""
            else: company = str(company_raw)
            header_table = Table([[ [Paragraph(job.get("role", ""), styles['EntryHeader']), Paragraph(company, styles['EntrySubHeader'])], [Paragraph(date, styles['RightAlign']), Paragraph(location, styles['RightAlign'])] ]], colWidths=[4.5*inch, 2.5*inch])
            story.append(header_table)
            for duty in job.get("duties", []): story.append(Paragraph(f"• {duty}", styles['BulletPoint']))
            story.append(Spacer(1, 12))
    if resume_data.get("projects"):
        add_line(); story.append(Paragraph("PROJECTS", styles['SectionHeader']))
        for proj in resume_data.get("projects", []):
            if not isinstance(proj, dict): continue
            project_header_text = f"<b>{proj.get('role', '')}</b> | <i>{proj.get('company', '')}</i>"
            story.append(Paragraph(project_header_text, styles['Normal']))
            for duty in proj.get("duties", []): story.append(Paragraph(f"• {duty}", styles['BulletPoint']))
            story.append(Spacer(1, 12))
    skills_data = resume_data.get("skills")
    if skills_data:
        add_line(); story.append(Paragraph("TECHNICAL SKILLS", styles['SectionHeader']))
        # ✅ FIX: Handle both new dictionary format and old list format
        if isinstance(skills_data, dict):
            for category, skill_list in skills_data.items():
                if skill_list and isinstance(skill_list, list):
                    story.append(Paragraph(category, styles['SkillCategory']))
                    story.append(Paragraph(", ".join(skill_list), styles['Normal']))
        elif isinstance(skills_data, list):
            story.append(Paragraph(", ".join(skills_data), styles['Normal']))
    return story