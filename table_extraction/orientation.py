import cv2
import numpy as np


def detect_skew_angle(image):
    """
    Detect skew angle using Hough line transform.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)

    if lines is None:
        return 0.0

    angles = []
    for line in lines[:20]:
        rho, theta = line[0]
        angle = (theta - np.pi / 2) * (180 / np.pi)
        angles.append(angle)

    return np.median(angles)


def deskew_image(image):
    """
    Rotate image to correct skew.
    """
    angle = detect_skew_angle(image)

    if abs(angle) < 1.0:
        return image  # no correction needed

    h, w = image.shape[:2]
    center = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(
        image, M, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )

    return rotated
