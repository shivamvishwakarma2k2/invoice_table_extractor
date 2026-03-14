import streamlit as st
import numpy as np
import cv2
from PIL import Image
from pdf2image import convert_from_bytes

from run_pipeline import run_full_pipeline


# PAGE CONFIG
APP_TITLE = "StructuRAI"

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
debug_mode = st.sidebar.toggle("Enable Debug Mode")

# HEADER
st.title(APP_TITLE)
st.caption("AI Powered Structured Invoice Table Extraction")


# TABS
tab1, tab2, tab3, tab4 = st.tabs(
    ["Upload", "Results", "Metrics", "Debug"]
)


# TAB 1 - UPLOAD - Old Ui

# with tab1:

#     uploaded_file = st.file_uploader(
#         "Upload Invoice (Image or PDF - Max 5 Pages)",
#         type=["jpg", "jpeg", "png", "pdf"]
#     )

#     preview_image = None

#     if uploaded_file:

#         # PDF handling
#         if uploaded_file.type == "application/pdf":

#             pdf_bytes = uploaded_file.read()
#             pages = convert_from_bytes(pdf_bytes)

#             if len(pages) > 5:
#                 st.error("Maximum 5 pages allowed.")
#                 st.stop()

#             preview_image = np.array(pages[0])

#         # Image handling
#         else:
#             image = Image.open(uploaded_file)
#             preview_image = np.array(image)

#         st.subheader("Preview")
#         # st.image(preview_image, width=550)

#         preview_display = cv2.resize(preview_image, None, fx=0.6, fy=0.6)
#         st.image(preview_display, width=350)

#         st.session_state["preview_image"] = preview_image


#         if st.button("Extract Table"):

#             progress = st.progress(0)
#             status_text = st.empty()

#             with st.spinner("Running StructuRAI extraction..."):

#                 progress.progress(20)
#                 status_text.text("Processing document...")

#                 results = run_full_pipeline(preview_image)

#                 progress.progress(100)
#                 status_text.text("Extraction completed.")

#             progress.empty()
#             status_text.empty()

#             # Error handling
#             if "error" in results:

#                 st.error(results["error"])

#             else:

#                 st.session_state["results"] = results
#                 st.session_state["table_image"] = results.get("table_image")
#                 st.success("Extraction completed successfully.")



# TAB 1 - UPLOAD DOCUMENT
with tab1:

    st.subheader("Upload Document")

    uploaded_file = st.file_uploader(
        "Upload Invoice Image or PDF",
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
                use_container_width=True
            )

        spinner_placeholder = col_spin.empty()
        message_placeholder = st.empty()

        # Run pipeline

        if extract_clicked:

            with spinner_placeholder:
                with st.spinner(""):

                    results = run_full_pipeline(preview_image)

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




# TAB 2 - RESULTS

with tab2:

    if "results" in st.session_state:

        results = st.session_state["results"]

        table = results["table"]
        excel_path = results["excel_path"]

        st.subheader("Extracted Structured Table")

        st.dataframe(table, use_container_width=True)

        with open(excel_path, "rb") as f:

            st.download_button(
                label="Download Excel",
                data=f,
                file_name="StructuRAI_Output.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    else:

        st.info("No results available. Please extract table first.")


# TAB 3 - METRICS

with tab3:

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


# TAB 4 - DEBUG

with tab4:


    if "results" not in st.session_state:
        st.caption("Debug overlay shown on extracted table region")
        st.info("Run extraction first to enable debug visualization.")
        st.stop()

    if not debug_mode:
        st.info("Enable Debug Mode from sidebar to view overlays.")
        st.stop()

    results = st.session_state["results"]

    # preview_image = st.session_state.get("preview_image", None)

    # if preview_image is None:
    #     st.warning("No processed image available.")
    #     st.stop()

    table_image = st.session_state.get("table_image", None)

    if table_image is None:
        st.warning("No processed image available.")
        st.stop()

    # Copy image for drawing
    # debug_img = preview_image.copy()
    debug_img = table_image.copy()


    columns = results.get("columns", [])
    logical_rows = results.get("logical_rows", [])

    # Draw Column Lines
    for col_x in columns:

        cv2.line(
            debug_img,
            (int(col_x), 0),
            (int(col_x), debug_img.shape[0]),
            (0, 255, 0),
            2
        )


    # Draw Row Boundaries
    for row in logical_rows:

        if not row:
            continue

        try:

            y1 = min(w["y1"] for w in row)
            y2 = max(w["y2"] for w in row)

            cv2.line(
                debug_img,
                (0, int(y1)),
                (debug_img.shape[1], int(y1)),
                (255, 0, 0),
                1
            )

            cv2.line(
                debug_img,
                (0, int(y2)),
                (debug_img.shape[1], int(y2)),
                (255, 0, 0),
                1
            )

        except Exception:
            continue

    # Draw OCR Bounding Boxes
    for row in logical_rows:

        for w in row:

            try:

                x1 = int(w["x1"])
                y1 = int(w["y1"])
                x2 = int(w["x2"])
                y2 = int(w["y2"])

                cv2.rectangle(
                    debug_img,
                    (x1, y1),
                    (x2, y2),
                    (0, 165, 255),
                    1
                )

            except Exception:
                continue

    # Legend
    st.subheader("Overlay Legend")

    st.table({
        "Visualization": [
            "Column Detection",
            "Row Detection",
            "OCR Word Bounding Boxes"
        ],
        "Color": [
            "🟢 Green",
            "🔵 Blue",
            "🟠 Orange"
        ]
    })
    # Display Image
    st.markdown("Image")
    st.image(debug_img, width=650)
