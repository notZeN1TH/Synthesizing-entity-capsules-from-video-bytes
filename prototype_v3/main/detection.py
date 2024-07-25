from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
from PIL import Image, ImageDraw
import os

# Function to save image with bounding boxes
def save_image_with_boxes(image, results, output_folder, image_name, threshold=0.9):
    # Create output folder if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # Create a copy of the input image
    annotated_image = image.copy()
    draw = ImageDraw.Draw(annotated_image)

    # Loop through each detected object
    for idx, (score, label, box) in enumerate(zip(results["scores"], results["labels"], results["boxes"])):
        if score >= threshold:
            box = [int(round(i)) for i in box.tolist()]
            label_str = model.config.id2label[label.item()]

            # Draw bounding box on the annotated image
            draw.rectangle(box, outline="red")
            draw.text((box[0], box[1]), f'{label_str} {score:.3f}', fill="red")

    # Save the annotated image with bounding boxes
    annotated_image.save(os.path.join(output_folder, f"{image_name}_annotated.jpg"))
    print(f"Saved annotated image with bounding boxes to: {output_folder}/{image_name}_annotated.jpg")

# Initialize the processor and model
processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50", revision="no_timm")
model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50", revision="no_timm")

# Define input and output directories
input_folder = "frames_output"
output_folder = "annotated_images"

# Iterate through each subfolder in the input directory
for foldername in os.listdir(input_folder):
    subfolder_path = os.path.join(input_folder, foldername)

    # Skip files directly in the input directory
    if not os.path.isdir(subfolder_path):
        continue

    # Create corresponding output subfolder
    output_subfolder = os.path.join(output_folder, foldername)
    os.makedirs(output_subfolder, exist_ok=True)

    # Process each image within the subfolder
    for filename in os.listdir(subfolder_path):
        if filename.endswith(('.jpg', '.jpeg', '.png')):  # Check for image files
            image_path = os.path.join(subfolder_path, filename)
            image_name = os.path.splitext(filename)[0]

            # Load image
            image = Image.open(image_path)

            # Preprocess the image
            inputs = processor(images=image, return_tensors="pt")

            # Perform object detection
            outputs = model(**inputs)

            # Convert outputs (bounding boxes and class logits) to COCO API format
            target_sizes = torch.tensor([image.size[::-1]])
            results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]

            # Save annotated image with bounding boxes
            save_image_with_boxes(image, results, output_subfolder, image_name)

print("Object detection and annotation completed for all images.")
