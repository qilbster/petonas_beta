import streamlit as st
from streamlit_extras.switch_page_button import switch_page

st.set_page_config(layout="wide")
# Remove the sidebar from streamlit
st.markdown("""
    <style>
        section[data-testid="stSidebar"][aria-expanded="true"]{
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)

# Layout the page as two columns
initial_inputs, space_col, selections = st.columns([2, 0.2, 1.2])

# Function to use value from session state if it exists and if not, set as default
def get_default_value(key, default_value):
    if st.session_state.get(key):
        return st.session_state[key]
    else:
        return default_value

with selections:      
    # Empty space
    for _ in range(3):
        st.text("")
    # Fine tune inputs based on prompt engineering techniques
    num_shots = st.slider("Number of shots", 1, 5, get_default_value('num_shots', 1))
    shot_question = st.text_input("Example prompt:", get_default_value('shot_question', ''))
    shot_reply = st.text_input("Example reply:", get_default_value('shot_reply', ''))
    # Format selected inputs to be displayed to users
    final_input = st.session_state['initial_input'] + f'\nNumber of shots: {num_shots}\nExample prompt: {shot_question}\nExample reply: {shot_reply}'
    subcol1, subcol2, subcol3, subcol4, subcol5 = st.columns(5)
    completed_prompt_selection = subcol5.button("Done")

with initial_inputs:
    if st.button("Back"): switch_page('app')
    st.subheader("Selection")
    st.code(final_input)

if completed_prompt_selection:
        inputs_to_save = {"num_shots":num_shots, "shot_question":shot_question, "shot_reply":shot_reply, 'final_input':final_input, "prompt_page":"shot_prompting"}
        # Check if all inputs are filled
        if not all(inputs_to_save.values()):
            st.error("Please fill in all inputs.")
        else:
            for input in inputs_to_save.keys():
                st.session_state[input] = inputs_to_save[input]
            switch_page("prompt_refining")