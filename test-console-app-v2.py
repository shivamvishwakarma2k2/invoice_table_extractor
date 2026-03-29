import os

from preprocessing.image_cleaner import load_image
from layout_detection.layout_model import detect_layout
from table_extraction.extractor import extract_clean_table

from pipeline.hybrid_table_extractor import HybridTableExtractor
from postprocessing.table_cleaner import TableCleaner
from export.excel_exporter import ExcelExporter
from metrics.confidence_analyzer import ConfidenceAnalyzer


def test():

    INPUT_IMAGE = "test_images/invoice1.jpg"
    OUTPUT_FILE = "test_outputs/invoice_output.xlsx"

    os.makedirs("test_outputs", exist_ok=True)

    # Load image
    print("Load image")

    image = load_image(INPUT_IMAGE)

    if image is None:
        print("Failed to load image")
        return

    # Detect layout
    print("Detect layout")

    layout = detect_layout(image)

    if not layout or not layout.has_table:
        print("No table detected")
        return

    tables = layout.tables

    if not tables:
        print("No tables found")
        return

    # INIT COMPONENTS
    extractor = HybridTableExtractor()
    cleaner = TableCleaner()
    exporter = ExcelExporter()
    analyzer = ConfidenceAnalyzer()

    all_tables = []
    all_scores = []

    print("Processing all detected tables")

    # LOOPING the TABLES
    for idx, tbl in enumerate(tables):

        print(f"Processing Table {idx + 1}")

        if "bbox" not in tbl:
            print("Invalid table bbox → skipped")
            continue

        table_img = extract_clean_table(image, tbl["bbox"])

        if table_img is None or table_img.size == 0:
            print("Table extraction failed")
            continue

        try:
            result = extractor.extract(table_img)
        except Exception as e:
            print("Extraction error:", str(e))
            continue

        if not result:
            print("Empty result")
            continue

        table = result.get("table", [])
        words = result.get("words", [])
        engine = result.get("engine", "unknown")

        print(f"Engine used: {engine}")

        if not table:
            print("No table extracted")
            continue

        # CLEAN TABLE
        print("Cleaning table...")

        table = cleaner.clean(table)

        # Normalize column size
        max_cols = max(len(row) for row in table)

        for i in range(len(table)):
            if len(table[i]) < max_cols:
                table[i].extend([""] * (max_cols - len(table[i])))

        # CONFIDENCE ANALYSIS
        try:
            metrics = analyzer.analyze(
                words=words,
                logical_rows=table,
                table_matrix=table,
                columns=list(range(len(table[0])))
            )

            score = metrics["overall_score"]

        except Exception as e:
            print("Metrics error:", str(e))
            score = 0
            metrics = {}

        print("\n--- Metrics ---")

        if metrics:
            print("OCR:", metrics["ocr_metrics"])
            print("Structure:", metrics["structure_metrics"])
            print("Completeness:", metrics["completeness_metrics"])
            print("Numeric:", metrics["numeric_metrics"])
            print("Score:", score)
            print("Status:", metrics["status"])
        else:
            print("Metrics unavailable")

        all_scores.append(score)
        all_tables.append(table)

    # FINAL CHECK
    if not all_tables:
        print("No valid tables extracted")
        return

    # PRINT OUTPUT
    print("FINAL OUTPUT")

    for i, table in enumerate(all_tables):

        print(f"\n--- Table {i + 1} ---\n")

        for row in table:
            print(row)

    #  CONFIDENCE
    if all_scores:

        avg_score = sum(all_scores) / len(all_scores)
        print("OVERALL CONFIDENCE")
        print("Average Score:", round(avg_score, 4))

        if avg_score > 0.9:
            print("Status: High Reliability")
        elif avg_score > 0.75:
            print("Status: Medium Reliability")
        else:
            print("Status: Low Reliability")

    # EXPORT EXCEL
    print("\nExporting Excel")

    try:
        exporter.export_multiple(all_tables, OUTPUT_FILE)
        print("Excel saved:", OUTPUT_FILE)
    except Exception as e:
        print("Excel export failed:", str(e))

    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    test()
