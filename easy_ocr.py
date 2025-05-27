import re
import pytesseract
from PIL import Image
import cv2
import numpy as np


def preprocess_image(image_path):


    image = cv2.imread(image_path)


    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


    thresh = cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )

    # Optional: Denoise (e.g., median blur)
    denoised = cv2.medianBlur(thresh, 3)

    return denoised


def extract_docket_number(image_path):

    processed_img = preprocess_image(image_path)
    pil_img = Image.fromarray(processed_img)


    text = pytesseract.image_to_string(
        pil_img,
        config="--psm 6 --oem 3"
    )


    matches = re.findall(r"\b\d{9}\b", text)

    return matches



image_path = "vyoma.jpg"
docket_numbers = extract_docket_number(image_path)

if docket_numbers:
    print("Docket Number(s) found:", docket_numbers)
else:
    print("No docket number found.")
    print("Try adjusting preprocessing or regex pattern.")
