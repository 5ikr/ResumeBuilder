import json

import streamlit as st

from exporter import generate_resume_pdf
from models import Education, Experience, PersonalInfo
from preview import resume_markdown
from resume_upload import clear_resume, import_uploaded_resume
from ui import education_form, experience_form, personal_info_form


st.set_page_config(
    page_title="Resume Builder",
    page_icon="📄",
    layout="wide"
)


# SESSION STATE SETUP

for section in ("personal_info", "education", "experience"):
    if section not in st.session_state:
        st.session_state[section] = {}


# JSON PROFILE VALIDATION

def normalise_profile(data):

    if not isinstance(data, dict):
        raise ValueError("Invalid JSON structure.")

    personal_info = data.get("personal_info")
    education = data.get("education")
    experience = data.get("experience")

    if not isinstance(personal_info, dict):
        raise ValueError("Personal information is invalid.")

    if not isinstance(education, dict):
        raise ValueError("Education data is invalid.")

    if not isinstance(experience, dict):
        raise ValueError("Experience data is invalid.")

    personal_defaults = PersonalInfo().__dict__
    education_defaults = Education().__dict__
    experience_defaults = Experience().__dict__

    clean_personal = {
        field: str(personal_info.get(field, default) or "")
        for field, default in personal_defaults.items()
    }

    def clean_entries(entries, defaults, section_name):

        cleaned = {}

        for entry_id, entry in entries.items():

            if not isinstance(entry_id, str) or not isinstance(entry, dict):
                raise ValueError(f"Invalid {section_name} entry.")

            cleaned[entry_id] = {
                field: str(entry.get(field, default) or "")
                for field, default in defaults.items()
            }

        return cleaned

    clean_education = clean_entries(
        education, education_defaults, "education"
    )

    clean_experience = clean_entries(
        experience, experience_defaults, "experience"
    )

    return clean_personal, clean_education, clean_experience


# JSON PROFILE LOADING

def load_saved_profile(upload_key="json_profile_upload"):

    uploaded_file = st.session_state.get(upload_key)

    if uploaded_file is None:
        return

    try:

        profile_data = json.loads(
            uploaded_file.getvalue().decode("utf-8")
        )

        personal_info, education, experience = normalise_profile(
            profile_data
        )

        # Restore main data
        st.session_state.personal_info = personal_info
        st.session_state.education = education
        st.session_state.experience = experience

        # Restore personal information widgets
        for field, value in personal_info.items():
            st.session_state[f"personal_{field}"] = value

        # Restore education widgets
        for entry_id, entry in education.items():

            for field, value in entry.items():

                st.session_state[
                    f"education_{entry_id}_{field}"
                ] = value

        # Restore experience widgets
        for entry_id, entry in experience.items():

            for field, value in entry.items():

                st.session_state[
                    f"experience_{entry_id}_{field}"
                ] = value

        st.session_state["json_profile_message"] = (
            "success",
            "Profile loaded successfully."
        )

    except (
        UnicodeDecodeError,
        json.JSONDecodeError,
        KeyError,
        TypeError,
        ValueError
    ):

        st.session_state["json_profile_message"] = (
            "error",
            "Could not load this file. Please upload a valid Resume Builder JSON profile."
        )


# PAGE HEADING

st.title("Resume Builder")

st.caption(
    "Build your resume and watch the preview update as you type."
)


# SIDEBAR NAVIGATION

page = st.sidebar.radio(
    "Resume sections",
    ("Personal Info", "Education", "Experience", "Preview")
)


# EXISTING RESUME IMPORT

upload_key = f"resume_upload_{st.session_state.get('upload_version', 0)}"

st.sidebar.file_uploader(
    "Resume Upload (PDF or TXT)",
    type=["pdf", "txt"],
    key=upload_key,
    on_change=import_uploaded_resume,
    args=(upload_key,)
)

st.sidebar.caption(
    "Import your name, email, and phone. Review the results before using them."
)

if "upload_message" in st.session_state:

    level, message = st.session_state.upload_message

    getattr(st.sidebar, level)(message)


st.sidebar.divider()


# PERSON 3: JSON SAVE PROFILE

st.sidebar.subheader("Save or Load Profile")

# PERSON 3: JSON LOAD PROFILE

st.sidebar.file_uploader(
    "Load a saved profile",
    type=["json"],
    key="json_profile_upload",
    on_change=load_saved_profile,
    help="Upload a JSON profile previously downloaded from this Resume Builder."
)

if "json_profile_message" in st.session_state:

    level, message = st.session_state.json_profile_message

    getattr(st.sidebar, level)(message)


st.sidebar.divider()


# PERSON 3: PDF FONT COLOUR THEMES

st.sidebar.subheader("PDF Customization")

font_themes = {

    "Classic Black": (40, 40, 40),

    "Professional Blue": (30, 70, 130),

    "Elegant Purple": (100, 60, 130),

    "Forest Green": (35, 100, 65),

    "Dark Red": (140, 40, 40)

}

selected_theme = st.sidebar.selectbox(
    "Choose PDF font colour",
    options=list(font_themes.keys()),
    key="pdf_font_theme"
)


# CLEAR DATA

st.sidebar.button(
    "Clear Data",
    on_click=clear_resume,
    key="clear_data"
)


# RESUME EDITOR AND LIVE PREVIEW

editor, preview = st.columns([1, 1], gap="large")


with editor:

    st.subheader(page)

    if page == "Personal Info":

        personal_info_form()

    elif page == "Education":

        education_form()

    elif page == "Experience":

        experience_form()

    else:

        st.info(
            "Use the sidebar to edit your resume. "
            "Your changes appear here automatically."
        )


with preview:

    st.subheader("Live preview")

    with st.container(border=True):

        st.markdown(
            resume_markdown(
                st.session_state.personal_info,
                st.session_state.education,
                st.session_state.experience
            )
        )


profile_data = {
    "format_version": 1,
    "personal_info": st.session_state.personal_info,
    "education": st.session_state.education,
    "experience": st.session_state.experience
}

json_data = json.dumps(
    profile_data,
    indent=4,
    ensure_ascii=False
)

st.sidebar.download_button(
    label="Save Profile (JSON)",
    data=json_data,
    file_name="resume_profile.json",
    mime="application/json",
    key="save_profile_json",
    use_container_width=True
)



# PDF EXPORT

st.divider()

st.subheader("Export Your Resume")


if st.button("Generate PDF", type="primary"):

    personal_info = st.session_state.personal_info

    education = st.session_state.education

    experience = st.session_state.experience

    if not personal_info.get("full_name", "").strip():

        st.warning(
            "Please enter your full name before generating your resume."
        )

    else:

        try:

            pdf_bytes = generate_resume_pdf(
                personal_info,
                education,
                experience,
                font_color=font_themes[selected_theme]
            )

            st.session_state.generated_pdf = (pdf_bytes, json_data, selected_theme)

            st.success(
                f"Your resume PDF is ready ({selected_theme})."
            )

        except Exception as error:

            st.error(f"PDF generation failed: {error}")

if "generated_pdf" in st.session_state:
    pdf_bytes, saved_data, saved_theme = st.session_state.generated_pdf
    if (saved_data, saved_theme) == (json_data, selected_theme):
        st.download_button("Download Resume as PDF", pdf_bytes, "resume.pdf",
                           "application/pdf", key="download_resume_pdf")
    else:
        st.session_state.pop("generated_pdf", None)
