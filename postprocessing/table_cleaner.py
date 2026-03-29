import re


class TableCleaner:

    def clean(self, table):

        if not table:
            return table

        table = self.normalize(table)
        table = self.fix_headers(table)
        table = self.merge_description(table)
        table = self.clean_numeric(table)

        return table

    # NORMALIZE TABLE SHAPE
    def normalize(self, table):

        max_cols = max(len(row) for row in table)

        for i in range(len(table)):
            if len(table[i]) < max_cols:
                table[i].extend([""] * (max_cols - len(table[i])))

        return table

    # HEADER DETECTION
    def fix_headers(self, table):

        if len(table) < 2:
            return table

        header = table[0]

        merged_header = []

        for cell in header:
            text = cell.strip().lower()

            # merge broken headers
            if text in ["", "net", "gross", "worth"]:
                continue

            merged_header.append(cell)

        if merged_header:
            table[0] = merged_header + [""] * (len(header) - len(merged_header))

        return table

    # MERGE DESCRIPTION LINES
    def merge_description(self, table):

        cleaned = []

        for row in table:

            if not cleaned:
                cleaned.append(row)
                continue

            prev = cleaned[-1]

            # if first column empty → continuation
            if not row[0].strip():
                for i in range(len(row)):
                    if row[i].strip():
                        prev[i] += " " + row[i]
            else:
                cleaned.append(row)

        return cleaned

    # CLEAN NUMERIC COLUMNS
    def clean_numeric(self, table):

        for i in range(1, len(table)):

            for j in range(len(table[i])):

                text = table[i][j]

                if not text:
                    continue

                # clean repeated numeric strings
                text = re.sub(r"\s+", " ", text)

                table[i][j] = text.strip()

        return table
