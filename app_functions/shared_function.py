import streamlit as st
from streamlit_extras.switch_page_button import switch_page

def page_format(col_layout=[2, 0.2, 1.2]):
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
    initial_inputs, space_col, selections = st.columns(col_layout)
    return (initial_inputs, space_col, selections)

# Function to use value from session state if it exists and if not, set as default
def get_default_value(key, default_value, prompt_engineering_techniques=None):
    if st.session_state.get(key):
        if key == 'prompt_type':
            return prompt_engineering_techniques.index(st.session_state[key])
        return st.session_state[key]
    else:
        return default_value
    
def completed_input(inputs_to_save, alternative_page_mapping, col_name, button_name='Done'):
    with col_name:
        subcol1, subcol2, subcol3, subcol4, subcol5 = st.columns(5)
        completed_prompt_selection = subcol5.button(button_name)
    if completed_prompt_selection:
        # Check if all inputs are filled
        if not all(inputs_to_save.values()):
            st.error("Please fill in all inputs.")
        else:
            for input in inputs_to_save.keys():
                st.session_state[input] = inputs_to_save[input]
            if isinstance(alternative_page_mapping, str):
                switch_page(alternative_page_mapping)
            elif alternative_page_mapping is None: pass
            else:
                for input_key in alternative_page_mapping.keys():
                    for input_type, page_name in alternative_page_mapping[input_key].items():
                        if st.session_state[input_key] == input_type:
                            switch_page(page_name)