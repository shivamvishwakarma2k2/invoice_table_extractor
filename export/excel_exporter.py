# export/excel_exporter.py

from openpyxl import Workbook


class ExcelExporter:
    """
    Export structured table data to Excel (.xlsx)
    """

    def __init__(self):
        pass

    # ---------------------------------------------------------
    # Export table to Excel
    # ---------------------------------------------------------
    def export(self, table, output_path):
        """
        Parameters:
            table: list of lists (2D structured table)
            output_path: output Excel file path
        """

        # Create workbook and sheet
        wb = Workbook()
        ws = wb.active
        ws.title = "Invoice Table"

        # Write rows
        for row_index, row in enumerate(table, start=1):
            for col_index, cell_value in enumerate(row, start=1):
                ws.cell(row=row_index, column=col_index, value=cell_value)

        # Save file
        wb.save(output_path)

        print(f"Excel file saved at: {output_path}")