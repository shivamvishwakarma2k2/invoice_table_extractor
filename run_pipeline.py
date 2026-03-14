import os
import tempfile
import time
import re

from preprocessing.image_cleaner import preprocess_for_ocr
from layout_detection.layout_model import detect_layout
from table_extraction.extractor import extract_clean_table
from table_extraction.table_selector import select_main_table
from ocr.ocr_engine import run_ocr
from structure.row_detector import detect_rows
from structure.column_detector import ColumnDetector
from structure.logical_row_builder import LogicalRowBuilder
from structure.table_builder import TableBuilder
from export.excel_exporter import ExcelExporter
from metrics.confidence_analyzer import ConfidenceAnalyzer


def looks_like_identifier(text):
    """
    Check if text looks like row identifier (No., 1., 12 etc)
    """
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


# ==========================================================
# MAIN PIPELINE
# ==========================================================

# def run_full_pipeline(image):

#     try:
#         start_time = time.time()

#         # ------------------------------------------------------
#         # STEP-1: Detect Layout
#         # ------------------------------------------------------
#         print("STEP-1: Detect layout")
#         layout = detect_layout(image)

#         if not layout.has_table:
#             raise Exception("No table detected")

#         # ------------------------------------------------------
#         # STEP-2: Select Main Table
#         # ------------------------------------------------------
#         print("STEP-2: Select main table")
#         main_table = select_main_table(layout)
#         table_img = extract_clean_table(image, main_table["bbox"])

#         # ------------------------------------------------------
#         # STEP-3: OCR
#         # ------------------------------------------------------
#         print("STEP-3: OCR")
#         ocr_ready = preprocess_for_ocr(table_img)
#         words = run_ocr(ocr_ready)

#         print(f"OCR words detected: {len(words)}")

#         # ------------------------------------------------------
#         # STEP-4: Row Detection (IMPORTANT FIX)
#         # ------------------------------------------------------
#         print("STEP-4: Row detection")
#         row_segments = detect_rows(words)

#         print(f"Row segments: {len(row_segments)}")

#         # ------------------------------------------------------
#         # STEP-5: Column Detection
#         # ------------------------------------------------------
#         print("STEP-5: Column detection")

#         column_detector = ColumnDetector(eps=45, min_samples=4)
#         columns = column_detector.detect_columns(words)

#         print(f"Columns detected: {len(columns)}")

#         # Assign columns safely (column-0 fix)
#         for w in words:

#             center_x = (w["x1"] + w["x2"]) / 2
#             distances = [abs(center_x - c) for c in columns]

#             if not distances:
#                 continue

#             col_idx = distances.index(min(distances))
#             text = w.get("text", "")

#             if col_idx == 0:
#                 if not looks_like_identifier(text):
#                     if text.lower() not in ["no.", "no", "item", "sr", "sr."]:
#                         if len(columns) > 1:
#                             col_idx = 1

#             w["col"] = col_idx

#         # ------------------------------------------------------
#         # STEP-6: Logical Row Reconstruction
#         # ------------------------------------------------------
#         print("STEP-6: Logical row reconstruction")

#         row_builder = LogicalRowBuilder()
#         logical_rows = row_builder.build_logical_rows(
#             words,
#             row_segments,
#             columns
#         )

#         print(f"Logical rows: {len(logical_rows)}")

#         # ------------------------------------------------------
#         # STEP-7: Table Matrix Construction
#         # ------------------------------------------------------
#         print("STEP-7: Table matrix construction")

#         table_builder = TableBuilder()
#         table = table_builder.build_table(
#             logical_rows=logical_rows,
#             column_count=len(columns)
#         )

#         # ------------------------------------------------------
#         # STEP-8: Export to Excel
#         # ------------------------------------------------------
#         print("STEP-8: Export to Excel")

#         temp_dir = tempfile.gettempdir()
#         excel_path = os.path.join(temp_dir, "structurai_output.xlsx")

#         exporter = ExcelExporter()
#         exporter.export(table, excel_path)

#         # ------------------------------------------------------
#         # STEP-9: Confidence Analysis
#         # ------------------------------------------------------
#         print("STEP-9: Confidence Analysis")

#         analyzer = ConfidenceAnalyzer()

#         metrics = analyzer.analyze(
#             words=words,
#             logical_rows=logical_rows,
#             table_matrix=table,
#             columns=columns
#         )

#         # Add processing time
#         metrics["processing_time_sec"] = round(time.time() - start_time, 2)

#         print("Pipeline completed successfully.")

