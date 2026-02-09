# File: test_step8_pipeline.py

import os
import cv2

# STEP-1 + STEP-4 preprocessing
from preprocessing.image_cleaner import load_image, preprocess_for_ocr

# STEP-2 layout detection
from layout_detection.layout_model import detect_layout

# STEP-3 table crop
from table_extraction.extractor import extract_clean_table

# STEP-4 OCR
from ocr.ocr_engine import run_ocr

# STEP-5 line detection (optional)
from structure.line_detector import detect_table_lines

# STEP-6 candidate row detection
from structure.row_detector import detect_rows

# STEP-7 column detection
from structure.column_detector import ColumnDetector

# STEP-8 logical row reconstruction
from structure.logical_row_builder import LogicalRowBuilder


def test_step8():

    INPUT_IMAGE = "test_images/invoice5.jpg"
    OUTPUT_DIR = "test_outputs/step8_full_pipeline"

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # --------------------------------------------------
    # STEP-1 Load image
    # --------------------------------------------------

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
    # STEP-3 Table Crop
    # --------------------------------------------------

    print("STEP-3: Crop main table")

    table_bbox = layout.tables[0]["bbox"]

    table_img = extract_clean_table(image, table_bbox)

    cv2.imwrite(os.path.join(OUTPUT_DIR, "step3_table_crop.png"), table_img)

    # --------------------------------------------------
    # STEP-4 OCR
    # --------------------------------------------------

    print("STEP-4: OCR preprocessing")

    ocr_ready = preprocess_for_ocr(table_img)

    print("STEP-4: Run OCR")

    words = run_ocr(ocr_ready)

    print("OCR words detected:", len(words))

    # --------------------------------------------------
    # STEP-5 Line Detection (Optional helper)
    # --------------------------------------------------

    print("STEP-5: Detect table lines")

    horizontal_lines, vertical_lines = detect_table_lines(table_img)

    print("Horizontal lines:", len(horizontal_lines))
    print("Vertical lines:", len(vertical_lines))

    # --------------------------------------------------
    # STEP-6 Candidate Row Detection
    # --------------------------------------------------

    print("STEP-6: Detect candidate rows")

    rows = detect_rows(words)

    print("Candidate rows detected:", len(rows))

    # --------------------------------------------------
    # STEP-7 Column Detection
    # --------------------------------------------------

    print("STEP-7: Detect columns")

    column_detector = ColumnDetector(
        eps=45,         # clustering sensitivity
        min_samples=4   # minimum words to form column
    )

    columns = column_detector.detect_columns(words)

    print("Columns detected:", len(columns))
    print(columns)

    # --------------------------------------------------
    # STEP-8 Logical Row Reconstruction
    # --------------------------------------------------

    print("STEP-8: Logical row reconstruction")

    builder = LogicalRowBuilder(
        numeric_column_threshold=2
    )

    logical_rows = builder.build_logical_rows(
        rows,
        words,
        columns
    )

    print("Logical rows detected:", len(logical_rows))

    # --------------------------------------------------
    # Visualization
    # --------------------------------------------------

    vis_img = table_img.copy()

    # Draw candidate rows (blue)
    for r in rows:
        y1 = r["y1"]
        y2 = r["y2"]

        cv2.line(vis_img, (0, y1), (vis_img.shape[1], y1), (255, 0, 0), 1)
        cv2.line(vis_img, (0, y2), (vis_img.shape[1], y2), (255, 0, 0), 1)

    # Draw columns (green)
    for col_x in columns:
        x = int(col_x)

        cv2.line(
            vis_img,
            (x, 0),
            (x, vis_img.shape[0]),
            (0, 255, 0),
            2
        )

    # Draw logical rows (red boxes)
    for row in logical_rows:

        top = row["segments"][0]["y1"]
        bottom = row["segments"][-1]["y2"]

        cv2.rectangle(
            vis_img,
            (0, top),
            (vis_img.shape[1], bottom),
            (0, 0, 255),
            2
        )

    output_path = os.path.join(OUTPUT_DIR, "step8_logical_rows.png")

    cv2.imwrite(output_path, vis_img)

    print("Visualization saved at:", output_path)

    print("Pipeline completed successfully up to STEP-8.")


if __name__ == "__main__":
    test_step8()
