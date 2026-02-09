# import numpy as np


# def compute_word_center_y(word):
#     """
#     Compute vertical center of a word bounding box.
#     """
#     return (word["y1"] + word["y2"]) / 2


# def estimate_row_threshold(words):
#     """
#     Estimate row grouping threshold dynamically
#     based on average text height.
#     """

#     heights = [w["y2"] - w["y1"] for w in words]

#     if len(heights) == 0:
#         return 10

#     avg_height = np.mean(heights)

#     # Dynamic threshold
#     return avg_height * 0.8


# def cluster_words_into_rows(words):
#     """
#     Cluster OCR words into logical rows based on Y alignment.
#     """

#     if len(words) == 0:
#         return []

#     # Sort words by vertical position
#     words_sorted = sorted(words, key=lambda w: compute_word_center_y(w))

#     threshold = estimate_row_threshold(words)

#     rows = []
#     current_row = [words_sorted[0]]

#     for i in range(1, len(words_sorted)):

#         prev_y = compute_word_center_y(words_sorted[i - 1])
#         curr_y = compute_word_center_y(words_sorted[i])

#         if abs(curr_y - prev_y) <= threshold:
#             current_row.append(words_sorted[i])
#         else:
#             rows.append(current_row)
#             current_row = [words_sorted[i]]

#     rows.append(current_row)

#     return rows


# def convert_clusters_to_row_objects(row_clusters):
#     """
#     Convert clustered words into row structures.
#     """

#     rows = []

#     for idx, cluster in enumerate(row_clusters):

#         y1 = min(w["y1"] for w in cluster)
#         y2 = max(w["y2"] for w in cluster)

#         rows.append({
#             "row_id": idx,
#             "y1": int(y1),
#             "y2": int(y2),
#             "words": cluster
#         })

#     return rows


# def detect_rows(image, line_info, words):
#     """
#     Main row detection pipeline.

#     Uses OCR clustering as primary signal.
#     Lines used later for refinement.
#     """

#     row_clusters = cluster_words_into_rows(words)

#     rows = convert_clusters_to_row_objects(row_clusters)

#     return rows




# ----------------------------------------------------------------------------
# Chnage - 2 functions to use numeric anchors instead of all words for better row detection in tables with clear numeric columns.

# import numpy as np


# def is_numeric_word(text):
#     """
#     Detect numeric-like content.
#     """

#     text = text.replace(",", "").replace(".", "")

#     return text.isdigit() or "%" in text


# def find_anchor_words(words):
#     """
#     Find numeric words which likely belong to table columns.
#     """

#     anchors = []

#     for w in words:

#         if is_numeric_word(w["text"]):
#             anchors.append(w)

#     return anchors


# def cluster_anchors_into_rows(anchors, threshold=15):
#     """
#     Group numeric anchors into logical rows using Y alignment.
#     """

#     anchors_sorted = sorted(anchors, key=lambda w: (w["y1"] + w["y2"]) / 2)

#     rows = []

#     current_row = [anchors_sorted[0]]

#     for i in range(1, len(anchors_sorted)):

#         prev_y = (anchors_sorted[i - 1]["y1"] + anchors_sorted[i - 1]["y2"]) / 2
#         curr_y = (anchors_sorted[i]["y1"] + anchors_sorted[i]["y2"]) / 2

#         if abs(curr_y - prev_y) < threshold:
#             current_row.append(anchors_sorted[i])
#         else:
#             rows.append(current_row)
#             current_row = [anchors_sorted[i]]

#     rows.append(current_row)

#     return rows


# def assign_full_words_to_rows(anchor_rows, words):

#     rows = []

#     for idx, anchors in enumerate(anchor_rows):

#         y1 = min(a["y1"] for a in anchors) - 15
#         y2 = max(a["y2"] for a in anchors) + 25

#         row_words = []

#         for w in words:

#             center_y = (w["y1"] + w["y2"]) / 2

#             if y1 <= center_y <= y2:
#                 row_words.append(w)

#         rows.append({
#             "row_id": idx,
#             "y1": int(y1),
#             "y2": int(y2),
#             "words": row_words
#         })

#     return rows


# def detect_rows(image, line_info, words):

#     anchors = find_anchor_words(words)

#     anchor_rows = cluster_anchors_into_rows(anchors)

#     rows = assign_full_words_to_rows(anchor_rows, words)

#     return rows






# ----------------------------------------------------------------------------
# change 3 - Refactor to separate anchor detection, clustering, and word assignment for better modularity and potential future improvements.
# worked great

# import numpy as np


# def is_numeric_word(text):
#     """
#     Detect numeric-like content.
#     """
#     text_clean = text.replace(",", "").replace(".", "").replace("$", "").replace("%", "")
#     return text_clean.isdigit()


