import streamlit as st


st.set_page_config(page_title="Resume Builder", page_icon="📄", layout="wide")

for section in ("personal_info", "education", "experience"):
    if section not in st.session_state:
        st.session_state[section] = {}

st.title("Resume Builder")
