# File: test_step7_pipeline.py

import os
import cv2

# Step 1
from preprocessing.image_cleaner import load_image, preprocess_for_ocr

# Step 2
from layout_detection.layout_model import detect_layout

# Step 3
from table_extraction.extractor import extract_clean_table

# Step 4
from ocr.ocr_engine import run_ocr

# Step 5
from structure.line_detector import detect_table_lines, classify_table_type

# Step 6
from structure.row_detector import detect_rows

# Step 7 (NEW)
from structure.column_detector import ColumnDetector


def test_step7():
    """
    Full pipeline test until Step-7 column detection.
    """

    INPUT_IMAGE = "test_images/invoice5.jpg"
    OUTPUT_DIR = "test_outputs/step7_full_pipeline"

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("STEP-1: Load image")
    image = load_image(INPUT_IMAGE)

    # --------------------------------------------------
    # STEP-2 Layout Detection
    # --------------------------------------------------

    print("STEP-2: Detect layout")
    layout = detect_layout(image)

    if not layout.has_table:
        print("No table detected")
        return

    print("Tables detected:", len(layout.tables))

    # --------------------------------------------------
    # STEP-3 Table Cropping
    # --------------------------------------------------

    print("STEP-3: Crop main table")

    table_bbox = layout.tables[0]["bbox"]
    table_img = extract_clean_table(image, table_bbox)

    cv2.imwrite(os.path.join(OUTPUT_DIR, "step3_table_crop.png"), table_img)

    # --------------------------------------------------
    # STEP-4 OCR
    # --------------------------------------------------

    print("STEP-4: OCR preprocessing")

    clean = preprocess_for_ocr(table_img)

    print("STEP-4: Run OCR")

    words = run_ocr(clean)

    print("OCR words detected:", len(words))

    # --------------------------------------------------
    # STEP-5 Line Detection
    # --------------------------------------------------

    print("STEP-5: Detect table lines")

    horizontal_lines, vertical_lines = detect_table_lines(clean)

    table_type = classify_table_type(horizontal_lines, vertical_lines)

    print("Table type:", table_type)

    # --------------------------------------------------
    # STEP-6 Row Detection
    # --------------------------------------------------

    print("STEP-6: Detect candidate rows")

    rows = detect_rows(words)

    print("Candidate rows detected:", len(rows))

    # --------------------------------------------------
    # STEP-7 Column Detection (NEW)
    # --------------------------------------------------

    print("STEP-7: Detect columns")

    column_detector = ColumnDetector(
        eps=45,          # clustering sensitivity
        min_samples=4    # min words to form column
    )

    columns = column_detector.detect_columns(words)

    print("Columns detected:", len(columns))
    print(columns)

    # --------------------------------------------------
    # Visualization
    # --------------------------------------------------

    vis_img = table_img.copy()

    # Draw row boundaries
    for r in rows:
        y1 = r["y1"]
        y2 = r["y2"]

        cv2.line(vis_img, (0, y1), (vis_img.shape[1], y1), (255, 0, 0), 1)
        cv2.line(vis_img, (0, y2), (vis_img.shape[1], y2), (255, 0, 0), 1)

    # Draw column lines
    for col_x in columns:
        x = int(col_x)

        cv2.line(
            vis_img,
            (x, 0),
            (x, vis_img.shape[0]),
            (0, 255, 0),
            2
        )

    output_path = os.path.join(OUTPUT_DIR, "step7_rows_columns.png")

    cv2.imwrite(output_path, vis_img)

    print("Visualization saved at:", output_path)

    print("Pipeline test completed successfully up to Step-7.")


if __name__ == "__main__":
    test_step7()
