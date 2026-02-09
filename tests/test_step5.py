import os
import cv2

# Step-1: Image loading
from preprocessing.image_cleaner import load_image, preprocess_for_ocr

# Step-2: Layout detection
from layout_detection.layout_model import detect_layout

# Step-3: Table cropping
from table_extraction.extractor import extract_clean_table

# Step-4: OCR
from ocr.ocr_engine import run_ocr

# Step-5: Line detection + classification
from structure.line_detector import detect_table_lines
from structure.table_classifier import classify_table_type


def test_pipeline_step5():
    """
    Full pipeline test:
    Step-1  → Image load
    Step-2  → Layout detection
    Step-3  → Table cropping
    Step-4  → OCR
    Step-5  → Line detection + table type classification
    """

    INPUT_IMAGE = "test_images/invoice1.jpg"
    OUTPUT_DIR = "test_outputs/full_pipeline_step5"

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\nSTEP-1: Load image")
    image = load_image(INPUT_IMAGE)

    print("STEP-2: Detect layout (tables, sections, text)")
    layout = detect_layout(image)

    if not layout.has_table:
        print("No table detected. Pipeline stopped.")
        return

    print(f"Tables detected: {len(layout.tables)}")

    # Select main table (first one for now)
    print("STEP-3: Crop main table")
    table_bbox = layout.tables[0]["bbox"]
    table_img = extract_clean_table(image, table_bbox)

    # Save cropped table for verification
    cv2.imwrite(os.path.join(OUTPUT_DIR, "step3_table_crop.png"), table_img)

    print("STEP-4: OCR preprocessing")
    ocr_ready = preprocess_for_ocr(table_img)

    # Save OCR-preprocessed image
    cv2.imwrite(os.path.join(OUTPUT_DIR, "step4_ocr_input.png"), ocr_ready)

    print("STEP-4: Run OCR")
    words = run_ocr(ocr_ready)

    print(f"OCR words detected: {len(words)}")

    # Visualize OCR output
    ocr_vis = table_img.copy()
    for w in words:
        # Draw bounding boxes
        cv2.rectangle(
            ocr_vis,
            (w["x1"], w["y1"]),
            (w["x2"], w["y2"]),
            (0, 255, 0),
            1
        )

    cv2.imwrite(os.path.join(OUTPUT_DIR, "step4_ocr_boxes.png"), ocr_vis)

    print("STEP-5: Detect table lines")
    line_info = detect_table_lines(table_img)

    print("STEP-5: Classify table type")
    table_type = classify_table_type(line_info)

    print(f"Table type detected: {table_type}")
    print(f"Horizontal lines: {len(line_info['horizontal'])}")
    print(f"Vertical lines: {len(line_info['vertical'])}")

    # Visualize line detection
    line_vis = table_img.copy()

    # Draw horizontal lines
    for x1, y1, x2, y2 in line_info["horizontal"]:
        cv2.line(line_vis, (x1, y1), (x2, y2), (255, 0, 0), 1)

    # Draw vertical lines
    for x1, y1, x2, y2 in line_info["vertical"]:
        cv2.line(line_vis, (x1, y1), (x2, y2), (0, 255, 0), 1)

    cv2.imwrite(os.path.join(OUTPUT_DIR, "step5_detected_lines.png"), line_vis)

    print("\nPipeline test completed successfully up to Step-5.")
    print(f"Outputs saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    test_pipeline_step5()
