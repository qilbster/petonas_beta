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
    for _ in range(6):
        st.text("")
    # Fine tune inputs based on prompt engineering techniques
    summary_length = st.number_input("Maximum number of words:", min_value=1, max_value=1000, value=get_default_value('summary_length', 50), step=1, format='%d')
    summary_focus = st.text_input("Focus of the summary:", get_default_value('summary_focus', ''))
    final_input = st.session_state['initial_input'] + f'\nMaximum number of words: {summary_length}\nFocus of the summary: {summary_focus}'
    subcol1, subcol2, subcol3, subcol4, subcol5 = st.columns(5)
    completed_prompt_selection = subcol5.button("Done")

with initial_inputs:
    if st.button("Back"): switch_page('app')
    st.subheader("Selection")
    st.code(final_input, language='text')

if completed_prompt_selection:
        inputs_to_save = {"summary_length":summary_length, "summary_focus":summary_focus, 'final_input':final_input, "prompt_page":"focused_summary"}
        # Check if all inputs are filled
        if not all(inputs_to_save.values()):
            st.error("Please fill in all inputs.")
        else:
            for input in inputs_to_save.keys():
                st.session_state[input] = inputs_to_save[input]
            switch_page("prompt_refining")