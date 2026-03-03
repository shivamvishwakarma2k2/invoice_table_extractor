# ==========================================================
# File: metrics/confidence_analyzer.py
# Purpose:
#   Compute extraction confidence and quality metrics
#   for invoice table extraction pipeline.
#
# Inputs:
#   - words (OCR output)
#   - logical_rows (after merge)
#   - table_matrix (final structured table)
#   - columns (detected column centers)
#
# Output:
#   Dictionary containing detailed metrics + overall score
# ==========================================================

import re
import numpy as np


class ConfidenceAnalyzer:

    def __init__(self):
        pass

    # ------------------------------------------------------
    # OCR METRICS
    # ------------------------------------------------------
    def compute_ocr_metrics(self, words):

        if not words:
            return {
                "avg_confidence": 0,
                "min_confidence": 0,
                "low_confidence_words": 0,
                "total_words": 0
            }

        confidences = [w.get("confidence", 0) for w in words]

        avg_conf = float(np.mean(confidences))
        min_conf = float(np.min(confidences))
        low_conf = len([c for c in confidences if c < 0.8])

        return {
            "avg_confidence": round(avg_conf, 4),
            "min_confidence": round(min_conf, 4),
            "low_confidence_words": low_conf,
            "total_words": len(words)
        }

    # ------------------------------------------------------
    # STRUCTURAL METRICS
    # ------------------------------------------------------
    def compute_structure_metrics(self, logical_rows, columns):

        return {
            "logical_row_count": len(logical_rows),
            "column_count": len(columns)
        }

    # ------------------------------------------------------
    # DATA COMPLETENESS METRICS
    # ------------------------------------------------------
    def compute_completeness_metrics(self, table_matrix):

        if not table_matrix:
            return {
                "empty_cell_ratio": 1.0,
                "total_cells": 0,
                "empty_cells": 0
            }

        total_cells = 0
        empty_cells = 0

        for row in table_matrix:
            for cell in row:
                total_cells += 1
                if str(cell).strip() == "":
                    empty_cells += 1

        empty_ratio = empty_cells / total_cells if total_cells > 0 else 1

        return {
            "total_cells": total_cells,
            "empty_cells": empty_cells,
            "empty_cell_ratio": round(empty_ratio, 4)
        }

    # ------------------------------------------------------
    # NUMERIC CONSISTENCY METRICS
    # ------------------------------------------------------
    def compute_numeric_consistency(self, table_matrix):

        numeric_pattern = re.compile(r"^[\d.,]+%?$")

        numeric_cells = 0
        total_cells = 0

        for row in table_matrix:
            for cell in row:
                total_cells += 1
                if numeric_pattern.match(str(cell).strip()):
                    numeric_cells += 1

        ratio = numeric_cells / total_cells if total_cells > 0 else 0

        return {
            "numeric_cell_ratio": round(ratio, 4),
            "numeric_cells": numeric_cells
        }

    # ------------------------------------------------------
    # OVERALL SCORE
    # ------------------------------------------------------
    def compute_overall_score(
        self,
        ocr_metrics,
        completeness_metrics,
        structure_metrics
    ):

        # Weighted scoring
        ocr_score = ocr_metrics["avg_confidence"]
        completeness_score = 1 - completeness_metrics["empty_cell_ratio"]

        structure_score = 1.0
        if structure_metrics["logical_row_count"] < 1:
            structure_score = 0

        overall = (
            0.5 * ocr_score +
            0.3 * completeness_score +
            0.2 * structure_score
        )

        return round(overall, 4)

    # ------------------------------------------------------
    # MAIN ANALYSIS FUNCTION
    # ------------------------------------------------------
    def analyze(self, words, logical_rows, table_matrix, columns):

        ocr_metrics = self.compute_ocr_metrics(words)
        structure_metrics = self.compute_structure_metrics(
            logical_rows, columns
        )
        completeness_metrics = self.compute_completeness_metrics(
            table_matrix
        )
        numeric_metrics = self.compute_numeric_consistency(
            table_matrix
        )

        overall_score = self.compute_overall_score(
            ocr_metrics,
            completeness_metrics,
            structure_metrics
        )

        # Classification
        if overall_score > 0.9:
            status = "High Reliability"
        elif overall_score > 0.75:
            status = "Medium Reliability"
        else:
            status = "Low Reliability"

        return {
            "ocr_metrics": ocr_metrics,
            "structure_metrics": structure_metrics,
            "completeness_metrics": completeness_metrics,
            "numeric_metrics": numeric_metrics,
            "overall_score": overall_score,
            "status": status
        }