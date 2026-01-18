from table_extraction.table_cropper import crop_table, remove_white_margins
from table_extraction.orientation import deskew_image


def extract_clean_table(image, bbox):
    table = crop_table(image, bbox)
    table = deskew_image(table)
    table = remove_white_margins(table)
    return table
