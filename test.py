import os
import re

from preprocessing.image_cleaner import load_image, preprocess_for_ocr
from layout_detection.layout_model import detect_layout
from table_extraction.extractor import extract_clean_table
from ocr.ocr_engine import run_ocr
from structure.row_detector import detect_rows
from structure.column_detector import ColumnDetector
from structure.logical_row_builder import LogicalRowBuilder
from structure.table_builder import TableBuilder
from export.excel_exporter import ExcelExporter
from metrics.confidence_analyzer import ConfidenceAnalyzer


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


def test():

    INPUT_IMAGE = "test_images/invoice-2t.jpg"
    OUTPUT_FILE = "test_outputs/invoice_output.xlsx"

    os.makedirs("test_outputs", exist_ok=True)

    print("STEP-1: Load image")
    image = load_image(INPUT_IMAGE)

    print("STEP-2: Detect layout")
    layout = detect_layout(image)

    if not layout.has_table:
        print("No table detected")
        return

    detected_tables = layout.tables
    print(f"Tables detected: {len(detected_tables)}")

    all_table_matrices = []

    analyzer = ConfidenceAnalyzer()

    for idx, table in enumerate(detected_tables):

        print(f"\n==============================")
        print(f"Processing Table {idx+1}")
        print(f"==============================")

        table_img = extract_clean_table(image, table["bbox"])

        # STEP-3 OCR
        print("STEP-3: OCR")

        ocr_ready = preprocess_for_ocr(table_img)
        words = run_ocr(ocr_ready)

        print(f"OCR words detected: {len(words)}")

        # STEP-4 Row detection
        print("STEP-4: Row detection")

        row_segments = detect_rows(words)

        print(f"Row segments: {len(row_segments)}")

        # STEP-5 Column detection
        print("STEP-5: Column detection")

        column_detector = ColumnDetector(eps=45, min_samples=4)
        columns = column_detector.detect_columns(words)

        print(f"Columns detected: {len(columns)}")

        # Assign column index to words
        for w in words:

            center_x = (w["x1"] + w["x2"]) / 2
            distances = [abs(center_x - c) for c in columns]

            if not distances:
                continue

            col_idx = distances.index(min(distances))

            text = w.get("text", "")

            if col_idx == 0:

                if not looks_like_identifier(text):

                    if text.lower() not in ["no.", "no", "item", "sr", "sr."]:
                        if len(columns) > 1:
                            col_idx = 1

            w["col"] = col_idx

        # STEP-6 Logical row reconstruction
        print("STEP-6: Logical row reconstruction")

        row_builder = LogicalRowBuilder()

        logical_rows = row_builder.build_logical_rows(
            words,
            row_segments,
            columns
        )

        print(f"Logical rows: {len(logical_rows)}")

        # STEP-7 Table matrix
        print("STEP-7: Table matrix construction")

        table_builder = TableBuilder()

        table_matrix = table_builder.build_table(
            logical_rows=logical_rows,
            column_count=len(columns)
        )

        print("\nStructured Table Output:\n")

        for row in table_matrix:
            print(row)

        all_table_matrices.append(table_matrix)

        # STEP-8 Metrics
        print("\nSTEP-8: Confidence Analysis")

        metrics = analyzer.analyze(
            words=words,
            logical_rows=logical_rows,
            table_matrix=table_matrix,
            columns=columns
        )

        print("\nExtraction Metrics Summary\n")

        print("OCR Metrics:", metrics["ocr_metrics"])
        print("Structure Metrics:", metrics["structure_metrics"])
        print("Completeness Metrics:", metrics["completeness_metrics"])
        print("Numeric Metrics:", metrics["numeric_metrics"])
        print("Overall Score:", metrics["overall_score"])
        print("Status:", metrics["status"])


    # STEP-9 Export all tables
    print("\nSTEP-9: Export all tables to Excel")

    exporter = ExcelExporter()

    exporter.export_multiple_tables(
        all_table_matrices,
        OUTPUT_FILE
    )

    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    test()