# def compute_center_y(word):
#     return (word["y1"] + word["y2"]) / 2


# def find_anchor_words(words):
#     """
#     Numeric words are anchor candidates.
#     """
#     anchors = []

#     for w in words:
#         if is_numeric_word(w["text"]):
#             anchors.append(w)

#     return anchors


# def cluster_anchor_rows(anchors, threshold=15):
#     """
#     Group numeric words into anchor rows.
#     """

#     anchors_sorted = sorted(anchors, key=lambda w: compute_center_y(w))

#     rows = []
#     current = [anchors_sorted[0]]

#     for i in range(1, len(anchors_sorted)):

#         prev_y = compute_center_y(anchors_sorted[i-1])
#         curr_y = compute_center_y(anchors_sorted[i])

#         if abs(curr_y - prev_y) < threshold:
#             current.append(anchors_sorted[i])
#         else:
#             rows.append(current)
#             current = [anchors_sorted[i]]

#     rows.append(current)

#     return rows


# def build_row_boundaries(anchor_rows, image_height):
#     """
#     Build row regions using midpoint boundaries.
#     """

#     centers = [np.mean([compute_center_y(a) for a in row]) for row in anchor_rows]

#     boundaries = []

#     for i in range(len(centers)):

#         if i == 0:
#             top = 0
#         else:
#             top = int((centers[i-1] + centers[i]) / 2)

#         if i == len(centers)-1:
#             bottom = image_height
#         else:
#             bottom = int((centers[i] + centers[i+1]) / 2)

#         boundaries.append((top, bottom))

#     return boundaries


# def assign_words_to_rows(boundaries, words):

#     rows = []

#     for idx, (y1, y2) in enumerate(boundaries):

#         row_words = []

#         for w in words:

#             center_y = compute_center_y(w)

#             if y1 <= center_y <= y2:
#                 row_words.append(w)

#         rows.append({
#             "row_id": idx,
#             "y1": int(y1),
#             "y2": int(y2),
#             "words": row_words
#         })

#     return rows


# def detect_rows(image, line_info, words):

#     anchors = find_anchor_words(words)

#     anchor_rows = cluster_anchor_rows(anchors)

#     boundaries = build_row_boundaries(anchor_rows, image.shape[0])

#     rows = assign_words_to_rows(boundaries, words)

#     return rows







#--------------------------------------------------------------------------------
# chnage 4 - Add back alignment-based row detection as a complementary method to anchor-based detection, and merge results for better robustness across different table styles.

import numpy as np


def compute_center_y(word):
    return (word["y1"] + word["y2"]) / 2


def is_numeric_word(text):

    text_clean = text.replace(",", "").replace(".", "").replace("$", "").replace("%", "")

    return text_clean.isdigit()


# ---------- Alignment-based row detection ----------

def detect_alignment_rows(words):

    words_sorted = sorted(words, key=lambda w: compute_center_y(w))

    heights = [w["y2"] - w["y1"] for w in words]
    avg_height = np.mean(heights)

    threshold = avg_height * 0.9

    rows = []
    current = [words_sorted[0]]

    for i in range(1, len(words_sorted)):

        prev_y = compute_center_y(words_sorted[i-1])
        curr_y = compute_center_y(words_sorted[i])

        if abs(curr_y - prev_y) < threshold:
            current.append(words_sorted[i])
        else:
            rows.append(current)
            current = [words_sorted[i]]

    rows.append(current)

    return rows


# ---------- Numeric anchor detection ----------

def detect_anchor_rows(words):

    anchors = [w for w in words if is_numeric_word(w["text"])]

    return detect_alignment_rows(anchors)


# ---------- Merge row candidates ----------

def merge_row_sets(alignment_rows, anchor_rows):

    merged = alignment_rows.copy()

    for anchor in anchor_rows:
        merged.append(anchor)

    # Remove duplicates using Y overlap
    final_rows = []

    for row in merged:

        y1 = min(w["y1"] for w in row)
        y2 = max(w["y2"] for w in row)

        overlap = False

        for fr in final_rows:

            if abs(fr["y1"] - y1) < 10:
                overlap = True
                break

        if not overlap:
            final_rows.append({
                "y1": y1,
                "y2": y2,
                "words": row
            })

    final_rows = sorted(final_rows, key=lambda r: r["y1"])

    for i, r in enumerate(final_rows):
        r["row_id"] = i

    return final_rows


# ---------- Main ----------

def detect_rows(words):

# def detect_rows(image, line_info, words):

    alignment_rows = detect_alignment_rows(words)

    anchor_rows = detect_anchor_rows(words)

    rows = merge_row_sets(alignment_rows, anchor_rows)

    return rows
