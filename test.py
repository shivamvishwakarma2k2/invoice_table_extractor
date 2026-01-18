import os
import cv2

from preprocessing.image_cleaner import (
    load_image,
    preprocess_image
)
from layout_detection.layout_model import detect_layout
from table_extraction.extractor import extract_clean_table
from ocr.ocr_engine import run_ocr


def test():

    INPUT_IMAGE = "test_images/batch3-1895.jpg"
    OUTPUT_DIR = "test_outputs/step4"

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("STEP 1: Load image")
    image = load_image(INPUT_IMAGE)

    print("STEP 2: Detect table layout")
    layout = detect_layout(image)
    if not layout.has_table:
        print("No table detected")
        return

    print("STEP 3: Crop table")
    table_img = extract_clean_table(image, layout.tables[0]["bbox"])

    print("STEP 4: Preprocess for OCR and OCR Run")
    clean = preprocess_image(table_img)
    # clean = remove_table_lines(clean)
    words = run_ocr(clean)
    print(words)
    print(f"OCR detected {len(words)} valid words")

    # Draw OCR boxes for visual verification
    vis_img = table_img.copy()
    for w in words:
        cv2.rectangle(
            vis_img,
            (w["x1"], w["y1"]),
            (w["x2"], w["y2"]),
            (0, 255, 0),
            1
        )

    output_path = os.path.join(OUTPUT_DIR, "ocr_words.png")
    cv2.imwrite(output_path, vis_img)

    print(f"OCR visualization saved : {output_path}")


if __name__ == "__main__":
    test()
