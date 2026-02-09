import cv2
from paddleocr import PaddleOCR


# Initialize PaddleOCR in stable CPU mode
# oneDNN / MKLDNN disabled for Windows stability
ocr_model = PaddleOCR(
    use_angle_cls=True,   # angle classification
    lang='en',            # English OCR
    # use_gpu=False,        # force CPU mode
    enable_mkldnn=False   # disable oneDNN/MKLDNN backend
)


def is_valid_word(word):
    """
    Generic OCR noise filter.
    Keeps only valid bounding boxes and meaningful text.
    No invoice-specific logic.
    """
    return (
        isinstance(word["text"], str) and
        len(word["text"].strip()) > 0 and
        word["x2"] > word["x1"] and
        word["y2"] > word["y1"]
    )


def safe_parse_text_conf(data):
    """
    Safely extract text and confidence from PaddleOCR output.
    Handles multiple formats:
    - (text, conf)
    - [text, conf]
    - "text"
    """
    if isinstance(data, tuple) and len(data) == 2:
        return str(data[0]), float(data[1])

    if isinstance(data, list) and len(data) == 2:
        return str(data[0]), float(data[1])

    if isinstance(data, str):
        return data, 0.0

    return "", 0.0


def safe_parse_box(box):
    """
    Safely extract numeric bounding box coordinates.

    Expected format:
    [ [x1,y1], [x2,y2], [x3,y3], [x4,y4] ]

    Returns:
        (x1, y1, x2, y2) or None if invalid
    """

    # Must be list-like
    if not isinstance(box, (list, tuple)):
        return None

    # Must have at least 4 points
    if len(box) < 4:
        return None

    xs = []
    ys = []

    for point in box:
        # Each point must be [x, y]
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            return None

        x, y = point

        # Must be numeric
        if not (isinstance(x, (int, float)) and isinstance(y, (int, float))):
            return None

        xs.append(int(x))
        ys.append(int(y))

    return min(xs), min(ys), max(xs), max(ys)


def run_ocr(table_image):
    """
    Perform word-level OCR using PaddleOCR.

    Args:
        table_image: Cropped and preprocessed table image (BGR or grayscale)

    Returns:
        List of dicts:
        {
            text,
            x1, y1, x2, y2,
            confidence
        }
    """

    # Ensure image is in BGR format for PaddleOCR
    if len(table_image.shape) == 2:
        image = cv2.cvtColor(table_image, cv2.COLOR_GRAY2BGR)
    else:
        image = table_image.copy()

    # Run OCR
    results = ocr_model.ocr(image)

    words = []

    # PaddleOCR output is highly version dependent
    # We parse defensively

    for line in results:
        for item in line:

            # item should be [box, text_info]
            if not isinstance(item, (list, tuple)) or len(item) < 2:
                continue

            box = item[0]
            text_info = item[1]

            # Safely parse box
            box_coords = safe_parse_box(box)
            if box_coords is None:
                continue

            x1, y1, x2, y2 = box_coords

            # Safely parse text + confidence
            text, conf = safe_parse_text_conf(text_info)

            if not text.strip():
                continue

            word = {
                "text": text.strip(),
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "confidence": float(conf)
            }

            # Generic validation
            if is_valid_word(word):
                words.append(word)

    return words


# # Alternative Tesseract OCR implementation

# import cv2
# import pytesseract
# import pandas as pd


# # for Windows
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# def is_valid_word(word):
#     """
#     Generic filter to remove OCR noise and table border artifacts.
#     No invoice-specific rules.
#     """
#     return (
#         len(word["text"]) > 1 and
#         word["confidence"] >= 0.5 and
#         word["x2"] > word["x1"] and
#         word["y2"] > word["y1"]
#     )


# def run_ocr(table_image):
#     """
#     Perform word-level OCR on a cleaned table image.

#     Returns:
#         List of dicts:
#         {
#             text,
#             x1, y1, x2, y2,
#             confidence
#         }
#     """

#     # Ensure RGB for Tesseract
#     if len(table_image.shape) == 2:
#         rgb = cv2.cvtColor(table_image, cv2.COLOR_GRAY2RGB)
#     else:
#         rgb = cv2.cvtColor(table_image, cv2.COLOR_BGR2RGB)

#     # Generic OCR config (no invoice tuning)
#     custom_config = r"--oem 3 --psm 6"

#     data = pytesseract.image_to_data(
#         rgb,
#         config=custom_config,
#         output_type=pytesseract.Output.DATAFRAME
#     )

#     words = []

#     for _, row in data.iterrows():
#         if pd.isna(row["text"]):
#             continue

#         text = str(row["text"]).strip()
#         conf = float(row["conf"])

#         if text == "" or conf < 0:
#             continue

#         x = int(row["left"])
#         y = int(row["top"])
#         w = int(row["width"])
#         h = int(row["height"])

#         word = {
#             "text": text,
#             "x1": x,
#             "y1": y,
#             "x2": x + w,
#             "y2": y + h,
#             "confidence": conf / 100.0
#         }

#         if is_valid_word(word):
#             words.append(word)

#     return words
