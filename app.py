import streamlit as st

from preview import resume_markdown
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
