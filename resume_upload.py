from io import BytesIO
from pathlib import Path

import pdfplumber


def extract_resume_text(uploaded_file):
    content = uploaded_file.getvalue()
    suffix = Path(uploaded_file.name).suffix.lower()
    try:
        if suffix == ".pdf":
            with pdfplumber.open(BytesIO(content)) as pdf:
                text = "\n".join(page.extract_text() or "" for page in pdf.pages)
        elif suffix == ".txt":
            encoding = "utf-16" if content.startswith((b"\xff\xfe", b"\xfe\xff")) else "utf-8-sig"
            text = content.decode(encoding)
        else:
            raise ValueError("Choose a PDF or TXT file.")
    except UnicodeDecodeError as error:
        raise ValueError("Save your text file as UTF-8 or UTF-16 and try again.") from error
    except ValueError:
        raise
    except Exception as error:
        raise ValueError("Could not read this file. Try another PDF or a text file.") from error
    if not text.strip():
        raise ValueError("No text found. For scanned PDFs, upload a text version instead.")
    return text
