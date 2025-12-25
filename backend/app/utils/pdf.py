# app/utils/pdf.py

import io
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER


def generate_paper_pdf(paper: dict) -> bytes:
    """
    Generate a PDF for a paper.
    EXACT logic preserved from monolithic file.
    """

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []

    # -------- TITLE --------
    title_style = styles["Heading1"]
    title_style.alignment = TA_CENTER
    story.append(Paragraph(paper["title"], title_style))
    story.append(Spacer(1, 12))

    # -------- METADATA --------
    meta = styles["Normal"]
    story.append(Paragraph(f"<b>Subject:</b> {paper['subject']}", meta))
    story.append(Paragraph(f"<b>Exam Type:</b> {paper['exam_type']}", meta))

    if paper.get("year"):
        story.append(Paragraph(f"<b>Year:</b> {paper['year']}", meta))

    story.append(Spacer(1, 24))

    # -------- QUESTIONS --------
    for idx, q in enumerate(paper["questions"], start=1):
        story.append(Paragraph(f"<b>Q{idx}.</b> {q['question_text']}", styles["Normal"]))
        story.append(Spacer(1, 6))

        for key, value in q["options"].items():
            story.append(Paragraph(f"({key}) {value}", styles["Normal"]))

        story.append(Spacer(1, 12))

    # -------- ANSWER KEY --------
    story.append(Spacer(1, 24))
    story.append(Paragraph("<b>Answer Key:</b>", styles["Heading2"]))
    story.append(Spacer(1, 12))

    answers = ", ".join(
        [f"Q{i+1}: {q['correct_answer']}" for i, q in enumerate(paper["questions"])]
    )
    story.append(Paragraph(answers, styles["Normal"]))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()
