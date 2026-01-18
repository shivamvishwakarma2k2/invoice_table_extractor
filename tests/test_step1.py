import os
import cv2

from preprocessing.image_cleaner import load_image, preprocess_image


def test():
    INPUT_IMAGE = "test_images/Invoice.jpg"
    OUTPUT_DIR = "test_outputs/step1"

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("Loading image...")
    image = load_image(INPUT_IMAGE)

    print("Preprocessing image...")
    processed = preprocess_image(image)

    cv2.imwrite(os.path.join(OUTPUT_DIR, "original.png"), image)
    cv2.imwrite(os.path.join(OUTPUT_DIR, "processed.png"), processed)

    print("Step-1 test completed. Check test_outputs/step1/")


if __name__ == "__main__":
    test()
