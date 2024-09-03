import google.generativeai as genai
import PIL.Image
import pandas as pd
import streamlit as st
import json
import io
from io import BytesIO
from PyPDF2 import PdfReader
from docx import Document
from upload import handle_file_upload
import cv2
import numpy as np
from PIL import Image
import librosa
from dotenv import load_dotenv
import os



genai_api = os.getenv('genai_api')
#genai_api = st.secrets['genai_api']
genai.configure(api_key=genai_api)

# Define the generative model
model = genai.GenerativeModel(model_name="gemini-1.5-flash")

def configure():
        load_dotenv()

def process_image(file, query):
    img = PIL.Image.open(file)
    response = model.generate_content([query, img])
    return response

def process_text(file, query):
    text = file.read().decode("utf-8")
    response = model.generate_content([query, text])
    return response

def process_pdf(file, query):
    pdf = PdfReader(file)
    text = ""
    for page in pdf.pages:
        text += page.extract_text()
    response = model.generate_content([query, text])
    return response

def process_csv(file, query):
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    df = None
    for encoding in encodings:
        try:
            file.seek(0)  # Reset file pointer to the beginning
            df = pd.read_csv(file, encoding=encoding)
            if not df.empty:
                break  # Exit the loop if reading is successful and DataFrame is not empty
        except (UnicodeDecodeError, pd.errors.ParserError) as e:
            continue  # Try the next encoding if there's an error

    if df is None or df.empty:
        return "Failed to read the CSV file or the file is empty."

    summary = df.describe().to_string()
    response = model.generate_content([query, summary])
    return response


def process_xlsx(file, query):
    df = pd.read_excel(file)
    summary = df.describe().to_string()
    response = model.generate_content([query, summary])
    return response

def process_docx(file, query):
    doc = Document(file)
    text = "\n".join([p.text for p in doc.paragraphs])
    response = model.generate_content([query, text])
    return response

def process_json(file, query):
    data = json.load(file)
    summary = json.dumps(data, indent=2)
    response = model.generate_content([query, summary])
    return response

def process_audio(file, query):
    # Load the audio file
    y, sr = librosa.load(file)
    
    # Extract features
    chroma = librosa.feature.chroma_stft(y=y, sr=sr)
    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    
    # Prepare a summary of the audio features
    summary = f"""
    Audio file analysis:
    - Duration: {librosa.get_duration(y=y, sr=sr):.2f} seconds
    - Estimated tempo: {tempo:.2f} BPM
    - Chroma features shape: {chroma.shape}
    - MFCC features shape: {mfccs.shape}
    """
    
    # Generate content based on the query and audio summary
    response = model.generate_content([query, summary])
    return response

def process_video(file, query):
    # Save the uploaded file to a temporary location
    with open("temp_video.mp4", "wb") as f:
        f.write(file.getvalue())
    
    # Open the video file
    video = cv2.VideoCapture("temp_video.mp4")
    
    # Get video properties
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    
    # Read the first frame
    ret, frame = video.read()
    
    # Convert the frame to RGB (from BGR)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Create a PIL Image from the frame
    pil_image = Image.fromarray(frame_rgb)
    
    # Prepare a summary of the video
    summary = f"""
    Video file analysis:
    - Duration: {duration:.2f} seconds
    - Frame rate: {fps:.2f} FPS
    - Total frames: {frame_count}
    - Resolution: {frame.shape[1]}x{frame.shape[0]}
    """
    
    # Generate content based on the query, video summary, and first frame
    response = model.generate_content([query, summary, pil_image])
    
    # Release the video capture object
    video.release()
    
    return response
def query_data():
    configure()
    st.markdown('<h1 style="font-size: 1rem; margin-top: 0;">Query your media</h1>', unsafe_allow_html=True)
    uploaded_files, dfs_tabular, dfs_non_tabular = handle_file_upload(page_name=query_data)
    if 'history' not in st.session_state:
        st.session_state.history = []

    query = st.text_input("Ask a question about the uploaded file:")

    if st.button("Submit Query", type='primary'):
       for uploaded_file in uploaded_files:
        if uploaded_file and query:
            file_type = uploaded_file.name.split('.')[-1].lower()
            response = None

            if file_type in ["jpg", "jpeg", "png"]:
                response = process_image(uploaded_file, query)
            elif file_type in ["txt"]:
                response = process_text(uploaded_file, query)
            elif file_type in ["pdf"]:
                response = process_pdf(uploaded_file, query)
            elif file_type in ["csv"]:
                response = process_csv(uploaded_file, query)
            elif file_type in ["xlsx"]:
                response = process_xlsx(uploaded_file, query)
            elif file_type in ["docx"]:
                response = process_docx(uploaded_file, query)
            elif file_type in ["json"]:
                response = process_json(uploaded_file, query)
            elif file_type in ["mp3", "wav"]:
                response = process_audio(uploaded_file, query)
            elif file_type in ["mp4"]:
                response = process_video(uploaded_file, query)

            if response and hasattr(response, 'parts'):
                response_text = "\n".join(part.text for part in response.parts)
            else:
                response_text = "No response or unsupported file type."

            # Add the query and response to history
            st.session_state.history.append({"query": query, "response": response_text})

        elif not query:
            st.warning("Please enter a query.")

    # Display chat history
    if st.session_state.history:
        st.markdown('<h1 style="font-size: 1rem; margin-top: 0;">Chat History</h1>', unsafe_allow_html=True)
        for entry in st.session_state.history:
            st.write(f"**You:** {entry['query']}")
            st.write(f"**AI:** {entry['response']}")

