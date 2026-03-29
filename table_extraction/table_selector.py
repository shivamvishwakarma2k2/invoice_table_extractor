
def select_main_table(layout):
    """
    Select main table from detected layout.

    Strategy: choose table with largest height
    """

    if not layout.tables:
        return None

    main_table = max(
        layout.tables,
        key=lambda t: (t["bbox"][3] - t["bbox"][1])
    )

    return main_table
