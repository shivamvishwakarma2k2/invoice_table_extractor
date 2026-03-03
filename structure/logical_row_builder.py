# import numpy as np

# class LogicalRowBuilder:

#     def assign_columns(self, words, columns):
#         """
#         Assign each OCR word to nearest column center.
#         """

#         # Safety check
#         if not columns:
#             print("WARNING: No columns detected — skipping logical reconstruction")
#             return []

#         column_centers = []

#         for col in columns:
#             # assume column is vertical line x-position
#             column_centers.append(col)

#         for w in words:

#             # calculate word center
#             cx = (w["x1"] + w["x2"]) / 2

#             distances = [abs(cx - c) for c in column_centers]

#             # safety: avoid empty list crash
#             if not distances:
#                 continue

#             col_idx = int(np.argmin(distances))
#             w["column"] = col_idx

#         return words

#     def build_logical_rows(self, words, rows, columns):
#         """
#         Combine words into structured logical rows.
#         """

#         # Safety guard
#         if not columns:
#             print("WARNING: No columns detected — skipping logical reconstruction")
#             return []

#         words = self.assign_columns(words, columns)

#         logical_rows = []

#         for row in rows:

#             row_words = []

#             for w in words:
#                 cy = (w["y1"] + w["y2"]) / 2

#                 # check if word belongs inside row bounds
#                 if row["y1"] <= cy <= row["y2"]:
#                     row_words.append(w)

#             # sort by column index
#             row_words.sort(key=lambda x: x.get("column", 0))

#             logical_rows.append(row_words)

#         return logical_rows






#  -------------------------------
# structure/logical_row_builder.py

import re


class LogicalRowBuilder:
    """
    Fully Generic Structural Logical Row Builder.

    Compatible with row_segments format:
    {
        "y1": int,
        "y2": int,
        "words": [ ... ],
        "row_id": int
    }

    Uses structural identifier detection only.
    No column-name dependency.
    """

    def __init__(self):
        pass

    # ---------------------------------------------------------
    # STEP-8 MAIN FUNCTION
    # ---------------------------------------------------------
    def build_logical_rows(self, words, row_segments, columns):
        """
        Build logical rows from physical row segments
        and merge continuation rows structurally.
        """

        # Step-1: Extract physical rows directly
        physical_rows = []

        for seg in row_segments:

            row_words = seg.get("words", [])

            # Sort words left-to-right
            row_words = sorted(row_words, key=lambda x: x["x1"])

            physical_rows.append(row_words)

        # Step-2: Apply structural merge
        logical_rows = self.merge_structural_rows(physical_rows)

        return logical_rows

    # ---------------------------------------------------------
    # STRUCTURAL MERGE
    # ---------------------------------------------------------
    def merge_structural_rows(self, rows):

        if not rows:
            return rows

        merged = []
        current_row = rows[0]

        for next_row in rows[1:]:

            if self.starts_new_record(next_row):
                merged.append(current_row)
                current_row = next_row
            else:
                current_row = self.merge_rows(current_row, next_row)

        merged.append(current_row)

        return merged

    # ---------------------------------------------------------
    # NEW RECORD DETECTION (GENERIC)
    # ---------------------------------------------------------
    def starts_new_record(self, row):

        if not row:
            return False

        # Find leftmost word in row
        leftmost_word = min(row, key=lambda w: w["x1"])
        text = leftmost_word.get("text", "").strip()

        return self.looks_like_identifier(text)

    # ---------------------------------------------------------
    # IDENTIFIER PATTERN CHECK
    # ---------------------------------------------------------
    def looks_like_identifier(self, text):

        if not text:
            return False

        patterns = [
            r"^\d+$",               # 1
            r"^\d+\.$",             # 1.
            r"^[A-Za-z]\d+$",       # A123
            r"^[A-Za-z]-\d+$",      # A-12
            r"^\d+[A-Za-z]+$",      # 123A
            # r"^[A-Za-z0-9\-]{1,10}$"  # generic short SKU/code
        ]

        for pattern in patterns:
            if re.match(pattern, text):
                return True

        return False

    # ---------------------------------------------------------
    # MERGE TWO ROWS
    # ---------------------------------------------------------
    def merge_rows(self, row1, row2):

        merged = row1.copy()

        for w in row2:
            merged.append(w)

        return merged