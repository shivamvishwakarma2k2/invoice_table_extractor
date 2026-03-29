class LogicalRowBuilder:
    """
    Improved Logical Row Builder

    Features:
    - Works without identifier column
    - Handles multi-line descriptions
    - Uses semantic + structural merging
    - Compatible with new row detector
    """

    def __init__(self):
        pass

    def build_logical_rows(self, words, row_segments, columns):
        """
        row_segments = list of rows (list of words)
        """

        if not row_segments:
            return []

        # Step-1: sort each row left → right
        physical_rows = []


        for row in row_segments:

            # Ensure row contains valid word dicts
            clean_row = []

            for w in row:
                if isinstance(w, dict) and "x1" in w:
                    clean_row.append(w)

            if not clean_row:
                continue

            sorted_row = sorted(clean_row, key=lambda w: w["x1"])
            physical_rows.append(sorted_row)




        # Step-2: merge intelligently
        logical_rows = self.merge_rows(physical_rows)

        return logical_rows

    # SMART MERGE LOGIC (CORE)
    def merge_rows(self, rows):

        merged = []

        for row in rows:

            if not merged:
                merged.append(row)
                continue

            prev_row = merged[-1]


            if self.is_continuation(prev_row, row):

                combined = prev_row + row

                combined = [w for w in combined if isinstance(w, dict)]

                merged[-1] = combined
            else:
                merged.append(row)


        return merged

    # CONTINUATION DETECTION 
    def is_continuation(self, prev_row, curr_row):

        if not curr_row:
            return False

        # Check if current row has numeric values
        has_number = any(
            isinstance(w, dict) and w.get("type") in ["number", "integer"]
            for w in curr_row
        )


        # Check vertical gap
        prev_bottom = max(w["y2"] for w in prev_row if isinstance(w, dict))
        curr_top = min(w["y1"] for w in curr_row if isinstance(w, dict))

        vertical_gap = abs(curr_top - prev_bottom)

        avg_height = sum((w["y2"] - w["y1"]) for w in prev_row) / len(prev_row)

        # RULES

        # Rule-1: No numbers → likely continuation
        if not has_number:
            return True

        # Rule-2: Very close vertically → continuation
        if vertical_gap < avg_height * 0.6:
            return True

        return False
