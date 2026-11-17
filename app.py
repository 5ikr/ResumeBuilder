"""Resume Builder workspace. Resume content autosaves within this Streamlit session."""
import json
import streamlit as st
from exporter import generate_resume_pdf
from preview import resume_markdown
from resume_upload import clear_resume, import_uploaded_resume
from ui import apply_styles, education_form, experience_form, personal_info_form
from profiles import (normalise_profile, initialise, restore, snapshot, checkpoint, travel,
                      duplicate, switch)
from editor_sections import (section_editor, summary_editor, additional_editor,
                             layout_editor, analysis_editor)
from analysis_tools import completion

st.set_page_config(page_title='Resume Builder', page_icon='R', layout='wide')
apply_styles()
initialise(st.session_state)
if 'pending_profile' in st.session_state:
    switch(st.session_state, st.session_state.pop('pending_profile'))


def load_saved_profile(upload_key='json_profile_upload'):
    uploaded_file = st.session_state.get(upload_key)
    if uploaded_file is None:
        return
    try:
        data = normalise_profile(json.loads(uploaded_file.getvalue().decode('utf-8-sig')))
        restore(st.session_state, data)
        st.session_state.json_profile_message = ('success', 'Profile loaded successfully.')
    except (UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        st.session_state.json_profile_message = ('error', 'Could not load this file. Please upload a valid Resume Builder JSON profile.')


@st.dialog('Clear this workspace?')
def confirm_clear():
    st.write('This removes all resume profiles, edits, uploads, and history from this session. Download a JSON backup first if you need it.')
    if st.button('Confirm clear', type='primary', key='confirm_clear'):
        clear_resume()
        st.rerun()
    if st.button('Keep editing', key='cancel_clear'):
        st.session_state.pop('show_clear_confirmation', None)
        st.rerun()


st.html('''<header class="masthead"><div><div class="eyebrow">Resume Builder / Your working draft</div>
<h1>Your experience.<br>Clearly expressed.</h1><p class="intro">A thoughtful workspace for your next opportunity. Build a resume that sounds like you, at your best.</p></div>
<div class="note"><p class="edition">Made for your next step</p><p>Write, refine, and review. Your changes stay in this session. Download a profile to keep a copy.</p></div></header>''')
st.sidebar.html('<div class="sidebar-brand">Resume Builder</div>')
page = st.sidebar.radio('Resume sections', ('Personal Info', 'Professional Summary', 'Education', 'Experience',
    'Skills', 'Projects', 'Certifications', 'Achievements', 'Additional Information', 'Preview', 'Review & Match'))

with st.sidebar.expander('Import & profiles'):
    upload_key = f"resume_upload_{st.session_state.get('upload_version', 0)}"
    st.file_uploader('Resume Upload (PDF or TXT)', type=['pdf', 'txt'], key=upload_key,
                     on_change=import_uploaded_resume, args=(upload_key,))
    st.caption('Recognizes contact details and clearly headed sections. Review imported values. Use JSON for exact restoration.')
    st.file_uploader('Load a saved profile', type=['json'], key='json_profile_upload', on_change=load_saved_profile)
for message in ('upload_message', 'json_profile_message'):
    if message in st.session_state:
        level, text = st.session_state[message]
        getattr(st.sidebar, level)(text)
font_themes = {'Classic Black': (40, 40, 40), 'Professional Blue': (30, 70, 130),
               'Burnt Amber': (160, 85, 35), 'Forest Green': (35, 100, 65), 'Dark Red': (140, 40, 40)}
selected_theme = st.sidebar.selectbox('Choose PDF font colour', list(font_themes), key='pdf_font_theme')

editor, preview = st.columns([1, 1.2], gap='large')
with editor:
    st.caption('01 / BUILD YOUR STORY')
    st.subheader('Preview & export' if page == 'Preview' else page)
    if page == 'Personal Info':
        personal_info_form()
    elif page == 'Professional Summary':
        summary_editor()
    elif page == 'Education':
        education_form()
    elif page == 'Experience':
        experience_form()
    elif page.lower() in ('skills', 'projects', 'certifications', 'achievements'):
        section_editor(page.lower())
    elif page == 'Additional Information':
        additional_editor()
    elif page == 'Review & Match':
        analysis_editor()
    else:
        layout_editor()
        st.info('Review your draft, then generate a PDF below. Empty sections are omitted automatically.')

profile_data = snapshot(st.session_state)
extra = {key: profile_data[key] for key in ('skills', 'projects', 'certifications', 'achievements', 'additional', 'settings')}
with preview:
    st.caption('02 / YOUR RESUME, LIVE')
    st.subheader('Live preview')
    st.caption(profile_data['settings']['template'])
    template_class = {'Classic Professional': 'classic', 'Modern Minimal': 'modern', 'Technical Resume': 'technical'}[profile_data['settings']['template']]
    # CSS selectors use this local marker; resume text always goes through escaped Markdown.
    st.html(f'<div class="template-marker {template_class}"></div>')
    with st.container(border=True, key='resume_sheet'):
        st.markdown(resume_markdown(st.session_state.personal_info, st.session_state.education,
                                    st.session_state.experience, **extra))

checkpoint(st.session_state)
checks = completion(profile_data)
st.sidebar.progress(sum(checks.values()) / len(checks), text=f'Draft essentials · {sum(checks.values())}/{len(checks)}')
st.sidebar.caption('Checks: name, email, summary, skills, education, and experience or projects. Optional sections do not affect this indicator.')
json_data = json.dumps(profile_data, indent=2, ensure_ascii=False)
st.sidebar.download_button('Save Profile (JSON)', json_data, 'resume_profile.json', 'application/json', key='save_profile_json', use_container_width=True)

with st.sidebar.expander('Workspace & history'):
    st.caption('Autosaved in this session only. Profiles and undo history are not stored on disk.')
    available = list(st.session_state.profiles)
    chosen = st.selectbox('Active profile', available, index=available.index(st.session_state.active_profile))
    if chosen != st.session_state.active_profile:
        # Delay restoration until the next rerun, before any editor widget is created.
        st.session_state.pending_profile = chosen
        st.rerun()
    name = st.text_input('New profile name', key='new_profile_name')
    if st.button('Duplicate resume'):
        try:
            duplicate(st.session_state, name)
            st.rerun()
        except ValueError as error:
            st.warning(str(error))
    st.button('Undo', disabled=len(st.session_state.history) < 2, on_click=travel, args=(st.session_state, 'undo'))
    st.button('Redo', disabled=not st.session_state.future, on_click=travel, args=(st.session_state, 'redo'))
if st.sidebar.button('Clear Data', key='clear_data'):
    st.session_state.show_clear_confirmation = True
if st.session_state.get('show_clear_confirmation'):
    confirm_clear()

st.divider()
st.subheader('Ready for your next step')
st.caption('Generate a print-ready PDF with the selected template. Review facts, links, and page breaks before sending.')
if st.button('Generate PDF', type='primary'):
    if not st.session_state.personal_info.get('full_name', '').strip():
        st.warning('Please enter your full name before generating your resume.')
    else:
        try:
            pdf_bytes = generate_resume_pdf(st.session_state.personal_info, st.session_state.education,
                                            st.session_state.experience, font_color=font_themes[selected_theme], **extra)
            st.session_state.generated_pdf = (pdf_bytes, json_data, selected_theme)
            st.success(f'Your resume PDF is ready ({selected_theme}).')
        except (ValueError, OSError) as error:
            st.error(f'PDF generation failed: {error}')
if 'generated_pdf' in st.session_state:
    pdf_bytes, saved_data, saved_theme = st.session_state.generated_pdf
    if (saved_data, saved_theme) == (json_data, selected_theme):
        st.download_button('Download Resume as PDF', pdf_bytes, 'resume.pdf', 'application/pdf', key='download_resume_pdf')
    else:
        st.session_state.pop('generated_pdf', None)
