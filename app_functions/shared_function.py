import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from databricks_api import DatabricksAPI
import time

def call_api(job_id, input_params):
    db = DatabricksAPI(
    host = "https://dbc-eb788f31-6c73.cloud.databricks.com/",
    token = "dapi52ff828b8575edb2585ede0beff0dcbb"
    )
    run_id = db.jobs.run_now(job_id=job_id, notebook_params=input_params).get('run_id')
    run_status = db.jobs.get_run(run_id)['state']['life_cycle_state']
    start_time = time.time()
    while (time.time()-start_time < 300 and run_status != 'TERMINATED'):
        time.sleep(10)
        run_status = db.jobs.get_run(run_id)['state']['life_cycle_state']

    if db.jobs.get_run(run_id)['state'].get('result_state') == 'SUCCESS':
        return db.jobs.get_run_output(run_id)['notebook_output']['result']

def get_output(prompt_type):
    if prompt_type == "Shot prompting":
        job_id = 914650064561932
        input_params = {"input":st.session_state['shot_question'], "output":st.session_state['shot_reply'], "context":st.session_state['prompt_context'], "num_shots":st.session_state['num_shots']}
    elif prompt_type == "Content summarization with specific focus":
        job_id = 807625195369077
        input_params = {"persona":st.session_state['persona'], "word_limit":st.session_state['summary_length'], "focus":st.session_state['summary_focus']}
    return call_api(job_id, input_params)

def page_format(col_layout=[2, 0.4, 2]):
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
    
def completed_input(inputs_to_save, alternative_page_mapping, key, button_name='Done', api_keys=None, get_output=get_output):
    subcol1, subcol2, subcol3, subcol4, subcol5 = st.columns(5)
    completed_prompt_selection = subcol5.button(button_name, key=key+'button')
    if completed_prompt_selection:
        # Check if all inputs are filled
        if not all(inputs_to_save.values()):
            st.error("Please fill in all inputs.")
        else:
            for input in inputs_to_save.keys():
                st.session_state[input] = inputs_to_save[input]
            if isinstance(alternative_page_mapping, str):
                switch_page(alternative_page_mapping)
            elif isinstance(alternative_page_mapping, dict):
                for input_key in alternative_page_mapping.keys():
                    for input_type, page_name in alternative_page_mapping[input_key].items():
                        if st.session_state[input_key] == input_type:
                            switch_page(page_name)
            else:
                with st.spinner("AI is still thinking..."):
                    st.session_state['ai_output'] = get_output(st.session_state['prompt_type'])