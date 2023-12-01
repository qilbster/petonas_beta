import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from app_functions.shared_function import page_format, completed_input, get_default_value

# Layout the page as two columns
initial_inputs, space_col, selections = page_format()

def shot_prompt_inputs(uniq):
    # Fine tune inputs based on prompt engineering techniques
    num_shots = st.slider("Number of shots", 1, 5, get_default_value('num_shots', 1), key=uniq+'num')
    shot_question = st.text_input("Example prompt:", get_default_value('shot_question', ''), key=uniq+'shot')
    shot_reply = st.text_input("Example reply:", get_default_value('shot_reply', ''), key=uniq+'reply')
    # Format selected inputs to be displayed to users
    final_input = st.session_state['initial_input'] + f'\nNumber of shots: {num_shots}\nExample prompt: {shot_question}\nExample reply: {shot_reply}'
    inputs_to_save = {"num_shots":num_shots, "shot_question":shot_question, "shot_reply":shot_reply, 'final_input':final_input, "prompt_page":"shot_prompting"}
    return final_input, inputs_to_save

with selections:
    for _ in range(3):
        st.text("")
    final_input, inputs_to_save = shot_prompt_inputs('initial')
    completed_input(inputs_to_save, "prompt_refining", 'inital')

with initial_inputs:
    if st.button("Back"): switch_page('app')
    st.subheader("Selection")
    st.code(final_input)

