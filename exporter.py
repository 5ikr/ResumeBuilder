"""Print-safe Unicode PDFs built from the same semantic content as preview."""
from pathlib import Path
from fpdf import FPDF
from preview import resume_blocks, safe_link
from profiles import normalise_profile

FONT_DIR = Path(__file__).parent / 'assets' / 'fonts'


def clean_text(value):
    return str(value or '').replace('\t', '    ').strip()


class ResumePDF(FPDF):
    def footer(self):
        self.set_y(-13)
        self.set_font('Resume', '', 8)
        self.set_text_color(120, 120, 120)
        self.cell(self.epw, 6, f'Page {self.page_no()}', align='C')


def generate_resume_pdf(personal_info, education, experience, font_color=(40, 40, 40), **extra):
    profile = normalise_profile(dict(personal_info=personal_info, education=education, experience=experience, **extra))
    template = profile['settings']['template']
    try:
        r, g, b = font_color
        rgb = tuple(max(0, min(255, int(c))) for c in (r, g, b))
    except (TypeError, ValueError, OverflowError):
        rgb = (40, 40, 40)
    pdf = ResumePDF(format='A4')
    pdf.set_margins(19 if template != 'Technical Resume' else 16, 17, 19 if template != 'Technical Resume' else 16)
    pdf.set_auto_page_break(True, 19)
    family = 'NotoSerif' if template == 'Classic Professional' else 'NotoSans'
    for style, suffix in (('', 'Regular'), ('B', 'Bold')):
        pdf.add_font('Resume', style, str(FONT_DIR / f'{family}-{suffix}.ttf'))
    pdf.add_page()
    pdf.set_title(f"{personal_info.get('full_name', 'Resume')} - Resume")
    pdf.set_author(personal_info.get('full_name', ''))
    compact = template == 'Technical Resume'
    leading = 4.2 if compact else 4.6
    blocks = resume_blocks(profile)
    for block in blocks:
        text = clean_text(block.text)
        style, size = '', 9.5
        if block.kind == 'name':
            style, size = 'B', 23 if template != 'Technical Resume' else 21
        elif block.kind == 'headline':
            size = 11
        elif block.kind == 'section':
            style, size = 'B', 10.5
            # Reserve the heading and at least the next two lines of content.
            if pdf.get_y() + 30 > pdf.h - pdf.b_margin:
                pdf.add_page()
            pdf.ln(3 if compact else 4)
            text = text.upper()
        elif block.kind == 'entry':
            style, size = 'B', 10
            if pdf.get_y() + 17 > pdf.h - pdf.b_margin:
                pdf.add_page()
            pdf.ln(1.5)
        elif block.kind in ('contact', 'date'):
            size = 8.5
        pdf.set_font('Resume', style, size)
        # Never silently omit unsupported glyphs.
        cmap = pdf.current_font.cmap
        unsupported = {c for c in text if not c.isspace() and ord(c) not in cmap}
        if unsupported:
            raise ValueError('The bundled font does not cover these characters: ' + ' '.join(sorted(unsupported)) + '. Use supported text or configure an appropriate font.')
        accent = template == 'Modern Minimal' and block.kind in ('name', 'section')
        pdf.set_text_color(*(rgb if not accent else (164, 68, 37)))
        indent = 5 if block.kind == 'bullet' else 0
        if block.kind == 'bullet':
            if pdf.will_page_break(leading):
                pdf.add_page()
            pdf.set_x(pdf.l_margin + 1)
            pdf.cell(3, leading, '•')
        pdf.set_x(pdf.l_margin + indent)
        link = block.link
        if block.kind == 'contact':
            # Render contact items separately for individual clickable annotations.
            first = True
            for key in ('email', 'phone', 'location', 'website'):
                value = personal_info.get(key, '')
                if value:
                    target = ('mailto:' + value) if key == 'email' else safe_link(value) if key == 'website' else ''
                    if not first:
                        pdf.write(leading, ' | ')
                    pdf.write(leading, clean_text(value), link=target, wrapmode='CHAR' if pdf.get_string_width(value) > pdf.epw else 'WORD')
                    first = False
            pdf.ln(leading)
            continue
        # WORD wrapping normally; long unbroken URLs/identifiers use character wrapping.
        longest = max(text.split(), key=len, default='')
        wrapmode = 'CHAR' if pdf.get_string_width(longest) > pdf.epw - indent else 'WORD'
        pdf.multi_cell(pdf.epw - indent, max(leading, size * .3), text, link=link,
                       new_x='LMARGIN', new_y='NEXT', wrapmode=wrapmode)
        if block.kind == 'section':
            pdf.set_draw_color(205, 200, 190)
            pdf.line(pdf.l_margin, pdf.get_y() + .8, pdf.w - pdf.r_margin, pdf.get_y() + .8)
            pdf.ln(2)
    return bytes(pdf.output())
