import cv2
import pytesseract
import pandas as pd


# for Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def is_valid_word(word):
    """
    Generic filter to remove OCR noise and table border artifacts.
    No invoice-specific rules.
    """
    return (
        len(word["text"]) > 1 and
        word["confidence"] >= 0.5 and
        word["x2"] > word["x1"] and
        word["y2"] > word["y1"]
    )


def run_ocr(table_image):
    """
    Perform word-level OCR on a cleaned table image.

    Returns:
        List of dicts:
        {
            text,
            x1, y1, x2, y2,
            confidence
        }
    """

    # Ensure RGB for Tesseract
    if len(table_image.shape) == 2:
        rgb = cv2.cvtColor(table_image, cv2.COLOR_GRAY2RGB)
    else:
        rgb = cv2.cvtColor(table_image, cv2.COLOR_BGR2RGB)

    # Generic OCR config (no invoice tuning)
    custom_config = r"--oem 3 --psm 6"

    data = pytesseract.image_to_data(
        rgb,
        config=custom_config,
        output_type=pytesseract.Output.DATAFRAME
    )

    words = []

    for _, row in data.iterrows():
        if pd.isna(row["text"]):
            continue

        text = str(row["text"]).strip()
        conf = float(row["conf"])

        if text == "" or conf < 0:
            continue

        x = int(row["left"])
        y = int(row["top"])
        w = int(row["width"])
        h = int(row["height"])

        word = {
            "text": text,
            "x1": x,
            "y1": y,
            "x2": x + w,
            "y2": y + h,
            "confidence": conf / 100.0
        }

        if is_valid_word(word):
            words.append(word)

    return words
