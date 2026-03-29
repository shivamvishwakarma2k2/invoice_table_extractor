from paddleocr import PPStructure
# from paddleocr.ppstructure.recovery.recovery_to_doc import sorted_layout_boxes


class TableStructureExtractor:

    def __init__(self):
        self.engine = PPStructure(
            show_log=False,
            use_gpu=False
        )

    def extract_tables(self, image):

        result = self.engine(image)

        tables = []

        for res in result:

            if res["type"] == "table":

                table_html = res.get("res", {}).get("html", "")

                if table_html:
                    tables.append(table_html)

        return tables

