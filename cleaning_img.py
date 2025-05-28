import cv2
import pytesseract
import numpy as np
import os
import shutil

# CONFIG
INPUT_FOLDERS = [
    "D:\\internship\\data\\classified_by_lsp\\BLDT",
    "D:\\internship\\data\\classified_by_lsp\\DLHV",
    "D:\\internship\\data\\classified_by_lsp\\GATI",
    "D:\\internship\\data\\classified_by_lsp\\SFEX1"
]

ERROR_FOLDER = "D:/internship/data/PODImages_Error"
os.makedirs(ERROR_FOLDER, exist_ok=True)


def rotate_image(img, angle):
    if angle == 90:
        return cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
    elif angle == 180:
        return cv2.rotate(img, cv2.ROTATE_180)
    elif angle == 270:
        return cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
    return img  # 0


def get_text_score_and_angle(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray, config='--psm 6')
    box_data = pytesseract.image_to_boxes(gray)

    angles = []

    for line in box_data.strip().split('\n'):
        parts = line.split()
        if len(parts) >= 6:
            x1, y1, x2, y2 = map(int, parts[1:5])
            angle = np.degrees(np.arctan2((y2 - y1), (x2 - x1)))
            if abs(x2 - x1) > abs(y2 - y1):  # prefer horizontal
                angles.append(angle)

    median_angle = np.median(angles) if angles else 999
    return len(text.strip()), abs(median_angle)


def evaluate_best_rotation(img):
    best_angle = 0
    best_score = 0
    best_angle_score = 999
    h, w = img.shape[:2]
    aspect_hint = "tall" if h > w else "wide"

    print(f"📐 Aspect ratio hint: {aspect_hint} (h={h}, w={w})")

    for angle in [0, 90, 180, 270]:
        rotated = rotate_image(img, angle)
        text_len, median_angle = get_text_score_and_angle(rotated)
        print(f"🔁 {angle}° → {text_len} chars, median text angle: {median_angle:.1f}")

        rotated_h, rotated_w = rotated.shape[:2]
        rotated_aspect = "tall" if rotated_h > rotated_w else "wide"

        # Boost score if aspect matches original orientation expectation
        aspect_bonus = 20 if rotated_aspect == aspect_hint else 0
        adjusted_score = text_len + aspect_bonus

        if (adjusted_score > best_score) or (adjusted_score == best_score and median_angle < best_angle_score):
            best_score = adjusted_score
            best_angle_score = median_angle
            best_angle = angle

    print(f"✅ Chosen angle: {best_angle}° (score: {best_score}, angle: {best_angle_score:.1f})")
    return best_angle


def process_images_in_folder(folder):
    image_files = [f for f in os.listdir(folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    print(f"📂 Processing folder: {folder} - {len(image_files)} images")

    for filename in image_files:
        image_path = os.path.join(folder, filename)

        img = cv2.imread(image_path)
        if img is None:
            # Optional: log or count failed reads silently
            continue

        try:
            best_rotation = evaluate_best_rotation(img)
            if best_rotation != 0:
                corrected = rotate_image(img, best_rotation)
                cv2.imwrite(image_path, corrected)
                # Commented out detailed prints
                # print(f"✅ Saved rotated image: {filename} by {best_rotation}°")
            else:
                # print(f"✅ Already upright: {filename}")
                pass
        except Exception as e:
            # You may log errors silently or count them
            shutil.move(image_path, os.path.join(ERROR_FOLDER, filename))

def evaluate_best_rotation(img):
    # You can keep this silent by removing print statements
    best_angle = 0
    best_score = 0
    best_angle_score = 999
    h, w = img.shape[:2]
    aspect_hint = "tall" if h > w else "wide"

    for angle in [0, 90, 180, 270]:
        rotated = rotate_image(img, angle)
        text_len, median_angle = get_text_score_and_angle(rotated)

        rotated_h, rotated_w = rotated.shape[:2]
        rotated_aspect = "tall" if rotated_h > rotated_w else "wide"

        aspect_bonus = 20 if rotated_aspect == aspect_hint else 0
        adjusted_score = text_len + aspect_bonus

        if (adjusted_score > best_score) or (adjusted_score == best_score and median_angle < best_angle_score):
            best_score = adjusted_score
            best_angle_score = median_angle
            best_angle = angle

    return best_angle

def process_all_folders():
    for folder in INPUT_FOLDERS:
        process_images_in_folder(folder)

if __name__ == "__main__":
    print("Tesseract path:", pytesseract.pytesseract.tesseract_cmd)
    process_all_folders()
    print("\n🎉 All images processed.")

