from io import BytesIO
import unittest

from streamlit.testing.v1 import AppTest

from resume_upload import extract_resume_text, parse_resume_text


class ResumeUploadTest(unittest.TestCase):
    def test_parse_contact_details(self):
        cases = [
            ("RESUME\nPranav Ramkumar\npranav@example.com\n+91 98765 43210", {
                "full_name": "Pranav Ramkumar", "email": "pranav@example.com", "phone": "+91 98765 43210"}),
            ("Full Name: Ana O'Neil\nEmail: ana.oneil+work@example.co.uk\nPhone: (415) 555-1234", {
                "full_name": "Ana O'Neil", "email": "ana.oneil+work@example.co.uk", "phone": "(415) 555-1234"}),
            ("José García | jose@example.com\n2020 - 2024", {
                "full_name": "José García", "email": "jose@example.com"}),
            ("Education\n2020 - 2024\nSkills", {}),
            ("", {}),
        ]
        for text, expected in cases:
            with self.subTest(text=text):
                self.assertEqual(parse_resume_text(text), expected)

    def test_text_files_and_bad_uploads(self):
        for encoding in ("utf-8-sig", "utf-16"):
            upload = BytesIO("José García\njose@example.com".encode(encoding))
            upload.name = "resume.TXT"
            upload.seek(5)
            self.assertEqual(extract_resume_text(upload), "José García\njose@example.com")
        for name, content in (("empty.txt", b"  "), ("bad.pdf", b"not a pdf"),
                              ("bad.txt", b"\x80\x81"), ("resume.doc", b"Hello")):
            upload = BytesIO(content)
            upload.name = name
            with self.subTest(name=name), self.assertRaises(ValueError):
                extract_resume_text(upload)

    def test_pdf_text(self):
        content = b"BT /F1 12 Tf 72 720 Td (Alex Smith) Tj 0 -20 Td (alex@example.com) Tj ET"
        pdf = (
            b"%PDF-1.4\n1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
            b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
            b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
            b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >> endobj\n"
            b"4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n"
            b"5 0 obj << /Length " + str(len(content)).encode() + b" >> stream\n" + content
            + b"\nendstream endobj\ntrailer << /Root 1 0 R >>\n%%EOF"
        )
        upload = BytesIO(pdf)
        upload.name = "resume.pdf"
        self.assertEqual(parse_resume_text(extract_resume_text(upload)), {
            "full_name": "Alex Smith", "email": "alex@example.com"
        })
