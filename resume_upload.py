from io import BytesIO
from pathlib import Path
import re

import pdfplumber
import streamlit as st


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


def parse_resume_text(text):
    result = {}
    email = re.search(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", text)
    if email:
        result["email"] = email.group()
    for match in re.finditer(r"(?<!\w)\+?\(?\d[\d ().-]*\d(?!\w)", text):
        phone = match.group().strip()
        if 10 <= len(re.sub(r"\D", "", phone)) <= 15:
            result["phone"] = phone
            break
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    labeled_name = next(
        (re.sub(r"^(?:full\s+)?name\s*:\s*", "", line, flags=re.I)
         for line in lines if re.match(r"^(?:full\s+)?name\s*:", line, re.I)),
        None,
    )
    headings = {"resume", "curriculum vitae", "cv", "personal info", "personal information",
                "contact", "contact info", "contact information", "professional summary",
                "summary", "education", "experience", "work experience", "skills"}
    for line in ([labeled_name] if labeled_name else lines[:8]):
        candidate = re.split(r"[|•]", line)[0].strip()
        words = candidate.split()
        if (candidate.lower() not in headings and 1 <= len(words) <= 5
                and all(any(char.isalpha() for char in word) for word in words)
                and all(char.isalpha() or char in " .'-’" for char in candidate)):
            result["full_name"] = candidate
            break
    return result


def import_uploaded_resume(upload_key):
    uploaded_file = st.session_state.get(upload_key)
    st.session_state.pop("upload_message", None)
    if uploaded_file is None:
        return
    try:
        parsed = parse_resume_text(extract_resume_text(uploaded_file))
    except ValueError as error:
        st.session_state.upload_message = ("error", str(error))
        return
    if not parsed:
        st.session_state.upload_message = ("warning", "No name, email, or phone found. Try another file.")
        return
    st.session_state.setdefault("personal_info", {}).update(parsed)
    for field, value in parsed.items():
        st.session_state[f"personal_{field}"] = value
    st.session_state.upload_message = (
        "success", "Imported " + ", ".join(field.replace("_", " ") for field in parsed) + ". Please review the results."
    )


def clear_resume():
    next_version = st.session_state.get("upload_version", 0) + 1
    st.session_state.clear()
    st.session_state.upload_version = next_version
