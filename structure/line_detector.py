import cv2
import numpy as np


def detect_table_lines(table_image):
    """
    Detect horizontal and vertical lines in a table image.

    Args:
        table_image: Cropped table image (BGR or grayscale)

    Returns:
        Dictionary with detected horizontal and vertical lines
    """

    # Convert to grayscale if needed
    if len(table_image.shape) == 3:
        gray = cv2.cvtColor(table_image, cv2.COLOR_BGR2GRAY)
    else:
        gray = table_image.copy()

    # Edge detection to highlight lines
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)

    # Detect lines using Hough Transform
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=150,
        minLineLength=40,
        maxLineGap=5
    )

    horizontal_lines = []
    vertical_lines = []

    if lines is None:
        return {
            "horizontal": [],
            "vertical": []
        }

    for line in lines:
        x1, y1, x2, y2 = line[0]

        # Horizontal line condition
        if abs(y1 - y2) < 5:
            horizontal_lines.append((x1, y1, x2, y2))

        # Vertical line condition
        elif abs(x1 - x2) < 5:
            vertical_lines.append((x1, y1, x2, y2))

    return {
        "horizontal": horizontal_lines,
        "vertical": vertical_lines
    }




def classify_table_type(horizontal_lines, vertical_lines):
    """
    Classify table type based on detected lines.

    This helps decide how later reconstruction behaves.

    Parameters:
        horizontal_lines : list
        vertical_lines   : list

    Returns:
        str:
            "grid"        -> both horizontal and vertical lines exist
            "row_lines"   -> mostly horizontal lines
            "no_lines"    -> borderless table
    """

    h_count = len(horizontal_lines)
    v_count = len(vertical_lines)

    # Grid-based tables
    if h_count > 5 and v_count > 2:
        return "grid"

    # Only horizontal separators
    elif h_count > 5:
        return "row_lines"

    # No structural lines detected
    else:
        return "no_lines"
