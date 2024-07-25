import sys
from transformers import DetrImageProcessor, DetrForObjectDetection
import torch
from PIL import Image, ImageDraw
import os

if len(sys.argv) != 3:
    print("Usage: python detection.py <input_folder> <output_folder>")
    sys.exit(1)

input_folder = sys.argv[1]
output_folder = sys.argv[2]

def save_image_with_all_boxes(image, results, output_path, threshold=0.9):
    try:
        annotated_image = image.copy()
        draw = ImageDraw.Draw(annotated_image)

        for score, label, box in zip(results["scores"], results["labels"], results["boxes"]):
            if score >= threshold:
                box = [int(round(i)) for i in box.tolist()]
                label_str = model.config.id2label[label.item()]
                draw.rectangle(box, outline="red")
                draw.text((box[0], box[1]), f'{label_str} {score:.3f}', fill="red")

        annotated_image.save(output_path)
        print(f"Saved annotated image to: {output_path}")
    except Exception as e:
        print(f"Error saving image {output_path}: {str(e)}")

try:
    processor = DetrImageProcessor.from_pretrained("facebook/detr-resnet-50")
    model = DetrForObjectDetection.from_pretrained("facebook/detr-resnet-50")

    for root, dirs, files in os.walk(input_folder):
        for folder_name in dirs:
            folder_dir = os.path.join(root, folder_name)
            output_dir = os.path.join(output_folder, folder_name)
            os.makedirs(output_dir, exist_ok=True)

            for filename in os.listdir(folder_dir):
                if filename.lower().endswith((".jpg", ".jpeg", ".png")):
                    image_path = os.path.join(folder_dir, filename)
                    output_path = os.path.join(output_dir, filename)

                    try:
                        image = Image.open(image_path)
                        inputs = processor(images=image, return_tensors="pt")
                        outputs = model(**inputs)
                        target_sizes = torch.tensor([image.size[::-1]])
                        results = processor.post_process_object_detection(outputs, target_sizes=target_sizes, threshold=0.9)[0]
                        save_image_with_all_boxes(image, results, output_path)
                    except Exception as e:
                        print(f"Error processing image {filename}: {str(e)}")
except Exception as e:
    print(f"Error initializing model or processing directories: {str(e)}")
    sys.exit(2)
