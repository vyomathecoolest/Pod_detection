import cv2
import pytesseract
import re
import os
import pandas as pd

# Paths
folder_path = r"C:\Users\vyoma\OneDrive\Documents\Desktop\internship\classified_by_lsp\resized_sfex4"
excel_path = r"C:\Users\vyoma\OneDrive\Documents\Desktop\internship\blur_classified\blur_results.xlsx"  # Replace with your file path

# Fixed bounding box coordinates
x, y, w, h = 713, 23, 1317, 311

# OCR config
custom_config = r'--oem 3 --psm 6'

# Load existing Excel file
df = pd.read_excel(excel_path)

# Optional: make sure filenames in Excel match your image filenames
df['filename'] = df['filename'].astype(str).str.lower().str.strip()

# Store predictions
predictions = []


def process_image(image_path):
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not load image {image_path}")
        return ""

    # Crop and preprocess
    cropped = image[y:y + h, x:x + w]
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)
    blurred = cv2.GaussianBlur(resized, (3, 3), 0)

    # OCR
    text = pytesseract.image_to_string(blurred, config=custom_config)
    text = text.replace('\n', ' ').strip()

    # Extract pattern like "1000 2105 6000"
    match = re.findall(r'\b\d{4}\s\d{4}\s\d{4}\b', text)

    return match[0] if match else ""


# Loop through images and add predictions
for filename in os.listdir(folder_path):
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
        filepath = os.path.join(folder_path, filename)
        result = process_image(filepath)
        predictions.append((filename.lower().strip(), result))
        print(f"{filename}: {result}")

# Merge predictions into DataFrame
pred_dict = dict(predictions)
df['predicted sfex'] = df['filename'].map(pred_dict)

# Save back to Excel
df.to_excel(excel_path, index=False)
print("Updated Excel file with predictions.")
