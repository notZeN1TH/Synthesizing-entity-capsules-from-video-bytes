import streamlit as st
import os
from PIL import Image
import subprocess

# Paths to directories
UPLOAD_FOLDER = 'prototype_v1/uploads'
OUTPUT_FOLDER = 'prototype_v1/frames_output'

# Create upload directory if it does not exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Streamlit interface for file upload
st.title("Video Upload and Frame Extraction")

# File uploader allows user to add their video. Ensure to pass a unique key to the file_uploader.
uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "avi", "mov"], key="unique_upload_key")

if uploaded_file is not None:
    # Save the uploaded video file to the UPLOAD_FOLDER
    video_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    # Use app.py to process the video and extract frames
    # Assume app.py is in the same directory as strm1.py and has the necessary functions imported
    # Here, we import inside the if-statement to prevent re-importing which causes the error
    if 'app' not in st.session_state:
        from app import process_video, allowed_file
        st.session_state['app'] = (process_video, allowed_file)

    process_video, allowed_file = st.session_state['app']

    if allowed_file(uploaded_file.name):
        frames_folder_path = process_video(video_path, OUTPUT_FOLDER)

        # Display the frames
        st.subheader("Extracted Frames:")
        if frames_folder_path:
            frame_files = sorted(os.listdir(frames_folder_path))  # Sort
