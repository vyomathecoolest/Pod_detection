import re
import cv2
import numpy as np
import easyocr
from PIL import Image

def preprocess_image(image_path):
    """Preprocess the image to improve OCR accuracy."""
    # Read image using OpenCV
    image = cv2.imread(image_path)


    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    
    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )

    
    denoised = cv2.medianBlur(thresh, 3)

    return denoised

def extract_docket_number(image_path):
    
    processed_img = preprocess_image(image_path)

    
    processed_img_rgb = cv2.cvtColor(processed_img, cv2.COLOR_GRAY2RGB)


    reader = easyocr.Reader(['en'])

    # Perform OCR on processed image
    result = reader.readtext(processed_img_rgb, detail=0)  # detail=0 returns text only

    # Join all recognized text into one string for regex search
    text = " ".join(result)

    
    matches = re.findall(r"\b\d{9}\b", text)

    return matches

# Example usage
image_path = "vyoma.jpg"  # Replace with your image path
docket_numbers = extract_docket_number(image_path)

if docket_numbers:
    print("Docket Number(s) found:", docket_numbers)
else:
    print("No docket number found.")
    print("Try adjusting preprocessing or regex pattern.")
