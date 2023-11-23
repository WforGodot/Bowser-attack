import cv2
import numpy as np
import pytesseract

# Configure Tesseract path

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load the image
folder = 'c:\\Users\\proje\\Documents\\GitHub\\Bowser-attack\\bowser\\base_segment\\test_screenshots\\'
image = cv2.imread(folder + 'Screenshot 2023-11-21 151349.png')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Run Tesseract OCR
data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)

# Iterate through OCR result and remove text
n_boxes = len(data['level'])
for i in range(n_boxes):
    if int(data['conf'][i]) > 60:  # Confidence threshold
        (x, y, w, h) = (data['left'][i], data['top'][i], data['width'][i], data['height'][i])
        #cv2.rectangle(image, (x, y), (x + w, y + h), (255, 255, 255), -1)

# Apply adaptive thresholding
thresholded_image = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)

# Find contours on the thresholded image
contours, _ = cv2.findContours(thresholded_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

# Draw contours on the original image
cv2.drawContours(image, contours, -1, (0, 255, 0), 3)

# Display the result
cv2.imshow('Segmented Image', image)
cv2.waitKey(0)
cv2.destroyAllWindows()