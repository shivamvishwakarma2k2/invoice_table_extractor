import os
import cv2

from preprocessing.image_cleaner import load_image, preprocess_for_ocr
from layout_detection.layout_model import detect_layout
from table_extraction.extractor import extract_clean_table
from ocr.ocr_engine import run_ocr


def test():
    INPUT_IMAGE = "test_images/invoice1.jpg"
    OUTPUT_DIR = "test_outputs/step4"

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("STEP 1: Load image")
    image = load_image(INPUT_IMAGE)

    print("STEP 2: Detect table layout")
    layout = detect_layout(image)
    if not layout.has_table:
        print("No table detected")
        return

    print("STEP 3: Crop main table")
    table_img = extract_clean_table(image, layout.tables[0]["bbox"])

    print("STEP 4: Preprocess for OCR")
    clean = preprocess_for_ocr(table_img)

    print("STEP 5: Run PaddleOCR")
    words = run_ocr(clean)

    print(f"OCR detected {len(words)} words")

    # Visualization
    vis_img = table_img.copy()

    for w in words:
        # Draw bounding box
        cv2.rectangle(
            vis_img,
            (w["x1"], w["y1"]),
            (w["x2"], w["y2"]),
            (0, 255, 0),
            1
        )

        # Draw text
        cv2.putText(
            vis_img,
            w["text"],
            (w["x1"], max(10, w["y1"] - 5)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.4,
            (0, 0, 255),
            1
        )

    output_path = os.path.join(OUTPUT_DIR, "ocr_words.png")
    cv2.imwrite(output_path, vis_img)

    print(f"OCR visualization saved at: {output_path}")


if __name__ == "__main__":
    test()
