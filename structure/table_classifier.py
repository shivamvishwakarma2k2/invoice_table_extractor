def classify_table_type(line_info, min_lines=2):
    """
    Classify table as GRID or TEXT based on detected lines.

    Args:
        line_info: Output from detect_table_lines()
        min_lines: Minimum lines required to consider table as grid

    Returns:
        String: "grid" or "text"
    """

    horizontal_count = len(line_info["horizontal"])
    vertical_count = len(line_info["vertical"])

    # If sufficient horizontal and vertical lines exist,
    # classify as grid-based table
    if horizontal_count >= min_lines and vertical_count >= min_lines:
        return "grid"

    # Otherwise, treat as text-aligned table
    return "text"
