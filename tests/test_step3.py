import os
import cv2

from preprocessing.image_cleaner import load_image
from layout_detection.layout_model import detect_layout
from table_extraction.extractor import extract_clean_table


def test():
    INPUT_IMAGE = "test_images/Invoice.jpg"
    OUTPUT_DIR = "test_outputs/step3"

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Loading image...")
    image = load_image(INPUT_IMAGE)

    print("Detecting layout...")
    layout = detect_layout(image)

    if not layout.has_table:
        print("No table detected")
        return

    print(f"Found {len(layout.tables)} table(s)")

    for idx, table in enumerate(layout.tables):
        bbox = table["bbox"]
        table_img = extract_clean_table(image, bbox)

        output_path = os.path.join(OUTPUT_DIR, f"table_{idx}.png")
        cv2.imwrite(output_path, table_img)

        print(f"Saved cropped table: {output_path}")


if __name__ == "__main__":
    test()
