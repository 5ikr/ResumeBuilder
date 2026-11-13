
from fpdf import FPDF


def clean_text(value):
    if value is None:
        return ""

    value = str(value)

    replacements = {
        "\u2019": "'",
        "\u2018": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2022": "-",
        "\u2026": "...",
        "\u00a0": " "
    }

    for old, new in replacements.items():
        value = value.replace(old, new)

    return value.encode("latin-1", "replace").decode("latin-1").strip()


class ResumePDF(FPDF):

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(
            w=self.w - self.l_margin - self.r_margin,
            h=8,
            text=f"Page {self.page_no()}",
            align="C"
        )


def generate_resume_pdf(personal_info, education, experience, font_color=(40, 40, 40)):

    pdf = ResumePDF(format="A4")
    pdf.set_margins(18, 16, 18)
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    content_width = pdf.w - pdf.l_margin - pdf.r_margin

    try:
        r, g, b = font_color
        pdf.set_text_color(int(r), int(g), int(b))
    except (TypeError, ValueError):
        pdf.set_text_color(40, 40, 40)

    def write_text(text, size=10, style="", indent=0, align="L"):
        text = clean_text(text)

        if not text:
            return

        available_width = content_width - indent

        pdf.set_font("Helvetica", style, size)
        pdf.set_x(pdf.l_margin + indent)

        pdf.multi_cell(
            w=available_width,
            h=5,
            text=text,
            align=align,
            new_x="LMARGIN",
            new_y="NEXT",
            wrapmode="CHAR"
        )

    def section_title(title):

        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(35, 75, 115)

        pdf.set_x(pdf.l_margin)

        pdf.cell(
            w=content_width,
            h=8,
            text=clean_text(title).upper(),
            new_x="LMARGIN",
            new_y="NEXT"
        )

        pdf.set_draw_color(190, 205, 220)

        pdf.line(
            pdf.l_margin,
            pdf.get_y(),
            pdf.w - pdf.r_margin,
            pdf.get_y()
        )

        pdf.ln(2)
        pdf.set_text_color(40, 40, 40)

    # PERSONAL INFORMATION

    name = clean_text(personal_info.get("full_name")) or "Your Name"

    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(25, 55, 85)

    write_text(name, 22, "B")

    headline = personal_info.get("headline", "")

    if headline:
        pdf.set_text_color(80, 80, 80)
        write_text(headline, 11, "B")

    contact = [
        personal_info.get(key, "")
        for key in ("email", "phone", "location", "website")
    ]

    contact = [clean_text(item) for item in contact if clean_text(item)]

    if contact:
        pdf.set_text_color(90, 90, 90)
        write_text(" | ".join(contact), 9, align="C")

    summary = personal_info.get("summary", "")

    if summary:
        section_title("Professional Profile")
        pdf.set_text_color(40, 40, 40)
        write_text(summary, 10)

    # EDUCATION

    if education:

        section_title("Education")

        entries = education.values() if isinstance(education, dict) else education

        for item in entries:

            degree = " - ".join(filter(None, [
                clean_text(item.get("degree")),
                clean_text(item.get("field_of_study"))
            ]))

            if degree:
                write_text(degree, 11, "B")

            institution = item.get("institution", "")

            if institution:
                write_text(institution, 10, "B")

            dates = " - ".join(filter(None, [
                clean_text(item.get("start_date")),
                clean_text(item.get("end_date"))
            ]))

            if dates:
                write_text(dates, 9)

            details = item.get("details", "")

            if details:
                write_text(details, 9)

            pdf.ln(2)

    # EXPERIENCE

    if experience:

        section_title("Work Experience")

        entries = experience.values() if isinstance(experience, dict) else experience

        for item in entries:

            job_title = item.get("job_title", "")

            if job_title:
                write_text(job_title, 11, "B")

            company = " | ".join(filter(None, [
                clean_text(item.get("company")),
                clean_text(item.get("location"))
            ]))

            if company:
                write_text(company, 10, "B")

            dates = " - ".join(filter(None, [
                clean_text(item.get("start_date")),
                clean_text(item.get("end_date"))
            ]))

            if dates:
                write_text(dates, 9)

            achievements = item.get("achievements", "")

            for achievement in str(achievements).splitlines():

                achievement = achievement.strip()

                if achievement:
                    write_text(
                        "- " + achievement,
                        9,
                        indent=4
                    )

            pdf.ln(2)

    return bytes(pdf.output())
