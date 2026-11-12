from dataclasses import asdict

import streamlit as st

from models import PersonalInfo


def personal_info_form():
    data = asdict(PersonalInfo(**st.session_state.personal_info))
    labels = {
        "full_name": "Full name",
        "headline": "Professional headline",
        "email": "Email",
        "phone": "Phone",
        "location": "Location",
        "website": "Website or LinkedIn",
        "summary": "Professional summary",
    }
    for field, label in labels.items():
        widget = st.text_area if field == "summary" else st.text_input
        data[field] = widget(label, value=data[field], key=f"personal_{field}")
    st.session_state.personal_info = data
