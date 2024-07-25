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

# Path to your local image file
image_path = "frame_6.jpg"

# Initialize the processor and model
processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50", revision="no_timm")
model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50", revision="no_timm")

# Preprocess the image
image_name = os.path.splitext(os.path.basename(image_path))[0]
image = Image.open(image_path)
inputs = processor(images=image, return_tensors="pt")

# Perform object detection
outputs = model(**inputs)

# Convert outputs (bounding boxes and class logits) to COCO API format
target_sizes = torch.tensor([image.size[::-1]])
results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]

# Output folder to save annotated images with bounding boxes
annotated_images_folder = "annotated_images"

# Output folder to save original images without bounding boxes
original_images_folder = "original_images"

# Save annotated image with bounding boxes
save_image_with_boxes(image, results, annotated_images_folder, image_name)

# Save original image without bounding boxes
image.save(os.path.join(original_images_folder, f"{image_name}.jpg"))
print(f"Saved original image without bounding boxes to: {original_images_folder}/{image_name}.jpg")
