import streamlit as st
import os
import subprocess
from PIL import Image

# Paths to directories
UPLOAD_FOLDER = 'prototype_v1/uploads'
OUTPUT_FOLDER = 'prototype_v1/frames_output'

# Create upload directory if it does not exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Streamlit interface for file upload
st.title("Video Upload and Frame Extraction")

# File uploader allows user to add their video
uploaded_file = st.file_uploader("Choose a video file...", type=["mp4", "avi", "mov"])

if uploaded_file is not None:
    # Save the uploaded video file to the UPLOAD_FOLDER
    video_path = os.path.join(UPLOAD_FOLDER, uploaded_file.name)
    with open(video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Use app.py to process the video and extract frames
    # Assuming app.py is in the same directory as strm1.py and has necessary functions
    from app import process_video, allowed_file
    if allowed_file(uploaded_file.name):
        frames_folder_path = process_video(video_path, OUTPUT_FOLDER)
        
        # Display the frames
        st.subheader("Extracted Frames:")
        if frames_folder_path:
            frame_files = sorted(os.listdir(frames_folder_path))  # Sort if necessary
            for frame_file in frame_files:
                frame_path = os.path.join(frames_folder_path, frame_file)
                image = Image.open(frame_path)
                st.image(image, caption=frame_file)
        else:
            st.error("An error occurred while processing the video.")
    else:
        st.error("This file type is not allowed.")
