import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from streamlit_extras.stylable_container import stylable_container

# Remove the pages from streamlit sidebar
st.markdown("<style> ul {display: none;} </style>", unsafe_allow_html=True)

with st.sidebar:
    if st.button("Back"): 
        if st.session_state['prompt_page'] == "focused_summary":
            switch_page('focused_summary')
        elif st.session_state['prompt_page'] == "shot_prompting":
            switch_page('shot_prompting')
    st.subheader("Inputs to prompt generator:")
    display_inputs = st.session_state['final_input'].replace('\n', '<br>')
    
    # Create a container with a black border and a grey background.
    with stylable_container(key="container_with_border",
                            css_styles="""
                            {
                            border: 1px solid rgba(49, 51, 63, 0.2); 
                            padding: calc(1em - 12px); 
                            border-radius: 0.5rem;
                            }
                            """):
        st.markdown(display_inputs, unsafe_allow_html=True)

# Layout the page as two columns
selections, space_col, initial_inputs = st.columns([1.2, 0.2, 2])

# Define functions to be used in the chat
def call_API(prompt_type):
    # Call API to get the output
    with initial_inputs:
        with st.spinner('AI is thinking...'):
            if prompt_type == "Shot prompting":
                promptTemplate='Testing123'
    st.session_state.latest_output = {"role": "AI", "content": promptTemplate}
    st.session_state.chat_history.append(st.session_state.latest_output)

def on_input_change():
    user_input = st.session_state.user_input
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    call_API(st.session_state.prompt_type)

def on_btn_click():
    del st.session_state.chat_history[1:]

st.session_state.setdefault('chat_history', [{'role':'user','content':st.session_state['final_input']}])

with initial_inputs:
    for message in st.session_state.chat_history:
        with st.chat_message(message['role']):
            st.text(message['content'])
    if len(st.session_state.chat_history) == 1:
        call_API(st.session_state.prompt_type)
        with st.chat_message("AI"):
            st.text("I'm a bot, not a human")
    subcol1, subcol2, subcol3, subcol5 = st.columns(4)
    subcol5.button("Clear message", on_click=on_btn_click)
    st.text_input("User Input:", on_change=on_input_change, key="user_input")

with selections:
    final_output = st.text_area(value=st.session_state.latest_output['content'],label="Engineering prompt returned by the AI",label_visibility='hidden', height=300)
