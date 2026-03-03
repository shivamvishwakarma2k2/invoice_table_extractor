# test_step9_pipeline.py

import os
import cv2

# STEP-1 + STEP-4 preprocessing
from preprocessing.image_cleaner import load_image, preprocess_for_ocr

# STEP-2 layout detection
from layout_detection.layout_model import detect_layout

# STEP-3 table extraction
from table_extraction.extractor import extract_clean_table
from table_extraction.table_selector import select_main_table

# STEP-4 OCR
from ocr.ocr_engine import run_ocr

# STEP-5 line detection
from structure.line_detector import detect_table_lines

# STEP-6 row detection
from structure.row_detector import detect_rows

# STEP-7 column detection (class-based)
from structure.column_detector import ColumnDetector

# STEP-8 logical row reconstruction
from structure.logical_row_builder import LogicalRowBuilder

# STEP-9 table builder
from structure.table_builder import TableBuilder


def test():

    INPUT_IMAGE = "test_images/invoice1.jpg"

    print("STEP-1: Load image")
    image = load_image(INPUT_IMAGE)

    print("STEP-2: Detect layout")
    layout = detect_layout(image)

    if not layout.has_table:
        print("No table detected")
        return

    print("STEP-3: Select main table")
    main_table = select_main_table(layout)

    if main_table is None:
        print("No valid table selected")
        return

    table_img = extract_clean_table(image, main_table["bbox"])

    print("STEP-4: OCR")
    ocr_ready = preprocess_for_ocr(table_img)
    words = run_ocr(ocr_ready)

    print("OCR words:", len(words))

    print("STEP-5: Line detection")
    detect_table_lines(table_img)

    print("STEP-6: Row detection")
    rows = detect_rows(words)
    print("Row segments:", len(rows))

    print("STEP-7: Column detection")
    column_detector = ColumnDetector(
        eps=45,
        min_samples=4
    )
    columns = column_detector.detect_columns(words)

    print("Columns detected:", len(columns))

    # # Assign column index to each word
    # for w in words:

    #     center_x = (w["x1"] + w["x2"]) / 2

    #     distances = [abs(center_x - c) for c in columns]

    #     if distances:
    #         col_idx = distances.index(min(distances))
    #         w["col"] = col_idx


    # ----------------------
    import re

    def looks_like_identifier(text):
        patterns = [
            r"^\d+$",
            r"^\d+\.$",
            r"^[A-Za-z]\d+$",
            r"^[A-Za-z]-\d+$",
            r"^\d+[A-Za-z]+$"
        ]

        for p in patterns:
            if re.match(p, text.strip()):
                return True
        return False


    # Assign column index to each word
    for w in words:

        center_x = (w["x1"] + w["x2"]) / 2
        distances = [abs(center_x - c) for c in columns]

        if not distances:
            continue

        col_idx = distances.index(min(distances))

        # ---- SAFE COLUMN-0 CORRECTION ----
        if col_idx == 0:
            text = w.get("text", "")

            if not looks_like_identifier(text):
                # Move to next column if possible
                if len(columns) > 1:
                    col_idx = 1

        w["col"] = col_idx


        # print("STEP-8: Logical row reconstruction")
        row_builder = LogicalRowBuilder()
        logical_rows = row_builder.build_logical_rows(
            words,
            rows,
            columns
        )

    print("Logical rows:", len(logical_rows))

    print("Sample word from first logical row:")
    print(logical_rows[0][0])

    print("STEP-9: Table matrix construction")
    table_builder = TableBuilder()
    table = table_builder.build_table(
        logical_rows=logical_rows,
        column_count=len(columns)
    )

    print("\nStructured Table Output:\n")

    for row in table:
        print(row)

    print("\nPipeline completed successfully up to STEP-9")


if __name__ == "__main__":
    test()