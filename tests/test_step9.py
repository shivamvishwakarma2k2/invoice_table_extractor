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
from table_structure.line_detector import detect_table_lines

# STEP-6 row detection
from table_structure.row_detector import detect_rows

# STEP-7 column detection (class-based)
from table_structure.column_detector import ColumnDetector

# STEP-8 logical row reconstruction
from structure.logical_row_builder import LogicalRowBuilder

# STEP-9 table builder
from structure.table_builder import TableBuilder


def test_step9():

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

    print("STEP-8: Logical row reconstruction")
    row_builder = LogicalRowBuilder()
    logical_rows = row_builder.build_logical_rows(
        words,
        rows,
        columns
    )

    print("Logical rows:", len(logical_rows))

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
    test_step9()