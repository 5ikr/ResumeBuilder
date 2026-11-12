import streamlit as st

from preview import resume_markdown
from resume_upload import clear_resume, import_uploaded_resume
from ui import education_form, experience_form, personal_info_form


st.set_page_config(page_title="Resume Builder", page_icon="📄", layout="wide")

for section in ("personal_info", "education", "experience"):
    if section not in st.session_state:
        st.session_state[section] = {}

st.title("Resume Builder")
st.caption("Build your resume and watch the preview update as you type.")

page = st.sidebar.radio(
    "Resume sections", ("Personal Info", "Education", "Experience", "Preview")
)
upload_key = f"resume_upload_{st.session_state.get('upload_version', 0)}"
st.sidebar.file_uploader(
    "Resume Upload", type=["pdf", "txt"], key=upload_key,
    on_change=import_uploaded_resume, args=(upload_key,),
)
st.sidebar.caption("Import your name, email, and phone. Review the results before using them.")
if "upload_message" in st.session_state:
    level, message = st.session_state.upload_message
    getattr(st.sidebar, level)(message)
st.sidebar.button("Clear Data", on_click=clear_resume, key="clear_data")
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
        st.info("Use the sidebar to edit your resume. Your changes appear here automatically.")

with preview:
    st.subheader("Live preview")
    with st.container(border=True):
        st.markdown(resume_markdown(
            st.session_state.personal_info,
            st.session_state.education,
            st.session_state.experience,
        ))
