import cv2
import numpy as np


def crop_table(image, bbox, padding=10):
    """
    Crop table from full invoice image.
    """
    h, w = image.shape[:2]
    x1, y1, x2, y2 = bbox

    # add padding safely
    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(w, x2 + padding)
    y2 = min(h, y2 + padding)

    table_img = image[y1:y2, x1:x2]

    return table_img


def remove_white_margins(table_img):
    """
    Remove extra white borders around the table.
    """
    gray = cv2.cvtColor(table_img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    coords = cv2.findNonZero(thresh)
    if coords is None:
        return table_img

    x, y, w, h = cv2.boundingRect(coords)
    cropped = table_img[y:y+h, x:x+w]

    return cropped
