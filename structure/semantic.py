# structure/semantic.py

import re


def classify(text):
    """
    Classify word into semantic type

    Returns:
        "integer"
        "number"
        "percentage"
        "currency"
        "text"
        "mixed"
    """

    if not text:
        return "unknown"

    t = text.strip()

    # Remove common symbols for checking
    clean = t.replace(",", "").replace("₹", "").replace("$", "")

    # INTEGER (e.g., 1, 25)
    if re.fullmatch(r"\d+", clean):
        return "integer"

    # FLOAT / NUMBER (e.g., 10.50)
    if re.fullmatch(r"\d+\.\d+", clean):
        return "number"

    # PERCENTAGE (e.g., 10%)
    if "%" in t:
        return "percentage"

    # CURRENCY (₹100, $20.5)
    if "₹" in t or "$" in t:
        return "currency"

    # PURE TEXT (Description)
    if re.fullmatch(r"[A-Za-z ]+", t):
        return "text"

    # MIXED (fallback)
    return "mixed"
