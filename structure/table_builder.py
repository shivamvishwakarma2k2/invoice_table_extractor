class TableBuilder:
    """
    Build structured table matrix from logical rows.
    Compatible with logical_rows = List[List[word_dict]]
    """

    def __init__(self):
        pass

    # --------------------------------------------------
    # Build table matrix
    # --------------------------------------------------
    def build_table(self, logical_rows, column_count):
        """
        Convert logical rows into table matrix.

        Parameters:
            logical_rows: List[List[word_dict]]
            column_count: total number of detected columns

        Returns:
            table: list of lists (2D matrix)
        """

        table = []

        for row in logical_rows:

            # Create empty row cells
            row_cells = [""] * column_count

            for w in row:

                if not isinstance(w, dict):
                    continue

                col_idx = w.get("col")

                if col_idx is None:
                    continue

                text = w.get("text", "")

                if col_idx >= column_count:
                    continue

                # Append text to proper column
                if row_cells[col_idx] == "":
                    row_cells[col_idx] = text
                else:
                    row_cells[col_idx] += " " + text

            table.append(row_cells)

        return table