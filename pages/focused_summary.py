import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from app_functions.shared_function import page_format, completed_input, get_default_value

# Layout the page as two columns
initial_inputs, space_col, selections = page_format()
    
with selections:      
    # Empty space
    for _ in range(6):
        st.text("")
    # Fine tune inputs based on prompt engineering techniques
    summary_length = st.number_input("Maximum number of words:", min_value=1, max_value=1000, value=get_default_value('summary_length', 50), step=1, format='%d')
    summary_focus = st.text_input("Focus of the summary:", get_default_value('summary_focus', ''))
    final_input = st.session_state['initial_input'] + f'\nMaximum number of words: {summary_length}\nFocus of the summary: {summary_focus}'

inputs_to_save = {"summary_length":summary_length, "summary_focus":summary_focus, 'final_input':final_input, "prompt_page":"focused_summary"}
completed_input(inputs_to_save, "prompt_refining", selections)

with initial_inputs:
    if st.button("Back"): switch_page('app')
    st.subheader("Selection")
    st.code(final_input, language='text')

