def is_anchor(text):
    text = text.strip()

    return (
        text.isdigit() or
        text.endswith('.') or
        (len(text) <= 5 and any(c.isdigit() for c in text))
    )


def detect_rows(words):
    """
    Anchor-based row detection
    """

    # Sort top to bottom
    words = sorted(words, key=lambda w: w["y1"])

    rows = []
    current_row = []

    for w in words:

        text = w.get("text", "")

        if is_anchor(text):
            # Start new row
            if current_row:
                rows.append(current_row)

            current_row = [w]

        else:
            if not current_row:
                current_row = [w]
            else:
                current_row.append(w)

    if current_row:
        rows.append(current_row)

    return rows