#         return {
#             "table": table,
#             "metrics": metrics,
#             "excel_path": excel_path,
#             "logical_rows": logical_rows,
#             "columns": columns
#         }
    
#     except Exception as e:

#         print(f"Pipeline failed: {str(e)}")

#         return {
#             "error": "Unexpected error occurred.",
#             "error_type": "system error",
#             "details": str(e)
#         }
















def run_full_pipeline(image):

    try:

        start_time = time.time()

        # ------------------------------------------------------
        # STEP-1: Detect Layout
        # ------------------------------------------------------
        print("STEP-1: Detect layout")

        layout = detect_layout(image)

        if not layout or not layout.has_table:
            return {
                "error": "No table detected in the uploaded document.",
                "error_type": "no_table"
            }

        # ------------------------------------------------------
        # STEP-2: Select Main Table
        # ------------------------------------------------------
        print("STEP-2: Select main table")

        main_table = select_main_table(layout)

        if not main_table or "bbox" not in main_table:
            return {
                "error": "Unable to determine main table region.",
                "error_type": "table_selection_failure"
            }

        table_img = extract_clean_table(image, main_table["bbox"])

        if table_img is None or table_img.size == 0:
            return {
                "error": "Table extraction failed.",
                "error_type": "table_extraction_failure"
            }

        # ------------------------------------------------------
        # STEP-3: OCR
        # ------------------------------------------------------
        print("STEP-3: OCR")

        ocr_ready = preprocess_for_ocr(table_img)
        words = run_ocr(ocr_ready)

        if not words:
            return {
                "error": "OCR could not detect readable text.",
                "error_type": "ocr_failure"
            }

        print(f"OCR words detected: {len(words)}")

        # ------------------------------------------------------
        # STEP-4: Row Detection
        # ------------------------------------------------------
        print("STEP-4: Row detection")

        row_segments = detect_rows(words)

        if not row_segments:
            return {
                "error": "Row detection failed. Table structure unclear.",
                "error_type": "row_detection_failure"
            }

        print(f"Row segments: {len(row_segments)}")

        # ------------------------------------------------------
        # STEP-5: Column Detection
        # ------------------------------------------------------
        print("STEP-5: Column detection")

        column_detector = ColumnDetector(eps=45, min_samples=4)
        columns = column_detector.detect_columns(words)

        if not columns:
            return {
                "error": "Column detection failed.",
                "error_type": "column_detection_failure"
            }

        print(f"Columns detected: {len(columns)}")

        # ------------------------------------------------------
        # Assign Columns Safely
        # ------------------------------------------------------
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

        # ------------------------------------------------------
        # STEP-6: Logical Row Reconstruction
        # ------------------------------------------------------
        print("STEP-6: Logical row reconstruction")

        row_builder = LogicalRowBuilder()
        logical_rows = row_builder.build_logical_rows(
            words,
            row_segments,
            columns
        )

        if not logical_rows:
            return {
                "error": "Logical row reconstruction failed.",
                "error_type": "logical_row_failure"
            }

        print(f"Logical rows: {len(logical_rows)}")

        # ------------------------------------------------------
        # STEP-7: Table Matrix Construction
        # ------------------------------------------------------
        print("STEP-7: Table matrix construction")

        table_builder = TableBuilder()
        table = table_builder.build_table(
            logical_rows=logical_rows,
            column_count=len(columns)
        )

        if not table:
            return {
                "error": "Final table construction failed.",
                "error_type": "table_build_failure"
            }

        # ------------------------------------------------------
        # STEP-8: Export to Excel
        # ------------------------------------------------------
        print("STEP-8: Export to Excel")

        temp_dir = tempfile.gettempdir()
        excel_path = os.path.join(temp_dir, "structurai_output.xlsx")

        exporter = ExcelExporter()
        exporter.export(table, excel_path)

        # ------------------------------------------------------
        # STEP-9: Confidence Analysis
        # ------------------------------------------------------
        print("STEP-9: Confidence Analysis")

        analyzer = ConfidenceAnalyzer()

        metrics = analyzer.analyze(
            words=words,
            logical_rows=logical_rows,
            table_matrix=table,
            columns=columns
        )

        metrics["processing_time_sec"] = round(
            time.time() - start_time, 2
        )

        print("Pipeline completed successfully.")

        return {
            "table": table,
            "metrics": metrics,
            "excel_path": excel_path,
            "logical_rows": logical_rows,
            "columns": columns,
            "table_image": table_img
        }

    except Exception as e:

        print(f"Pipeline failed: {str(e)}")

        return {
            "error": "Unexpected system error occurred.",
            "error_type": "system_error",
            "details": str(e)
        }
