import os
import cv2
import uuid
import streamlit as st
from PIL import Image
import subprocess

# Define paths relative to the 'prototype_v2' directory
prototype_dir = 'prototype_v2'
final_dir = os.path.join(prototype_dir, 'FINAL')
frames_output_dir = os.path.join(final_dir, 'frames_output')
output_dir = os.path.join(final_dir, 'output')
allowed_extensions = {'mp4', 'avi', 'mov'}

# Function to process the video and extract frames
def process_video(video_path, output_folder):
    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        raise IOError(f"Error: Could not open video '{video_path}'")
    
    # Generate a unique folder name based on the video file's name
    video_filename = os.path.basename(video_path)
    video_name = os.path.splitext(video_filename)[0]
    unique_folder_name = f"{video_name}_{uuid.uuid4().hex}"
    output_folder_path = os.path.join(output_folder, unique_folder_name)
    os.makedirs(output_folder_path, exist_ok=True)
    
    current_frame = 0
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break
        frame_filename = f"frame_{current_frame}.jpg"
        frame_path = os.path.join(output_folder_path, frame_filename)
        cv2.imwrite(frame_path, frame)
        current_frame += 1
    
    video_capture.release()
    return output_folder_path

# Streamlit UI
st.title("Video Frame Processor")

uploaded_file = st.file_uploader("Upload a video file", type=list(allowed_extensions), key="video_upload")

# If a file is uploaded
if uploaded_file is not None:
    # Use the name of the uploaded file to create a directory
    video_name = os.path.splitext(uploaded_file.name)[0]
    video_dir = os.path.join(frames_output_dir, f"{video_name}_{uuid.uuid4().hex}")
    os.makedirs(video_dir, exist_ok=True)
    
    # Save uploaded file to the created directory
    video_path = os.path.join(video_dir, uploaded_file.name)
    with open(video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Process the video and extract frames
    try:
        frames_folder_path = process_video(video_path, frames_output_dir)
        st.success("Video processed successfully.")
        
        # Display the extracted frames
        st.subheader("Extracted Frames:")
        frame_files = sorted(os.listdir(frames_folder_path))
        for frame_file in frame_files:
            frame_path = os.path.join(frames_folder_path, frame_file)
            image = Image.open(frame_path)
            st.image(image, caption=frame_file)
    except Exception as e:
        st.error(f"An error occurred: {e}")

    # Call the detection script
    detection_script_path = os.path.join(final_dir, 'detection.py')
    try:
        subprocess.run(['python', detection_script_path], check=True)
        st.success("Detection completed successfully.")
        
        # Assume detection script outputs to a folder named after the video in 'output'
        output_frames_path = os.path.join(output_dir, os.path.basename(frames_folder_path))
        
        # Display the annotated frames
        st.subheader("Annotated Frames:")
        annotated_frame_files = sorted(os.listdir(output_frames_path))
        for annotated_frame_file in annotated_frame_files:
            annotated_frame_path = os.path.join(output_frames_path, annotated_frame_file)
            image = Image.open(annotated_frame_path)
            st.image(image, caption=annotated_frame_file)
            
    except subprocess.CalledProcessError as e:
        st.error(f"An error occurred during detection: {e}")
