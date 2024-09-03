import streamlit as st
import streamlit_shadcn_ui as ui
import home
import data_visualization
import query_data
import sentimental_analysis
import text_summarization
import data_preprocessing
import tabular_data_summarization



def main_page():    

    st.markdown('<h1 style="margin-top: -0.5rem; margin-bottom: 0;">insightView</h1>', unsafe_allow_html=True)

    # Description with smaller text
    st.markdown('<p style="font-size: 0.6rem; margin-top: 0;">Data analysis and visualization tool</p>', unsafe_allow_html=True)

    # Define the tab options

    tab_options = [
        'Upload Data',
        'Data Preprocessing', 
        'Tabular Data Summarization', 
        'Data Visualization', 
        'Query your media', 
        'Text Summarization', 
        'Sentimental Analysis'
    ]

    # Create tabs using Streamlit's built-in st.tabs
    tabs = st.tabs(tab_options)

    with tabs[0]:
        home.home()
    with tabs[1]:
        data_preprocessing.data_preprocessing()
    with tabs[2]:
        tabular_data_summarization.tabular_data_summarization()
    with tabs[3]:
        data_visualization.data_visualization()
    with tabs[4]:
        query_data.query_data()
    with tabs[5]:
        text_summarization.text_summarization()
    with tabs[6]:
        sentimental_analysis.sentimental_analysis()

if __name__ == "__main__":
         main_page()


