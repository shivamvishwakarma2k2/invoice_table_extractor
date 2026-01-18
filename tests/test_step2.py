
import os
import cv2

from preprocessing.image_cleaner import load_image
from layout_detection.layout_model import detect_layout


def test():
    INPUT_IMAGE = "test_images/Invoice.jpg"
    OUTPUT_DIR = "test_outputs/step2"

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Loading image...")
    image = load_image(INPUT_IMAGE)

    print("Detecting table layout...")
    layout = detect_layout(image)

    if not layout.has_table:
        print("No table detected")
        return

    for idx, table in enumerate(layout.tables):
        x1, y1, x2, y2 = table["bbox"]
        cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), 3)
        print(f"Table {idx} detected with confidence {table['confidence']:.2f}")

    output_path = os.path.join(OUTPUT_DIR, "layout_detected.png")
    cv2.imwrite(output_path, image)

    print(f"Step-2 test completed. Saved {output_path}")


if __name__ == "__main__":
    test()
