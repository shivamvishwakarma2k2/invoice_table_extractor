import os
import cv2

from preprocessing.image_cleaner import load_image, preprocess_for_ocr
from layout_detection.layout_model import detect_layout
from table_extraction.extractor import extract_clean_table
from ocr.ocr_engine import run_ocr
from structure.line_detector import detect_table_lines
from structure.row_detector import detect_rows


def test_step6():

    INPUT_IMAGE = "test_images/invoice1.jpg"
    OUTPUT_DIR = "test_outputs/step6_rows"

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("STEP-1: Load image")
    image = load_image(INPUT_IMAGE)

    print("STEP-2: Layout detection")
    layout = detect_layout(image)

    table_img = extract_clean_table(image, layout.tables[0]["bbox"])

    print("STEP-4: OCR")
    ocr_ready = preprocess_for_ocr(table_img)
    words = run_ocr(ocr_ready)

    print("STEP-5: Line detection")
    line_info = detect_table_lines(table_img)

    print("STEP-6: Row detection")
    rows = detect_rows(table_img, line_info, words)

    print(f"Rows detected: {len(rows)}")

    

    # Visualization
    vis = table_img.copy()

    for r in rows:

        cv2.rectangle(
            vis,
            (0, r["y1"]),
            (vis.shape[1], r["y2"]),
            (255, 0, 0),
            1
        )

    output_path = os.path.join(OUTPUT_DIR, "rows_detected.png")
    cv2.imwrite(output_path, vis)

    print("Row visualization saved:", output_path)


if __name__ == "__main__":
    test_step6()
