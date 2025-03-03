import streamlit as st
import time
import pandas as pd
import numpy as np
from langgraph_agent import create_workflow
if "messages" not in st.session_state:
    st.session_state.messages = []
if 'app' not in st.session_state:
    st.session_state.app=create_workflow()
with st.sidebar:
    with st.form("mode_api_key"):
        model_name=st.text_input(label="Enter the model name")
        api_key=st.text_input(label="Enter the groq api key")
        button=st.form_submit_button(label='submit')
input_msg=st.chat_input("enter the question")
for i in st.session_state.messages:
    st.chat_message(i['role']).write(i['content'])
if input_msg:
    st.session_state.messages.append({'role':'human','content':input_msg})
    st.chat_message("human").write(input_msg)
    with st.spinner():
        response=st.session_state.app.invoke({'question':input_msg})
        st.session_state.messages.append({'role':'assistant','content':response['results']})
        with st.chat_message('assistant'):
            st.write(response['results'])
            st.write(f"visualization {response['visualization']}")
            if response['visualization']:
                chart_data = pd.DataFrame(np.random.randn(20, 3), columns=["a", "b", "c"])
                st.line_chart(chart_data)

