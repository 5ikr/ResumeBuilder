import streamlit as st

from ui import personal_info_form


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
