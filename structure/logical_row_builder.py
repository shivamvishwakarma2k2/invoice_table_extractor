
# import numpy as np

# class LogicalRowBuilder:
#     """
#     Convert candidate row segments into logical rows.

#     Handles:
#     - multiline descriptions
#     - borderless tables
#     - generic invoice layouts
#     """

#     def __init__(self, numeric_column_threshold=2):
#         """
#         numeric_column_threshold:

#         minimum number of numeric columns required
#         to consider a row as a NEW logical row.
#         """

#         self.numeric_column_threshold = numeric_column_threshold

#     # --------------------------------------------------
#     # Assign each word to closest column anchor
#     # --------------------------------------------------

#     def assign_columns(self, words, columns):

#         for w in words:
#             center_x = (w["x1"] + w["x2"]) / 2

#             # find nearest column anchor
#             distances = [abs(center_x - c) for c in columns]
#             col_idx = int(np.argmin(distances))

#             w["column_id"] = col_idx

#         return words

#     # --------------------------------------------------
#     # Check if row contains numeric content
#     # --------------------------------------------------

#     def is_numeric_text(self, text):

#         if text is None:
#             return False

#         # simple numeric detection
#         return any(char.isdigit() for char in text)

#     def count_numeric_columns(self, row_words):

#         numeric_cols = set()

#         for w in row_words:
#             if self.is_numeric_text(w["text"]):
#                 numeric_cols.add(w["column_id"])

#         return len(numeric_cols)

#     # --------------------------------------------------
#     # Main build function
#     # --------------------------------------------------

#     def build_logical_rows(self, row_segments, words, columns):

#         # assign columns first
#         words = self.assign_columns(words, columns)

#         logical_rows = []
#         current_row = None

#         # group words by row segment
#         for seg in row_segments:

#             seg_words = []

#             for w in words:
#                 center_y = (w["y1"] + w["y2"]) / 2

#                 if seg["y1"] <= center_y <= seg["y2"]:
#                     seg_words.append(w)

#             numeric_count = self.count_numeric_columns(seg_words)

#             # ----------------------------------
#             # New logical row condition
#             # ----------------------------------

#             if numeric_count >= self.numeric_column_threshold:

#                 # start new logical row
#                 if current_row:
#                     logical_rows.append(current_row)

#                 current_row = {
#                     "segments": [seg],
#                     "words": seg_words.copy()
#                 }

#             else:
#                 # continuation of previous row
#                 if current_row:
#                     current_row["segments"].append(seg)
#                     current_row["words"].extend(seg_words)
#                 else:
#                     # fallback if first row
#                     current_row = {
#                         "segments": [seg],
#                         "words": seg_words.copy()
#                     }

#         if current_row:
#             logical_rows.append(current_row)

#         return logical_rows







#-------------------------------------------------
# structure/logical_row_builder.py

import numpy as np


class LogicalRowBuilder:

    def assign_columns(self, words, columns):
        """
        Assign each OCR word to nearest column center.
        """

        # Safety check
        if not columns:
            print("WARNING: No columns detected — skipping logical reconstruction")
            return []

        column_centers = []

        for col in columns:
            # assume column is vertical line x-position
            column_centers.append(col)

        for w in words:

            # calculate word center
            cx = (w["x1"] + w["x2"]) / 2

            distances = [abs(cx - c) for c in column_centers]

            # safety: avoid empty list crash
            if not distances:
                continue

            col_idx = int(np.argmin(distances))
            w["column"] = col_idx

        return words

    def build_logical_rows(self, words, rows, columns):
        """
        Combine words into structured logical rows.
        """

        # Safety guard
        if not columns:
            print("WARNING: No columns detected — skipping logical reconstruction")
            return []

        words = self.assign_columns(words, columns)

        logical_rows = []

        for row in rows:

            row_words = []

            for w in words:
                cy = (w["y1"] + w["y2"]) / 2

                # check if word belongs inside row bounds
                if row["y1"] <= cy <= row["y2"]:
                    row_words.append(w)

            # sort by column index
            row_words.sort(key=lambda x: x.get("column", 0))

            logical_rows.append(row_words)

        return logical_rows
