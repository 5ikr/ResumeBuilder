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
