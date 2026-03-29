import pandas as pd

class ExcelExporter:

    def export_multiple(self, tables, output_path):

        with pd.ExcelWriter(output_path, engine="openpyxl") as writer:

            for idx, table in enumerate(tables):
                df = pd.DataFrame(table)
                df.columns = [""] * len(df.columns)
                sheet_name = f"Table_{idx+1}"
                df.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    index=False,
                    header=False   
                )
                
        print("Excel saved at:", output_path)
