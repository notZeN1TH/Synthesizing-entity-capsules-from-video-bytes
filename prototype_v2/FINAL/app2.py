import os
from flask import Flask, request, redirect, url_for, render_template
import cv2

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'frames_output'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def process_video(video_path, output_folder):
    video_capture = cv2.VideoCapture(video_path)
    if not video_capture.isOpened():
        print("Error: Could not open video.")
        return
    
    os.makedirs(output_folder, exist_ok=True)
    
    current_frame = 0
    while True:
        ret, frame = video_capture.read()
        
        if not ret:
            break
        
        frame_filename = f"{output_folder}/frame_{current_frame}.jpg"
        cv2.imwrite(frame_filename, frame)
        
        print(f"Extracted frame {current_frame}")
        current_frame += 1
    
    video_capture.release()
    print("Frame extraction completed.")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        
        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process the uploaded video
            process_video(filepath, OUTPUT_FOLDER)
            
            return redirect(url_for('uploaded_file', filename=filename))
    
    return render_template('upload.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return f'Frames extracted from: {filename}'

if __name__ == '__main__':
    app.run(debug=True)
