# import torch
# import streamlit as st # type: ignore
# from ultralytics import YOLO
# import ultralytics.nn.tasks

# torch.serialization.add_safe_globals(
#     [ultralytics.nn.tasks.DetectionModel]
# )

# @st.cache_resource
# def load_layout_model():
#     return YOLO(MODEL_PATH)


# MODEL_PATH = "models\yolov8x-doclaynet-epoch64-imgsz640-initiallr1e-4-finallr1e-5.pt"
# model = load_layout_model()

# class LayoutResult:
#     def __init__(self, tables):
#         self.tables = tables  # list of bounding boxes

#     @property
#     def has_table(self):
#         return len(self.tables) > 0


# def detect_layout(image):
#     """
#     Detect tables using YOLO layout model.
#     Returns LayoutResult
#     """
#     results = model(image)[0]

#     table_boxes = []

#     for box in results.boxes:
#         cls_id = int(box.cls[0])
#         label = results.names[cls_id]
#         conf = float(box.conf[0])

#         if label.lower() == "table" and conf > 0.4:
#             x1, y1, x2, y2 = box.xyxy[0]
#             table_boxes.append({
#                 "bbox": (int(x1), int(y1), int(x2), int(y2)),
#                 "confidence": conf
#             })

#     return LayoutResult(table_boxes)







import torch
import streamlit as st  # type: ignore
from ultralytics import YOLO
import ultralytics.nn.tasks

from huggingface_hub import hf_hub_download

# ---------------------------------------------------
# SAFE LOAD FIX (YOLO)
# ---------------------------------------------------
# torch.serialization.add_safe_globals(
#     [ultralytics.nn.tasks.DetectionModel]
# )

# ---------------------------------------------------
# CONFIG
# ---------------------------------------------------

# 👉 HF Model Config (USED IN DEPLOYMENT)
HF_REPO_ID = "shivam2k2/docustruct-yolo"
HF_MODEL_FILENAME = "yolov8x-doclaynet-epoch64-imgsz640-initiallr1e-4-finallr1e-5.pt"

# 👉 LOCAL MODEL PATH (USED FOR LOCAL DEVELOPMENT)
LOCAL_MODEL_PATH = "models/yolov8x-doclaynet-epoch64-imgsz640-initiallr1e-4-finallr1e-5.pt"


# ---------------------------------------------------
# MODEL LOADING LOGIC
# ---------------------------------------------------
@st.cache_resource
def load_layout_model():

    print("Loading layout detection model...")

    # ==========================================================
    # OPTION 1: LOAD FROM HUGGING FACE (DEFAULT - DEPLOYMENT)
    # ==========================================================
    try:
        model_path = hf_hub_download(
            repo_id=HF_REPO_ID,
            filename=HF_MODEL_FILENAME
        )
        print(f"Model loaded from HF: {model_path}")

    except Exception as e:
        print(f"HF download failed: {e}")
        raise RuntimeError("Failed to download YOLO model from Hugging Face")

    # ==========================================================
    # OPTION 2: LOAD LOCAL MODEL (FOR LOCAL USE ONLY)
    # ==========================================================
    
    # import os

    # if os.path.exists(LOCAL_MODEL_PATH):
    #     model_path = LOCAL_MODEL_PATH
    #     print(f"Model loaded locally: {model_path}")
    # else:
    #     raise FileNotFoundError("Local model file not found")
    

    # Load YOLO model
    model = YOLO(model_path)

    return model


# Initialize model
model = load_layout_model()


# ---------------------------------------------------
# RESULT CLASS
# ---------------------------------------------------
class LayoutResult:

    def __init__(self, tables):
        self.tables = tables

    @property
    def has_table(self):
        return len(self.tables) > 0


# ---------------------------------------------------
# MAIN DETECTION FUNCTION
# ---------------------------------------------------
def detect_layout(image):
    """
    Detect tables using YOLO layout model
    """

    results = model(image)[0]

    table_boxes = []

    try:
        for box in results.boxes:

            cls_id = int(box.cls[0])
            label = results.names.get(cls_id, "")
            conf = float(box.conf[0])

            if label.lower() == "table" and conf > 0.4:

                x1, y1, x2, y2 = box.xyxy[0]

                table_boxes.append({
                    "bbox": (int(x1), int(y1), int(x2), int(y2)),
                    "confidence": round(conf, 4)
                })

    except Exception as e:
        print(f"Detection error: {e}")

    return LayoutResult(table_boxes)
