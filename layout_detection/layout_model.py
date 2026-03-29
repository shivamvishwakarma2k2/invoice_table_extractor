import torch
import streamlit as st # type: ignore
from ultralytics import YOLO
import ultralytics.nn.tasks

torch.serialization.add_safe_globals(
    [ultralytics.nn.tasks.DetectionModel]
)

@st.cache_resource
def load_layout_model():
    return YOLO(MODEL_PATH)


MODEL_PATH = "models\yolov8x-doclaynet-epoch64-imgsz640-initiallr1e-4-finallr1e-5.pt"
model = load_layout_model()

class LayoutResult:
    def __init__(self, tables):
        self.tables = tables  # list of bounding boxes

    @property
    def has_table(self):
        return len(self.tables) > 0


def detect_layout(image):
    """
    Detect tables using YOLO layout model.
    Returns LayoutResult
    """
    results = model(image)[0]

    table_boxes = []

    for box in results.boxes:
        cls_id = int(box.cls[0])
        label = results.names[cls_id]
        conf = float(box.conf[0])

        if label.lower() == "table" and conf > 0.4:
            x1, y1, x2, y2 = box.xyxy[0]
            table_boxes.append({
                "bbox": (int(x1), int(y1), int(x2), int(y2)),
                "confidence": conf
            })

    return LayoutResult(table_boxes)
