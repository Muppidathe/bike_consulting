import streamlit as st
import time
import pandas as pd
import numpy as np
import os
import plotly.graph_objects as go
from langgraph_agent import create_workflow
from dotenv import load_dotenv,set_key, dotenv_values
# File path of .env
env_file = ".env"
load_dotenv()
api_key = os.getenv("groq_api")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if 'app' not in st.session_state:
    st.session_state.app = create_workflow()

# Sidebar for configuration
with st.sidebar:
    with st.form("model_api_key"):
        api_key = st.text_input(label="Enter the groq api key",value=api_key)
        button = st.form_submit_button(label='Submit')
        if button and api_key:
            set_key(env_file, "GROQ_API_KEY",api_key)
            del st.session_state['app']

# Function to display different visualization types
def display_visualization(vis_type, data):
    if data is None:
        st.write("No visualization data available")
        return
    
    try:
        if vis_type == "bar":
            # Format: { labels: string[], values: {data: number[], label: string}[] }
            labels = data['labels']
            
            # Create DataFrame from the data structure
            df_data = {}
            for series in data['values']:
                df_data[series['label']] = series['data']
            
            chart_data = pd.DataFrame(df_data, index=labels)
            st.bar_chart(chart_data)
            
        elif vis_type == "horizontal_bar":
            # Similar to bar but displayed horizontally using plotly
            labels = data['labels']
            
            fig = go.Figure()
            for series in data['values']:
                fig.add_trace(go.Bar(
                    y=labels,
                    x=series['data'],
                    name=series['label'],
                    orientation='h'
                ))
            
            fig.update_layout(barmode='group')
            st.plotly_chart(fig)
            
        elif vis_type == "line":
            # Format: { xValues: number[] | string[], yValues: { data: number[]; label: string }[] }
            x_values = data['xValues']
            
            # Create DataFrame for line chart
            df_data = {}
            for series in data['yValues']:
                label = series.get('label', 'Series')
                df_data[label] = series['data']
            
            chart_data = pd.DataFrame(df_data, index=x_values)
            st.line_chart(chart_data)
            
        elif vis_type == "pie":
            # Format: [{ id: number, value: number, label: string }]
            fig = go.Figure(data=[go.Pie(
                labels=[item['label'] for item in data],
                values=[item['value'] for item in data]
            )])
            
            st.plotly_chart(fig)
            
        elif vis_type == "scatter":
            # Format: { series: [{ data: { x: number; y: number; id: number }[], label: string }] }
            fig = go.Figure()
            
            for series in data['series']:
                x_values = [point['x'] for point in series['data']]
                y_values = [point['y'] for point in series['data']]
                
                fig.add_trace(go.Scatter(
                    x=x_values,
                    y=y_values,
                    mode='markers',
                    name=series.get('label', 'Series')
                ))
                
            st.plotly_chart(fig)
        
        else:
            st.write(f"Visualization type '{vis_type}' not supported")
            
    except Exception as e:
        st.error(f"Error displaying visualization: {str(e)}")
        st.write("Raw visualization data:")
        st.json(data)  # Display the raw data as JSON for debugging

# Main chat interface
st.title("Database Query Assistant")
input_msg = st.chat_input("Enter your question about the database")

# Display chat history
for i in st.session_state.messages:
    st.chat_message(i['role']).write(i['content'])

# Process new message
if input_msg:
    # Add user message to chat
    st.session_state.messages.append({'role': 'human', 'content': input_msg})
    st.chat_message("human").write(input_msg)
    
    # Process with LangGraph agent
    with st.spinner("Analyzing your question..."):
        response = st.session_state.app.invoke({'question': input_msg})
        
        # Extract results from response
        answer = response.get('answer', 'No answer found')
        vis_type = response.get('visualization', 'none')
        vis_data = response.get('formatted_data_for_visualization')
        
        # Add assistant response to chat
        content = answer
        st.session_state.messages.append({
            'role': 'assistant', 
            'content': content
        })
        
        # Display assistant response
        with st.chat_message('assistant'):
            st.write(answer)
            
            # Show visualization if available
            if vis_type != 'none' and vis_data:
                st.subheader(f"Data Visualization ({vis_type})")
                display_visualization(vis_type, vis_data)
                
                # Explain visualization choice
                if 'visualization_reason' in response:
                    with st.expander("Why this visualization?"):
                        st.write(response['visualization_reason'])