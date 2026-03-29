
from structure.table_structure_extractor import TableStructureExtractor
from structure.html_table_parser import html_to_table

from ocr.ocr_engine import run_ocr
from preprocessing.image_cleaner import preprocess_for_ocr


class HybridTableExtractor:

    def __init__(self):
        self.pp = TableStructureExtractor()

    def extract(self, table_img):

        # TRY PP-STRUCTURE
        tables_html = self.pp.extract_tables(table_img)

        if tables_html:
            try:
                table = html_to_table(tables_html[0])

                if table and len(table) > 1:
                    print("--> PP-Structure")

                    # Create dummy columns (needed for metrics)
                    num_cols = len(table[0]) if table else 0
                    columns = list(range(num_cols))

                    # Logical rows = table rows (for PP)
                    logical_rows = table

                    return {
                        "table": table,
                        "words": [],
                        "columns": columns,
                        "logical_rows": logical_rows,
                        "engine": "pp_structure" 
                    }
            except Exception:
                pass


        print("-> Fallback to Structured logic")

        # OCR
        ocr_ready = preprocess_for_ocr(table_img)
        words = run_ocr(ocr_ready)

        if not words:
            return []

        # NORMALIZE WORDS
        clean_words = []

        for w in words:

            text = str(w.get("text", "")).strip()

            if not text:
                continue

            w["text"] = text
            w["cx"] = (w["x1"] + w["x2"]) / 2
            w["cy"] = (w["y1"] + w["y2"]) / 2

            clean_words.append(w)

        words = clean_words

        if not words:
            return []

        # GROUP INTO ROWS (Y-BASED)
        words = sorted(words, key=lambda w: w["cy"])

        rows = []
        current_row = [words[0]]

        # dynamic threshold based on avg height
        heights = [(w["y2"] - w["y1"]) for w in words]
        avg_height = sum(heights) / len(heights)
        threshold = avg_height * 0.8

        for i in range(1, len(words)):

            prev = words[i - 1]
            curr = words[i]

            if abs(curr["cy"] - prev["cy"]) < threshold:
                current_row.append(curr)
            else:
                rows.append(current_row)
                current_row = [curr]

        rows.append(current_row)

        # COLUMN ZONE DETECTION (X-BINS)
        all_x = sorted([w["cx"] for w in words])

        num_cols = self.estimate_column_count(rows)

        min_x = min(all_x)
        max_x = max(all_x)

        step = (max_x - min_x) / max(num_cols, 1)

        columns = [min_x + i * step for i in range(num_cols)]

        # BUILD TABLE
        table = []

        for row in rows:

            # sort left → right
            row = sorted(row, key=lambda w: w["cx"])

            cells = [""] * num_cols

            for w in row:

                cx = w["cx"]

                distances = [abs(cx - c) for c in columns]

                if not distances:
                    continue

                col = distances.index(min(distances))

                if col >= num_cols:
                    continue

                text = w["text"]

                # merge text
                if cells[col]:
                    cells[col] += " " + text
                else:
                    cells[col] = text

            # ignore empty rows
            if any(c.strip() for c in cells):
                table.append(cells)

            return {
                "table": table,
                "words": words,
                "columns": columns,
                "logical_rows": rows,
                "engine": "custom"  
            }


    # ESTIMATE COLUMN COUNT BASED ON MEDIAN WORD COUNT PER ROW
    def estimate_column_count(self, rows):

        col_counts = []

        for row in rows:
            col_counts.append(len(row))

        if not col_counts:
            return 5

        # use median for stability
        col_counts.sort()
        mid = len(col_counts) // 2

        estimated = col_counts[mid]

        # clamp range
        return max(4, min(estimated, 10))
