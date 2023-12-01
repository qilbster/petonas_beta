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

prompt_engineering_techniques = ("Shot prompting", "Content summarization with specific focus")

# Function to use value from session state if it exists and if not, set as default
def get_default_value(key, default_value):
    if st.session_state.get(key):
        if key == 'prompt_type':
            return prompt_engineering_techniques.index(st.session_state[key])
        return st.session_state[key]
    else:
        return default_value

with selections:  
    persona = st.text_input('Please enter a persona:', get_default_value('persona', ''))
    # Empty space
    st.text("")
    prompt_context = st.text_input('Please enter the context for your prompt:', get_default_value('prompt_context', ''))
    # Empty space
    st.text ("")
    prompt_type = st.selectbox(
        'Please select a prompt engineering technique:',
        prompt_engineering_techniques, index=get_default_value('prompt_type', None))
    # Empty space
    st.text ("")
    # Format selected inputs to be displayed to users
    initial_input = f'Persona: {persona}\nContext: {prompt_context}\nPrompt type: {prompt_type}'
    subcol1, subcol2, subcol3, subcol4, subcol5 = st.columns(5)
    completed_prompt_selection = subcol5.button("Done")

with initial_inputs:
    st.subheader("Selection")
    st.code(initial_input, language="text")

if completed_prompt_selection:
    inputs_to_save = {"persona":persona, "prompt_context":prompt_context, "prompt_type":prompt_type, "initial_input":initial_input}
    # Check if all inputs are filled
    if not all(inputs_to_save.values()):
        st.error("Please fill in all inputs.")
    else:
        for input in inputs_to_save.keys():
            st.session_state[input] = inputs_to_save[input]
        if prompt_type == "Shot prompting":
            switch_page("shot_prompting")
        if prompt_type == "Content summarization with specific focus":
            switch_page("focused_summary")