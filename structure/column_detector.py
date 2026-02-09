import numpy as np
from sklearn.cluster import DBSCAN

class ColumnDetector:
    """
    Detect table columns using OCR alignment.

    This class uses clustering on X-axis positions of OCR bounding boxes to infer column structure.

    Generic approach:
    - Works with or without visible table lines
    - Invoice-agnostic
    """

    def __init__(self, eps=40, min_samples=5):
        """
        eps:
            clustering sensitivity (pixels)
            smaller = more columns
            larger = fewer columns

        min_samples:
            minimum words to form a column cluster
        """
        self.eps = eps
        self.min_samples = min_samples

    def detect_columns(self, words):
        """
        Detect column positions.

        Parameters:
            words (list):
                OCR output list:
                [
                    {
                        "text": str,
                        "x1": int,
                        "y1": int,
                        "x2": int,
                        "y2": int
                    }
                ]

        Returns:
            columns (list):
                list of column center X positions
        """

        if not words:
            return []

        # --------------------------------------
        # Step 1: Extract center X positions
        # --------------------------------------

        x_centers = []

        for w in words:
            center_x = (w["x1"] + w["x2"]) / 2
            x_centers.append([center_x])

        x_centers = np.array(x_centers)

        # --------------------------------------
        # Step 2: Cluster X positions
        # --------------------------------------

        clustering = DBSCAN(
            eps=self.eps,
            min_samples=self.min_samples
        ).fit(x_centers)

        labels = clustering.labels_

        # Ignore noise (-1 label)
        unique_labels = set(labels)
        unique_labels.discard(-1)

        columns = []

        for label in unique_labels:
            cluster_points = x_centers[labels == label]

            # Mean center of cluster
            col_x = float(np.mean(cluster_points))
            columns.append(col_x)

        # Sort left to right
        columns.sort()

        return columns
