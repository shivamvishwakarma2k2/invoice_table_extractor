import os

from preprocessing.image_cleaner import load_image, preprocess_for_ocr
from layout_detection.layout_model import detect_layout
from table_extraction.extractor import extract_clean_table
from table_extraction.table_selector import select_main_table
from ocr.ocr_engine import run_ocr
from structure.line_detector import detect_table_lines
from structure.row_detector import detect_rows
from structure.column_detector import ColumnDetector
from structure.logical_row_builder import LogicalRowBuilder
from structure.table_builder import TableBuilder
from export.excel_exporter import ExcelExporter
from metrics.confidence_analyzer import ConfidenceAnalyzer


def test():

    INPUT_IMAGE = "test_images/invoice1.jpg"
    # INPUT_IMAGE = "test_images/img5.jpg"
    OUTPUT_FILE = "test_outputs/invoice_output.xlsx"

    os.makedirs("test_outputs", exist_ok=True)

    print("STEP-1: Load image")
    image = load_image(INPUT_IMAGE)

    print("STEP-2: Detect layout")
    layout = detect_layout(image)

    if not layout.has_table:
        print("No table detected")
        return

    print("STEP-3: Select main table")
    main_table = select_main_table(layout)
    table_img = extract_clean_table(image, main_table["bbox"])

    print("STEP-4: OCR")
    ocr_ready = preprocess_for_ocr(table_img)
    words = run_ocr(ocr_ready)

    print("STEP-5: Row detection")
    row_segments = detect_rows(words)

    print("STEP-6: Column detection")
    column_detector = ColumnDetector(eps=45, min_samples=4)
    columns = column_detector.detect_columns(words)

    # Assign column index to words (with safe column-0 rule)
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

    for w in words:
        center_x = (w["x1"] + w["x2"]) / 2
        distances = [abs(center_x - c) for c in columns]

        if not distances:
            continue

        col_idx = distances.index(min(distances))

        text = w.get("text", "")

        if col_idx == 0:

            # Do NOT shift if it looks like identifier
            if not looks_like_identifier(text):

                # Also do NOT shift header words
                if text.lower() not in ["no.", "no", "item", "sr", "sr."]:
                    if len(columns) > 1:
                        col_idx = 1

        w["col"] = col_idx



    print("STEP-7: Logical row reconstruction")
    row_builder = LogicalRowBuilder()
    logical_rows = row_builder.build_logical_rows(
        words,
        row_segments,
        columns
    )

    print("STEP-8: Table matrix construction")
    table_builder = TableBuilder()
    table = table_builder.build_table(
        logical_rows=logical_rows,
        column_count=len(columns)
    )

    print("\nStructured Table Output:\n")

    for row in table:
        print(row)

    print("STEP-9: Export to Excel")
    exporter = ExcelExporter()
    exporter.export(table, OUTPUT_FILE)

    print("Pipeline completed successfully up to STEP-10")

    # STEP-11: Confidence Analysis

    print("STEP-11: Confidence Analysis")

    analyzer = ConfidenceAnalyzer()

    metrics = analyzer.analyze(
        words=words,
        logical_rows=logical_rows,
        table_matrix=table,
        columns=columns
    )

    print("\nExtraction Metrics Summary\n")

    print("OCR Metrics:", metrics["ocr_metrics"])
    print("Structure Metrics:", metrics["structure_metrics"])
    print("Completeness Metrics:", metrics["completeness_metrics"])
    print("Numeric Metrics:", metrics["numeric_metrics"])
    print("Overall Score:", metrics["overall_score"])
    print("Status:", metrics["status"])

if __name__ == "__main__":
    test()