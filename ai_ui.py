"""Review-first writing controls shared by all editable resume sections."""
import json
import os
import streamlit as st
from ai_service import ACTIONS, STYLES, LENGTHS, AIError, WritingRequest, improve


def accept_suggestion(key, data, field):
    suggestion = st.session_state.get('ai_result_' + key)
    if suggestion and suggestion['original'] == data.get(field, ''):
        data[field] = suggestion['text']
        st.session_state[key] = suggestion['text']
        st.session_state.pop('ai_result_' + key, None)


def writing_controls(key, data, field, section, *, summary=False, context=''):
    with st.expander('Summary assistant' if summary else 'AI Improve', expanded=False):
        st.caption('Optional · OpenAI receives the text shown below and the supplied context only when you request a suggestion. Review every factual claim before accepting.')
        if not os.getenv('OPENAI_API_KEY', '').strip():
            st.info('AI is unavailable until OPENAI_API_KEY is configured. You can keep editing and exporting.')
        action = 'Generate summary' if summary else st.selectbox('Writing action', ACTIONS, key='ai_action_' + key)
        style = st.selectbox('Writing style', STYLES, key='ai_style_' + key)
        length = st.selectbox('Length preference', LENGTHS, key='ai_length_' + key)
        original = data.get(field, '')
        source = context if summary else original
        signature = json.dumps([source, context, section, action, style, length], ensure_ascii=False)
        st.caption('Text to send')
        st.code(source or '(empty)', language=None)
        if context and not summary:
            st.caption('Context to send')
            st.code(context, language=None)
        consent = st.checkbox('I consent to sending this text and displayed context to OpenAI.', key='ai_consent_' + key)
        cached = st.session_state.get('ai_result_' + key)
        busy_key = 'ai_busy_' + key
        if st.button('Regenerate' if cached else 'Generate suggestion', key='ai_generate_' + key,
                     disabled=not consent or not bool(source.strip()) or st.session_state.get(busy_key, False)):
            st.session_state[busy_key] = True
            try:
                with st.spinner('Preparing a suggestion…'):
                    result = improve(WritingRequest(source, section, action, style, length, context if not summary else ''), consent=consent)
                st.session_state['ai_result_' + key] = dict(original=original, text=result.text, questions=result.questions, signature=signature)
            except AIError as error:
                st.error(str(error))
            finally:
                st.session_state[busy_key] = False
        result = st.session_state.get('ai_result_' + key)
        if result:
            st.caption('Original')
            st.text(result['original'] or '(empty)')
            st.caption('Suggestion · verify facts before accepting')
            st.text(result['text'])
            for question in result['questions']:
                st.info(question)
            stale = result['original'] != original or result.get('signature') != signature
            if stale:
                st.warning('The source, context, or writing preferences changed. Regenerate before accepting.')
            left, right = st.columns(2)
            left.button('Accept', key='ai_accept_' + key, disabled=stale, on_click=accept_suggestion, args=(key, data, field))
            if right.button('Reject', key='ai_reject_' + key):
                del st.session_state['ai_result_' + key]
                st.rerun()
