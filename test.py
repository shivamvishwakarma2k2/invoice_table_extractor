import os
import cv2
from preprocessing.image_cleaner import load_image, preprocess_for_ocr
from layout_detection.layout_model import detect_layout
from table_extraction.extractor import extract_clean_table
from table_extraction.table_selector import select_main_table
from ocr.ocr_engine import run_ocr
from structure.line_detector import detect_table_lines
from structure.row_detector import detect_rows
from structure.column_detector import ColumnDetector
from structure.logical_row_builder import LogicalRowBuilder


def test_step8():

    INPUT_IMAGE = "test_images/invoice.jpg"
    OUTPUT_DIR = "test_outputs/step8"

    os.makedirs(OUTPUT_DIR, exist_ok=True)


    print("STEP-1: Load image")
    image = load_image(INPUT_IMAGE)


    print("STEP-2: Detect layout")
    layout = detect_layout(image)

    if not layout.has_table:
        print("No table detected")
        return

    print("Tables detected:", len(layout.tables))


    print("STEP-3: Select main table")

    main_table = select_main_table(layout)

    if main_table is None:
        print("No valid table selected")
        return

    table_img = extract_clean_table(image, main_table["bbox"])

    cv2.imwrite(os.path.join(OUTPUT_DIR, "step3_table_crop.png"), table_img)


    print("STEP-4: OCR preprocessing")

    ocr_ready = preprocess_for_ocr(table_img)

    print("STEP-4: Run OCR")

    words = run_ocr(ocr_ready)

    print("OCR words detected:", len(words))


    print("STEP-5: Detect table lines")

    horizontal_lines, vertical_lines = detect_table_lines(table_img)

    print("Horizontal lines:", len(horizontal_lines))
    print("Vertical lines:", len(vertical_lines))


    print("STEP-6: Detect candidate rows")

    rows = detect_rows(words)

    print("Candidate rows detected:", len(rows))


    print("STEP-7: Detect columns")

    column_detector = ColumnDetector(
        eps=45,
        min_samples=4
    )

    columns = column_detector.detect_columns(words)

    print("Columns detected:", len(columns))
    print(columns)


    print("STEP-8: row reconstruction")

    builder = LogicalRowBuilder()

    logical_rows = builder.build_logical_rows(
        rows=rows,
        words=words,
        columns=columns
    )

    print("rows detected:", len(logical_rows))

    # Visualization (debug)

    vis_img = table_img.copy()

    # draw candidate rows (blue)
    for r in rows:
        cv2.line(vis_img, (0, r["y1"]), (vis_img.shape[1], r["y1"]), (255,0,0),1)
        cv2.line(vis_img, (0, r["y2"]), (vis_img.shape[1], r["y2"]), (255,0,0),1)

    # draw columns (green)
    for col_x in columns:
        x = int(col_x)
        cv2.line(vis_img, (x,0), (x,vis_img.shape[0]), (0,255,0),2)

    # draw logical rows (red boxes)

    for row in logical_rows:

        if not row:
            continue

        y_values = []

        for w in row:
            y_values.append(w["y1"])
            y_values.append(w["y2"])

        top = min(y_values)
        bottom = max(y_values)

        cv2.rectangle(
            vis_img,
            (0, top),
            (vis_img.shape[1], bottom),
            (0,0,255),
            2
        )


    output_path = os.path.join(OUTPUT_DIR, "step8_rows.png")

    cv2.imwrite(output_path, vis_img)

    print("Visualization saved:", output_path)


if __name__ == "__main__":
    test_step8()
