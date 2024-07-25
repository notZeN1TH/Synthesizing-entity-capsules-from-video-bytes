import os
import cv2
import uuid
import subprocess  # Import subprocess here
import streamlit as st
from PIL import Image

# Define paths relative to the 'prototype_v2/FINAL' directory
prototype_dir = 'prototype_v2'
final_dir = os.path.join(prototype_dir, 'FINAL')
frames_output_dir = os.path.join(final_dir, 'frames_output')
output_dir = os.path.join(final_dir, 'output')

# Ensure directories exist
os.makedirs(frames_output_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

st.title("Synthesizing entity capsules from video bytes")

# Function to check file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp4', 'avi', 'mov'}

# Function to process video and save frames
def process_video(video_path, output_folder):
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    unique_folder_name = f"{video_name}_{uuid.uuid4().hex}"
    output_folder_path = os.path.join(output_folder, unique_folder_name)
    os.makedirs(output_folder_path, exist_ok=True)

    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        raise IOError(f"Error: Could not open video '{video_path}'")
    
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
    return unique_folder_name

uploaded_file = st.file_uploader("Upload a video file", type=["mp4", "avi", "mov"], key="video_upload")

# If a file is uploaded
if uploaded_file is not None and allowed_file(uploaded_file.name):
    temp_video_path = os.path.join(final_dir, uploaded_file.name)
    with open(temp_video_path, "wb") as f:
        f.write(uploaded_file.getbuffer())

    try:
        unique_folder_name = process_video(temp_video_path, frames_output_dir)
        frames_folder_path = os.path.join(frames_output_dir, unique_folder_name)
        st.success("Video processed successfully.")

        st.subheader("Extracted Frames:")
        frame_files = sorted(os.listdir(frames_folder_path))
        for frame_file in frame_files:
            frame_path = os.path.join(frames_folder_path, frame_file)
            image = Image.open(frame_path)
            st.image(image, caption=frame_file)

        detection_script_path = os.path.join(final_dir, 'detection.py')
        subprocess_cmd = ['python', detection_script_path, frames_folder_path, os.path.join(output_dir, unique_folder_name)]
        process = subprocess.run(subprocess_cmd, capture_output=True, text=True, check=True)
        
        if process.returncode == 0:
            st.success("Detection completed successfully.")
            annotated_files = sorted(os.listdir(os.path.join(output_dir, unique_folder_name)))
            for annotated_file in annotated_files:
                annotated_frame_path = os.path.join(output_dir, unique_folder_name, annotated_file)
                image = Image.open(annotated_frame_path)
                st.image(image, caption=annotated_file)
        else:
            st.error(f"Detection failed: {process.stderr}")
            
    except Exception as e:
        st.error(f"An error occurred: {e}")
    finally:
        os.remove(temp_video_path)

