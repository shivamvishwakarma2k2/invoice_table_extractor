class ColumnDetector:

    def __init__(self, eps=40, min_samples=5):
        # kept for compatibility
        self.eps = eps
        self.min_samples = min_samples


    def detect_columns(self, words):
        """
        Stable column detection using histogram (not clustering)
        """

        if not words:
            return []

        # Collect x centers
        xs = [(w["x1"] + w["x2"]) / 2 for w in words]

        xs = sorted(xs)

        # Split into equal zones
        num_cols = 6  #  can tune (5–8)

        min_x = min(xs)
        max_x = max(xs)

        step = (max_x - min_x) / num_cols

        columns = []

        for i in range(num_cols):
            columns.append(min_x + i * step)

        return columns
