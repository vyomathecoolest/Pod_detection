import pandas as pd
from imutils import paths
import cv2
import os


def variance_of_laplacian(image):
    return cv2.Laplacian(image, cv2.CV_64F).var()


image_folder = r"D:\internship\data\downloaded_images"
output_folder = r"D:\internship\data\blur_classified"
os.makedirs(output_folder, exist_ok=True)
os.makedirs(os.path.join(output_folder, "blurry"), exist_ok=True)
os.makedirs(os.path.join(output_folder, "not_blurry"), exist_ok=True)

threshold = 100.0

data = []

for imagePath in paths.list_images(image_folder):
    image = cv2.imread(imagePath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    fm = variance_of_laplacian(gray)

    if fm >= threshold:
        label = "Not Blurry"
        dest_folder = "not_blurry"
    else:
        label = "Blurry"
        dest_folder = "blurry"

    save_path = os.path.join(output_folder, dest_folder, os.path.basename(imagePath))
    cv2.imwrite(save_path, image)

    data.append({
        "filename": os.path.basename(imagePath),
        "blur_score": fm,
        "label": label
    })

df = pd.DataFrame(data)
excel_path = os.path.join(output_folder, "blur_results.xlsx")
df.to_excel(excel_path, index=False)

print(f"Blur detection complete. Results saved in {excel_path}")