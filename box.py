import cv2

# Load image
image = cv2.imread("crazy.jpg")

# Let user draw the ROI (Region of Interest)
bbox = cv2.selectROI("Select Region", image, showCrosshair=True)

# This gives you (x, y, w, h)
x, y, w, h = bbox
print(f"Selected bounding box: x={x}, y={y}, w={w}, h={h}")

# Draw rectangle on the original image to show the selected area
image_with_box = image.copy()
cv2.rectangle(image_with_box, (x, y), (x + w, y + h), (0, 255, 0), 2)  # green box

cv2.imshow("Image with bounding box", image_with_box)
cv2.waitKey(0)

# Crop the image
cropped = image[y:y+h, x:x+w]

cv2.imshow("Cropped", cropped)
cv2.waitKey(0)
cv2.destroyAllWindows()
