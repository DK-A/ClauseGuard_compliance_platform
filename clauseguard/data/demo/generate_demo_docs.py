import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_pdf(filename: str, title: str, paragraphs: list):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    doc = SimpleDocTemplate(filename, pagesize=letter, rightMargin=54, leftMargin=54, topMargin=54, bottomMargin=54)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#2563eb'),
        spaceAfter=20
    )
    
    heading_style = ParagraphStyle(
        'DocHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1f1f24'),
        spaceBefore=12,
        spaceAfter=6
    )
    
    body_style = ParagraphStyle(
        'DocBody',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#343439'),
        spaceAfter=8
    )

    story = [Paragraph(title, title_style), Spacer(1, 10)]
    
    for item in paragraphs:
        if item.startswith("### "):
            story.append(Spacer(1, 8))
            story.append(Paragraph(item.replace("### ", ""), heading_style))
        else:
            story.append(Paragraph(item, body_style))
            
    doc.build(story)
    print(f"Generated PDF: {filename}")

def main():
    demo_dir = "uploaded_data"
    os.makedirs(demo_dir, exist_ok=True)
    
    # 1. HR Policy
    hr_policy = [
        "### Section 1. Scope & Guidelines",
        "This policy governs all active corporate members of the organization under Cambridge Institute of Technology guidelines.",
        "### Section 2. Telecommuting Operations",
        "2.1 Remote work requests requires written manager approval at least forty-eight (48) hours in advance of the telecommuting start date.",
        "### Section 3. Grievance Redressal Procedures",
        "3.1 All employee grievances must be submitted strictly in writing within seven (7) calendar days of the occurrence of the incident.",
        "### Section 4. Annual Leave Policy",
        "4.1 Annual leave must be taken in the calendar year in which it accrues. No carryover of leaves to the subsequent year is permitted.",
        "### Section 5. Operational Notice Period",
        "5.1 Resigning employees are obligated to provide a minimum notice period of one (1) month prior to departure."
    ]
    create_pdf(os.path.join(demo_dir, "hr_policy.pdf"), "Corporate HR Policy & Guidelines v4.0", hr_policy)
    
    # 2. Employment Contract
    employment_contract = [
        "### Section 1. Terms of Service",
        "This employment contract outlines the mutual terms between ClauseGuard Corp and the individual client member.",
        "### Section 2. Telecommuting Rights",
        "2.4 Employees are entitled to same-day remote work requests, requiring only immediate email notice to their team coordinator.",
        "### Section 3. Grievances",
        "8.3 Employees may raise grievances verbally or in writing. The company will acknowledge and review grievances within ten (10) working days.",
        "### Section 4. Leave Benefits",
        "12.1 Employees are permitted to carry over accrued annual leaves for up to an eighteen (18) month carryover period.",
        "### Section 5. Termination Notice",
        "14.2 The employee agrees to provide a mandatory notice period of three (3) months prior to formal contract termination."
    ]
    create_pdf(os.path.join(demo_dir, "employment_contract.pdf"), "Standard Employment Agreement & Covenant", employment_contract)
    
    # 3. SOP Operations
    sop_operations = [
        "### Section 1. System Logging Protocols",
        "This Standard Operating Procedure defines operational logging and security tracking on all edge nodes.",
        "### Section 2. Data Archiving",
        "2.1 System logs and active transactions must be retained for a duration of seven (7) years to comply with financial audits.",
        "### Section 3. Incident Management",
        "3.3 Any detected system security breach or data compromise must be escalated and disclosed to the regulators within twenty-four (24) hours."
    ]
    create_pdf(os.path.join(demo_dir, "sop_operations.pdf"), "SOP - System Infrastructure & Data Archiving", sop_operations)
    
    # 4. Compliance GDPR
    compliance_gdpr = [
        "### Section 1. Data Minimization",
        "This GDPR guidelines governs all personal identifiers saved on our locally encrypted storage systems.",
        "### Section 2. Data Retention Limits",
        "4.2 Log files containing user information shall be deleted within three (3) years to comply with data minimization requirements.",
        "### Section 3. Breach Disclosures",
        "6.1 In the event of a personal data breach, the company will notify data protection authorities within seventy-two (72) hours of discovery."
    ]
    create_pdf(os.path.join(demo_dir, "compliance_gdpr.pdf"), "GDPR Privacy & Data Sovereignty Policy", compliance_gdpr)

if __name__ == '__main__':
    main()
