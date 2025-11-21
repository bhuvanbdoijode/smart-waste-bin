import cv2
import numpy as np

def detect_fill(path):
    img = cv2.imread(path)
    img = cv2.resize(img, (500, 500))

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)

    # Strong edge detection
    edges = cv2.Canny(blur, 50, 150)

    # Find all contours
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return 0

    # The bin opening is the largest contour near the top of the image
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    # Pick the largest contour (likely the trash outline)
    cnt = contours[0]

    # Create a mask for the detected area
    mask = np.zeros_like(gray)
    cv2.drawContours(mask, [cnt], -1, 255, thickness=-1)

    # Apply mask
    masked = cv2.bitwise_and(gray, gray, mask=mask)

    # Adaptive threshold on masked area
    thresh = cv2.adaptiveThreshold(masked, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY_INV,
                                   11, 2)

    # Calculate fill percentage inside the detected bin area
    filled = cv2.countNonZero(thresh)
    total = cv2.countNonZero(mask)

    if total == 0:
        return 0

    percent = int((filled / total) * 100)
    percent = min(max(percent, 0), 100)

    return percent
