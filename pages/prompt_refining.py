import streamlit as st
from app_functions.shared_function import page_format, get_default_value
from pages.shot_prompting import shot_prompt_inputs
from app_functions.databricks_api import call_api
from time import sleep

user_inputs, space_col, ai_area = page_format([2, 0.4, 2])

def get_output(prompt_type):
    if prompt_type == "Shot prompting":
        job_id = 914650064561932
        input_params = {"input":st.session_state['shot_question'], "output":st.session_state['shot_reply'], "context":st.session_state['prompt_context'], "num_shots":st.session_state['num_shots']}
    return call_api(job_id, input_params)

with user_inputs:
    prompt_context = st.text_input('Please enter the context for your prompt:', get_default_value('prompt_context', ''))
    if st.session_state['prompt_type'] == 'Shot prompting':
        _, inputs_to_save = shot_prompt_inputs('edit')
    inputs_to_save["prompt_context"] = prompt_context
    subcol1, subcol2, subcol3, subcol4, subcol5, subcol6, subcol7 = st.columns(7)
    complete_edit = subcol7.button('Done', key='editbutton')
    if complete_edit:
        # Check if all inputs are filled
        if not all(inputs_to_save.values()):
            st.error("Please fill in all inputs.")
        else:
            for input in inputs_to_save.keys():
                st.session_state[input] = inputs_to_save[input]
            with ai_area:
                with st.spinner("AI is still thinking..."):
                    st.session_state['ai_output'] = get_output(st.session_state['prompt_type'])

if not st.session_state.get('ai_output'):
    with ai_area:
        display_inputs = st.session_state['final_input'].replace('\n', '<br>')
        st.markdown(display_inputs, unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        start_button = col3.button("Generate the prompt")
        if start_button:
            with st.spinner("AI is still thinking..."):
                st.session_state['ai_output'] = get_output(st.session_state['prompt_type'])
                st.rerun()
else:
    with ai_area:
        output_area = st.empty()
        with output_area.container():
            st.text_area(value=st.session_state['ai_output'],label="ai_output",label_visibility='hidden', height=300)
            col1, col2, col3 = st.columns(3)
            prompt_done = col3.button("I'm happy with the prompt 🥳")
        if prompt_done:
            with output_area.container():
                st.code(st.session_state['ai_output'], language="text")
                st.empty()