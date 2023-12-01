import streamlit as st
from app_functions.shared_function import page_format, completed_input, get_default_value

initial_inputs, space_col, selections = page_format()

prompt_engineering_techniques = ("Shot prompting", "Content summarization with specific focus")

with selections:  
    persona = st.text_input('Please enter a persona:', get_default_value('persona', ''))
    # Empty space
    st.text("")
    prompt_context = st.text_input('Please enter the context for your prompt:', get_default_value('prompt_context', ''))
    # Empty space
    st.text ("")
    prompt_type = st.selectbox(
        'Please select a prompt engineering technique:',
        prompt_engineering_techniques, index=get_default_value('prompt_type', None, prompt_engineering_techniques))
    # Empty space
    st.text ("")
    # Format selected inputs to be displayed to users
    initial_input = f'Persona: {persona}\nContext: {prompt_context}\nPrompt type: {prompt_type}'

inputs_to_save = {"persona":persona, "prompt_context":prompt_context, "prompt_type":prompt_type, "initial_input":initial_input}
alternative_page_mapping = {"prompt_type": {"Shot prompting":"shot_prompting","Content summarization with specific focus":"focused_summary"}}
completed_input(inputs_to_save, alternative_page_mapping, selections)

with initial_inputs:
    st.subheader("Selection")
    st.code(initial_input, language="text")