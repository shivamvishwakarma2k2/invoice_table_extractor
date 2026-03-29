import os
import tempfile
import time

from layout_detection.layout_model import detect_layout
from table_extraction.extractor import extract_clean_table

from pipeline.hybrid_table_extractor import HybridTableExtractor
from postprocessing.table_cleaner import TableCleaner
from export.excel_exporter import ExcelExporter
from metrics.confidence_analyzer import ConfidenceAnalyzer

from utlis.logger import AppLogger

logger = AppLogger()


def run_application(image):

    try:
        start_time = time.time()
        logger.clear()

        logger.log("Execution started")

        # Layout Detection
        logger.log("Layout Detection")
        layout = detect_layout(image)

        if not layout or not layout.has_table:
            logger.log("No table detected in document")
            return {"error": "No table detected in the document."}

        tables = layout.tables
        logger.log(f"Tables detected: {len(tables)}")

        extractor = HybridTableExtractor()
        cleaner = TableCleaner()
        analyzer = ConfidenceAnalyzer()
        exporter = ExcelExporter()

        all_tables = []
        all_results = []
        scores = []

        # -----------------------------------
        for idx, tbl in enumerate(tables):

            logger.log(f"Processing table {idx + 1}")

            if "bbox" not in tbl:
                logger.log("Bounding box missing, skipping table")
                continue

            table_img = extract_clean_table(image, tbl["bbox"])

            if table_img is None or table_img.size == 0:
                logger.log("Table image extraction failed")
                continue

            # EXTRACTION
            logger.log("Table Extraction")

            result = extractor.extract(table_img)

            if not result:
                logger.log("Extraction failed for table")
                continue

            engine = result.get("engine")
            if not engine:
                engine = "custom"

            logger.log(f"Extraction engine used: {engine}")

            table = result.get("table", [])
            words = result.get("words", [])
            columns = result.get("columns", [])
            logical_rows = result.get("logical_rows", [])

            # LOG EXTRACTION DETAILS
            logger.log("OCR Processing")
            logger.log(f"OCR words detected: {len(words)}")

            logger.log("Row Detection")
            logger.log(f"Row segments detected: {len(logical_rows)}")

            logger.log("Column Detection")
            logger.log(f"Columns detected: {len(columns)}")

            if not table:
                logger.log("Empty table extracted")
                continue

            # CLEANING
            logger.log("Table Construction")

            table = cleaner.clean(table)

            max_cols = max(len(r) for r in table)

            for r in table:
                r.extend([""] * (max_cols - len(r)))

            logger.log(f"Table size: {len(table)} rows x {max_cols} columns")

            # METRICS
            logger.log("Confidence Analysis")

            metrics = analyzer.analyze(
                words=words,
                logical_rows=logical_rows if logical_rows else table,
                table_matrix=table,
                columns=columns if columns else list(range(max_cols))
            )



            if "pp_structure" in engine:

                completeness = 1 - metrics["completeness_metrics"]["empty_cell_ratio"]

                # STRUCTURE QUALITY
                row_count = metrics["structure_metrics"]["logical_row_count"]
                col_count = metrics["structure_metrics"]["column_count"]

                structure_score = 1.0

                if row_count < 2:
                    structure_score *= 0.5

                if col_count < 2:
                    structure_score *= 0.5

                # CONTENT CONSISTENCY
                numeric_ratio = metrics["numeric_metrics"]["numeric_cell_ratio"]

                # Ideal numeric ratio range (invoice tables)
                if numeric_ratio < 0.05:
                    consistency_score = 0.5
                elif numeric_ratio > 0.9:
                    consistency_score = 0.7
                else:
                    consistency_score = 1.0

                # FINAL SCORE (NO OCR) for PP structure-based tables
                final_score = (
                    0.45 * completeness +
                    0.265 * structure_score +
                    0.258 * consistency_score
                )

                metrics["overall_score"] = round(final_score, 4)

                # STATUS
                if final_score > 0.9:
                    metrics["status"] = "High Reliability"
                elif final_score > 0.75:
                    metrics["status"] = "Medium Reliability"
                else:
                    metrics["status"] = "Low Reliability"


            # LOG METRICS for Custom engine
            logger.log("OCR Metrics")
            logger.log(str(metrics["ocr_metrics"]))

            logger.log("Structure Metrics")
            logger.log(str(metrics["structure_metrics"]))

            logger.log("Completeness Metrics")
            logger.log(str(metrics["completeness_metrics"]))

            logger.log("Numeric Metrics")
            logger.log(str(metrics["numeric_metrics"]))

            logger.log(f"Overall Score: {metrics['overall_score']}")
            logger.log(f"Status: {metrics['status']}")

            scores.append(metrics["overall_score"])
            all_tables.append(table)

            all_results.append({
                "table": table,
                "metrics": metrics,
                "engine": engine 
            })

        # VALIDATION
        if not all_tables:
            logger.log("No valid structured tables generated")
            return {"error": "No structured tables could be extracted."}

        # AGGREGATION
        logger.log("Result Aggregation")

        avg_score = sum(scores) / len(scores)

        combined_metrics = {
            "table_count": len(all_tables),
            "average_score": round(avg_score, 4),
            "status": (
                "High Reliability" if avg_score > 0.9 else
                "Medium Reliability" if avg_score > 0.75 else
                "Low Reliability"
            ),
            "processing_time_sec": round(time.time() - start_time, 2)
        }

        logger.log(f"Total tables processed: {len(all_tables)}")
        logger.log(f"Average score: {combined_metrics['average_score']}")
        logger.log(f"Final status: {combined_metrics['status']}")

        # EXPORT
        logger.log("Excel Export")

        temp_dir = tempfile.gettempdir()
        excel_path = os.path.join(temp_dir, "output.xlsx")

        exporter.export_multiple(all_tables, excel_path)

        logger.log("Excel file generated successfully")
        logger.log("Execution completed")

        print("\n")

        return {
            "table": all_tables[0],
            "excel_path": excel_path,
            "metrics": combined_metrics,
            "all_tables_metrics": all_results
        }

    except Exception as e:

        logger.log(f"System error: {str(e)}")

        return {
            "error": "Unexpected system error occurred.",
            "details": str(e)
        }
