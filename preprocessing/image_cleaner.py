import cv2
import numpy as np
from PIL import Image
from pdf2image import convert_from_path
import os

def load_image(file_path):
    """
    Loads invoice from image or PDF and returns OpenCV image.
    """
    if file_path.lower().endswith(".pdf"):
        pages = convert_from_path(file_path, dpi=300)
        image = np.array(pages[0])   # take first page
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    else:
        image = cv2.imread(file_path)

    if image is None:
        raise Exception("Invalid file or corrupted image")

    return image


def resize_image(image, max_width=2000):
    h, w = image.shape[:2]
    if w > max_width:
        scale = max_width / w
        image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    return image


def convert_to_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)



def remove_noise(gray):
    return cv2.fastNlMeansDenoising(gray, h=15)


def binarize_image(gray):
    return cv2.adaptiveThreshold(
        gray, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        15, 11
    )



def enhance_text(binary):
    kernel = np.ones((2,2), np.uint8)
    return cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)



def preprocess_image(image):
    image = resize_image(image)
    gray = convert_to_grayscale(image)
    noise_free = remove_noise(gray)
    binary = binarize_image(noise_free)
    enhanced = enhance_text(binary)
    return enhanced


def preprocess_for_ocr(image):
    """
    Preprocessing pipeline specifically for PaddleOCR.

    PaddleOCR works better on natural-looking images.
    So we avoid aggressive binarization and morphology.

    Steps:
    - Resize
    - Light denoise
    - Grayscale
    - Contrast normalization
    """

    # Resize for consistency
    image = resize_image(image)

    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()

    # Light noise removal (not aggressive)
    gray = cv2.GaussianBlur(gray, (3, 3), 0)

    # Contrast normalization (keeps texture)
    gray = cv2.normalize(gray, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

    # Convert back to BGR (PaddleOCR prefers BGR/RGB)
    ocr_ready = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)

    return ocr_ready



# def remove_table_lines(binary_img):
#     """
#     Generic table-line removal for grid-based documents.
#     Works for ANY invoice.
#     """
#     img = binary_img.copy()

#     # Vertical lines
#     vertical_kernel = cv2.getStructuringElement(
#         cv2.MORPH_RECT, (1, img.shape[0] // 30)
#     )
#     vertical_lines = cv2.morphologyEx(img, cv2.MORPH_OPEN, vertical_kernel)
#     img = cv2.subtract(img, vertical_lines)

#     # Horizontal lines
#     horizontal_kernel = cv2.getStructuringElement(
#         cv2.MORPH_RECT, (img.shape[1] // 30, 1)
#     )
#     horizontal_lines = cv2.morphologyEx(img, cv2.MORPH_OPEN, horizontal_kernel)
#     img = cv2.subtract(img, horizontal_lines)

#     return img
