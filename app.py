import streamlit as st # type: ignore
import numpy as np
import cv2
from pdf2image import convert_from_bytes
from app_entry import run_application

# PAGE CONFIG
APP_TITLE = "DocuStruct"

st.set_page_config(
    page_title=APP_TITLE,
    layout="wide"
)


st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
}
            
/* Extract Button Styling */
div.stButton > button {
    background: linear-gradient(90deg,#2563eb,#4f46e5);
    color: white;
    font-weight: 600;
    border-radius: 10px;
    border: none;
    padding: 10px 28px;
    font-size: 16px;
    transition: all 0.25s ease;
}

div.stButton > button:hover {
    background: linear-gradient(90deg,#1d4ed8,#4338ca);
    transform: translateY(-1px);
    box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
}

/* Spinner alignment */
.stSpinner {
    margin-top: 6px;
}

/* Cleaner preview container */
.preview-box {
    border-radius: 12px;
    padding: 10px;
    border: 1px solid #e5e7eb;
}

</style>
""", unsafe_allow_html=True)


# SIDEBAR
developer_mode = st.sidebar.toggle("Developer View")

# HEADER
st.title(APP_TITLE)
st.caption("Automated Table Extraction and Structural Reconstruction System for Invoices")


# TABS
tab1, tab2, tab3, tab4 = st.tabs(
    ["Upload", "Metrics", "Results", "Developer"]
)

# TAB 1 - UPLOAD DOCUMENT
with tab1:

    st.subheader("Upload Document")

    uploaded_file = st.file_uploader(
        "Upload Invoice Image or PDF(1 Page)",
        type=["png","jpg","jpeg","pdf"]
    )

    if uploaded_file:
        
        # Convert file → image
        if uploaded_file.type == "application/pdf":
            pdf_pages = convert_from_bytes(uploaded_file.read())
            preview_image = cv2.cvtColor(
                np.array(pdf_pages[0]),
                cv2.COLOR_RGB2BGR
            )

        else:
            file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
            preview_image = cv2.imdecode(file_bytes, 1)

        st.session_state["preview_image"] = preview_image

        # Action Bar

        col_btn, col_spin = st.columns([1,5])

        with col_btn:

            extract_clicked = st.button(
                "Extract Table",
                type="primary",
                width="stretch"
            )

        spinner_placeholder = col_spin.empty()
        message_placeholder = st.empty()

        # Run run_application from app_entry.py

        if extract_clicked:

            with spinner_placeholder:
                with st.spinner("Running DocuStruct..."):

                    results = run_application(preview_image)

            st.session_state["results"] = results
            st.session_state["table_image"] = results.get("table_image")

            if "error" in results:
                message_placeholder.error(results["error"])

            else:
                message_placeholder.success("Extraction completed successfully.")

        # Preview Image
        st.divider()

        preview_display = cv2.resize(
            preview_image,
            None,
            fx=0.55,
            fy=0.55
        )

        st.image(
            preview_display,
            width=650,
            caption="Document Preview"
        )



# TAB 2 - METRICS

with tab2:

    if "results" in st.session_state:

        metrics = st.session_state["results"]["metrics"]

        st.subheader("Extraction Summary")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "Overall Score",
                f"{round(metrics['overall_score'] * 100, 2)}%"
            )

        with col2:
            st.metric(
                "Processing Time",
                f"{metrics['processing_time_sec']} sec"
            )

        with col3:

            status = metrics["status"]

            if status == "High Reliability":
                st.success(status)

            elif status == "Medium Reliability":
                st.warning(status)

            else:
                st.error(status)


        with st.expander("Advanced Metrics"):

            st.subheader("OCR Metrics")
            st.json(metrics["ocr_metrics"])

            st.subheader("Structure Metrics")
            st.json(metrics["structure_metrics"])

            st.subheader("Completeness Metrics")
            st.json(metrics["completeness_metrics"])

            st.subheader("Numeric Metrics")
            st.json(metrics["numeric_metrics"])

    else:

        st.info("Run extraction to view metrics.")



# TAB 3 - RESULTS

with tab3:

    if "results" in st.session_state:

        results = st.session_state["results"]

        table = results["table"]
        excel_path = results["excel_path"]

        st.subheader("Extracted Structured Table")

        st.dataframe(table, width="stretch")

        with open(excel_path, "rb") as f:

            st.download_button(
                label="Download Excel",
                data=f,
                file_name="Output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    else:

        st.info("No results available. Please extract table first.")


# # TAB 4 - Developer - OLD UI without logs

# from utlis.logger import AppLogger
# logger = AppLogger()    

# with tab4:

#     if "results" not in st.session_state:
#         st.caption("Developer overlay shown on extracted table region")
#         st.info("Run extraction first to enable Developer visualization.")
#         st.stop()

#     if not developer_mode:
#         st.info("Enable Developer View from sidebar to view overlays.")
#         st.stop()

#     results = st.session_state["results"]

#     # preview_image = st.session_state.get("preview_image", None)

#     # if preview_image is None:
#     #     st.warning("No processed image available.")
#     #     st.stop()

#     table_image = st.session_state.get("table_image", None)

#     if table_image is None:
#         st.warning("No processed image available.")
#         st.stop()

#     # Copy image for drawing
#     # developer_img = preview_image.copy()
#     developer_img = table_image.copy()


#     columns = results.get("columns", [])
#     logical_rows = results.get("logical_rows", [])

#     # Draw Column Lines
#     for col_x in columns:

#         cv2.line(
#             developer_img,
#             (int(col_x), 0),
#             (int(col_x), developer_img.shape[0]),
#             (0, 255, 0),
#             2
#         )


#     # Draw Row Boundaries
#     for row in logical_rows:

#         if not row:
#             continue

#         try:

#             y1 = min(w["y1"] for w in row)
#             y2 = max(w["y2"] for w in row)

#             cv2.line(
#                 developer_img,
#                 (0, int(y1)),
#                 (developer_img.shape[1], int(y1)),
#                 (255, 0, 0),
#                 1
#             )

#             cv2.line(
#                 developer_img,
#                 (0, int(y2)),
#                 (developer_img.shape[1], int(y2)),
#                 (255, 0, 0),
#                 1
#             )

#         except Exception:
#             continue

#     # Draw OCR Bounding Boxes
#     for row in logical_rows:

#         for w in row:

#             try:

#                 x1 = int(w["x1"])
#                 y1 = int(w["y1"])
#                 x2 = int(w["x2"])
#                 y2 = int(w["y2"])

#                 cv2.rectangle(
#                     developer_img,
#                     (x1, y1),
#                     (x2, y2),
#                     (0, 165, 255),
#                     1
#                 )

#             except Exception:
#                 continue

#     # Legend
#     st.subheader("Overlay Legend")

#     st.table({
#         "Visualization": [
#             "Column Detection",
#             "Row Detection",
#             "OCR Word Bounding Boxes"
#         ],
#         "Color": [
#             "🟢 Green",
#             "🔵 Blue",
#             "🟠 Orange"
#         ]
#     })
#     # Display Image
#     st.markdown("Image")
#     st.image(developer_img, width=650)



# TAB 4 - Developer

from utlis.logger import AppLogger

logger = AppLogger()

with tab4:

    if "results" not in st.session_state:
        st.caption("Developer overlay shown on extracted table region")
        st.info("Run extraction first to enable Developer visualization.")
        st.stop()

    if not developer_mode:
        st.info("Enable Developer View from sidebar to view overlays.")
        st.stop()

    results = st.session_state["results"]

    table_image = st.session_state.get("table_image", None)

    if table_image is None:
        st.warning("No processed image available.")
        st.stop()

    # Copy image for drawing
    developer_img = table_image.copy()

    columns = results.get("columns", [])
    logical_rows = results.get("logical_rows", [])

    # Draw Column Lines (Green)
    for col_x in columns:
        cv2.line(
            developer_img,
            (int(col_x), 0),
            (int(col_x), developer_img.shape[0]),
            (0, 255, 0),
            2
        )

    # Draw Row Boundaries (Blue)
    for row in logical_rows:

        if not row:
            continue

        try:
            y1 = min(w["y1"] for w in row)
            y2 = max(w["y2"] for w in row)

            cv2.line(
                developer_img,
                (0, int(y1)),
                (developer_img.shape[1], int(y1)),
                (255, 0, 0),
                1
            )

            cv2.line(
                developer_img,
                (0, int(y2)),
                (developer_img.shape[1], int(y2)),
                (255, 0, 0),
                1
            )

        except Exception:
            continue

    # Draw OCR Bounding Boxes (Orange)
    for row in logical_rows:
        for w in row:
            try:
                x1 = int(w["x1"])
                y1 = int(w["y1"])
                x2 = int(w["x2"])
                y2 = int(w["y2"])

                cv2.rectangle(
                    developer_img,
                    (x1, y1),
                    (x2, y2),
                    (0, 165, 255),
                    1
                )

            except Exception:
                continue

    # Layout: Image + Logs
    col1, col2 = st.columns([2, 1])

    # LEFT → IMAGE
    with col1:

        st.subheader("Processed Image")

        st.image(developer_img, width=650)

        st.info("🟢 - Column 🟠 - Row 🔵 - OCR Words")

    # RIGHT → LOGS
    with col2:

        st.subheader("Execution Logs")

        logs = logger.get_logs()

        if logs:
            log_text = "\n".join(logs)

            st.text_area(
                label="Logs",
                value=log_text,
                height=400,
                # disabled=True,
            )
        else:
            st.info("No logs available.")

        # Clear logs button
        if st.button("Clear Logs"):
            logger.clear()
            st.success("Logs cleared")
