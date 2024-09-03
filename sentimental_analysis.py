import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import fitz  # PyMuPDF
import docx
from docx import Document
import io
from PIL import Image
import tempfile
from PyPDF2 import PdfReader
from sklearn.linear_model import LinearRegression
import os
import tabula
import base64
from io import BytesIO
from sklearn.impute import SimpleImputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.linear_model import BayesianRidge
from mitosheet.streamlit.v1 import spreadsheet
from collections import OrderedDict
import matplotlib.pyplot as plt
from fpdf import FPDF
from upload import handle_file_upload

            


            # Initialize session state variables
if 'processed_df' not in st.session_state:
                st.session_state.processed_df = None
if 'data_processed' not in st.session_state:
                st.session_state.data_processed = False
if 'uploaded_files' not in st.session_state:
                st.session_state.uploaded_files = None
if 'dfs_tabular' not in st.session_state:
                st.session_state.dfs_tabular = None
if 'dfs_non_tabular' not in st.session_state:
                st.session_state.dfs_non_tabular = None


            # Clear temporary files at the start
def clear_temp_files():
                temp_dir = tempfile.gettempdir()
                for filename in os.listdir(temp_dir):
                    if filename.startswith('temp') and filename.endswith('.csv'):
                        os.remove(os.path.join(temp_dir, filename))

clear_temp_files()


def read_pdf(file):
                file.seek(0)
                pdf_document = fitz.open(stream=file.read(), filetype="pdf")
                text = ""
                for page_num in range(pdf_document.page_count):
                    page = pdf_document.load_page(page_num)
                    text += page.get_text()
                return text


def read_docx(file):
                file.seek(0)
                doc = docx.Document(file)
                text = []
                for paragraph in doc.paragraphs:
                    text.append(paragraph.text)
                return "\n".join(text)



def read_txt(file):
                file.seek(0)
                return file.read().decode("utf-8")


def sentimental_analysis(): 
            import streamlit as st
            st.markdown('<h1 style="font-size: 1rem; margin-top: 0;">Sentimental Analysis</h1>', unsafe_allow_html=True)
            uploaded_files, _, dfs_non_tabular = handle_file_upload(page_name=sentimental_analysis)


            # Process uploaded files
            dfs_non_tabular = []

            if uploaded_files is None or len(uploaded_files) == 0:
                st.warning("Please upload a file that contains text data for sentimental analysis.")
                return

            for uploaded_file in uploaded_files:
                file_name = uploaded_file.name
                file_extension = file_name.split(".")[-1].lower()

                for file in uploaded_files:
                    file_extension = file.name.split('.')[-1].lower()
                    if file_extension not in ["txt", "pdf", "docx"]:
                        st.warning(f"Unsupported file type for file {file_name}. Please upload a file that contains text data for sentimental analysis. ")
                    else:
                        if file_extension == 'pdf':
                                # Extract text from PDF
                                text = read_pdf(file)
                                dfs_non_tabular.append(text)

                        elif file_extension == 'docx':
                                text = read_docx(file)
                                dfs_non_tabular.append(text)

                        elif file_extension == 'txt':
                                text = read_txt(file)
                                dfs_non_tabular.append(text)
                        else:
                                st.error(f"Unsupported file type for file {uploaded_files.name}. Please upload a TXT, PDF, or DOCX file.")                           



    # Sentiment analysis logic
            if dfs_non_tabular:
                
               # Combine all text data in dfs_non_tabular
                combined_text = "\n\n--- New Document ---\n\n".join(dfs_non_tabular)

                # Write the combined text to a file
                output_path = r"C:\Users\Kwaku\Desktop\project_final\upload_txt.txt"

                
                # List of encodings to try
                encodings_to_try = ['utf-8', 'utf-16', 'latin-1', 'cp1252']

                # Try each encoding until one works
                for encoding in encodings_to_try:
                        with open(output_path, 'w', encoding=encoding, errors='ignore') as f:
                            f.write(combined_text)
              


                def download_nltk_resources():
                    try:
                        nltk.data.find('tokenizers/punkt')
                    except LookupError:
                        st.warning("The NLTK `punkt` resource is missing. Attempting to download it now...")
                        nltk.download('punkt', quiet=True)

                    try:
                        nltk.data.find('vader_lexicon')
                    except LookupError:
                        st.warning("The NLTK `vader_lexicon` resource is missing. Attempting to download it now...")
                        nltk.download('vader_lexicon', quiet=True)

                    try:
                        nltk.data.find('stopwords')
                    except LookupError:
                        st.warning("The NLTK `stopwords` resource is missing. Attempting to download it now...")
                        nltk.download('stopwords', quiet=True)

                import nltk
             
                # Download necessary NLTK resources
                nltk.download('vader_lexicon')
                nltk.download('punkt')
                nltk.download('stopwords')

                from nltk.sentiment.vader import SentimentIntensityAnalyzer
                from nltk.corpus import stopwords
                from nltk.tokenize import sent_tokenize, word_tokenize
                from nltk.probability import FreqDist
                from heapq import nlargest
                import re
                import matplotlib.pyplot as plt
                import plotly.graph_objects as go
                import pandas as pd
                import streamlit as st


                # Function definitions
                def analyze_sentiment_vader(text):
                    analyzer = SentimentIntensityAnalyzer()
                    sentiment = analyzer.polarity_scores(text)
                    return sentiment

                def highest_sentiment(sentiment):
                    scores = {'negative': sentiment['neg'], 'neutral': sentiment['neu'], 'positive': sentiment['pos']}
                    highest = max(scores, key=scores.get)
                    return highest, scores[highest]

                
                def plot_sentiment_distribution(sentiment):
                    labels = ['Negative', 'Neutral', 'Positive']
                    values = [sentiment['neg'], sentiment['neu'], sentiment['pos']]
                    
                    fig = go.Figure(data=[go.Pie(labels=labels, values=values)])
                    fig.update_layout(title='Sentiment Distribution')
                    
                    return fig  # Return the figure object
                    

                # Read the text file
                with open(r'C:\Users\Kwaku\Desktop\project_final\upload_txt.txt', 'r') as file:
                    text = file.read()

                if text:
                  # Sentiment Analysis
                    sentiment = analyze_sentiment_vader(text)
                    highest, score = highest_sentiment(sentiment)
                    st.markdown('<h1 style="font-size: 1rem; margin-top: 0;">Sentimental analysis results:</h1>', unsafe_allow_html=True)
                    score = score * 10
                    st.write(f"The text shows a {highest} sentiment with a score of {score}/10")

                    # Create and display the sentiment distribution chart
                    fig = plot_sentiment_distribution(sentiment)
                    st.plotly_chart(fig)

                 # Visualizations
                plot_sentiment_distribution(sentiment)
   

                