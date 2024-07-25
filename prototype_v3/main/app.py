'''from flask import Flask, request, render_template
import cv2
import os
import uuid  # For generating unique identifiers

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
FRAMES_OUTPUT_FOLDER = 'frames_output'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}  # Allowed video file extensions

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_frames(video_path, output_folder):
    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0
    while success:
        frame_path = os.path.join(output_folder, f"frame_{count}.jpg")
        cv2.imwrite(frame_path, image)  # save frame as JPEG file
        success, image = vidcap.read()
        count += 1
    vidcap.release()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"

    file = request.files['file']

    if file.filename == '':
        return "No selected file"

    if file and allowed_file(file.filename):
        # Generate unique identifier for the video
        video_id = str(uuid.uuid4())
        video_folder = os.path.join(app.config['UPLOAD_FOLDER'], video_id)
        os.makedirs(video_folder, exist_ok=True)

        # Save the uploaded video file
        video_path = os.path.join(video_folder, file.filename)
        file.save(video_path)

        # Create a folder to store extracted frames for this video
        frames_output_folder = os.path.join(app.config['UPLOAD_FOLDER'], FRAMES_OUTPUT_FOLDER, video_id)
        os.makedirs(frames_output_folder, exist_ok=True)

        # Extract frames from the video
        extract_frames(video_path, frames_output_folder)

        return f"Frames extracted successfully! Video ID: {video_id}"

    return "Unsupported file format"

if __name__ == '__main__':
    app.run(debug=True)'''

import os
from flask import Flask, request, redirect, url_for, render_template
import cv2
import uuid  # For generating unique folder names

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'frames_output'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def process_video(video_path, output_folder):
    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        print(f"Error: Could not open video '{video_path}'")
        return
    
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
    return output_folder_path  # Return the path to the folder containing frames

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process the uploaded video
            frames_folder_path = process_video(filepath, OUTPUT_FOLDER)
            
            return redirect(url_for('uploaded_frames', folder_name=os.path.basename(frames_folder_path)))
    
    return render_template('upload.html')

@app.route('/uploads/<folder_name>')
def uploaded_frames(folder_name):
    return render_template('saved.html')

if __name__ == '__main__':
    app.run(debug=True)

