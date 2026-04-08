import os
import streamlit as st # type: ignore
import numpy as np
import tempfile
import cv2
from pdf2image import convert_from_bytes
from app_entry import run_application
from utlis.logger import AppLogger

logger = AppLogger()

# Initialize logs
if "logs" not in st.session_state:
    st.session_state["logs"] = []

APP_TITLE = "DocuStruct"
st.set_page_config(page_title=APP_TITLE, layout="wide")

st.markdown("""
<style>
.block-container {
    padding-top: 1rem;
}

/* Premium Button */
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
</style>
""", unsafe_allow_html=True)

# SIDEBAR
developer_mode = st.sidebar.toggle("Enable Developer Logs")

# HEADER
st.title(APP_TITLE)
st.caption("Structured Table Extraction System for Business Documents")

# TABS
tab1, tab2, tab3, tab4 = st.tabs(["Upload Document", "Metrics", "Results", "Developer Logs"])

# TAB 1 - UPLOAD
with tab1:

    uploaded_file = st.file_uploader(
        "Upload document (Image or PDF - single page)",
        type=["png", "jpg", "jpeg", "pdf"]
    )

    if uploaded_file:

        # Read file only ONCE
        uploaded_bytes = uploaded_file.read()

        if uploaded_file.type == "application/pdf":
            # pdf_pages = convert_from_bytes(uploaded_bytes)
            # preview_image = cv2.cvtColor(np.array(pdf_pages[0]), cv2.COLOR_RGB2BGR)

            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded_bytes)
                temp_path = tmp.name

            pdf_pages = convert_from_bytes(open(temp_path, "rb").read())
            preview_image = cv2.cvtColor(np.array(pdf_pages[0]), cv2.COLOR_RGB2BGR)


        else:
            file_bytes = np.asarray(bytearray(uploaded_bytes), dtype=np.uint8)
            preview_image = cv2.imdecode(file_bytes, 1)

        st.session_state["preview_image"] = preview_image

        col1, col2 = st.columns([1, 4])

        with col1:
            run_btn = st.button("Run Extraction", width="stretch")

        msg = st.empty()

        if run_btn:
            with st.spinner("Processing document..."):
                result = run_application(preview_image)

            st.session_state["results"] = result

            if "error" in result:
                msg.error(result["error"])
            else:
                msg.success("Extraction completed successfully")

        st.divider()

        st.image(preview_image, width=650, caption="Document Preview",)

# TAB 2 - METRICS
with tab2:

    if "results" not in st.session_state:
        st.stop()

    results = st.session_state["results"]

    if "error" in results:
        st.error(results["error"])
        st.stop()

    metrics = results.get("metrics", {})

    st.subheader("Extraction Overview")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Tables Detected", metrics.get("table_count", 0))
    c2.metric("Average Score", f"{metrics.get('average_score',0)*100:.2f}%")
    c3.metric("Status", metrics.get("status", "N/A"))
    c4.metric("Processing Time", f"{metrics.get('processing_time_sec',0)} sec")

    all_tables = results.get("all_tables_metrics", [])

    if not all_tables:
        st.info("No table-level metrics available.")
        st.stop()

    with st.expander("**Table-wise Analysis**"):

        table_tabs = st.tabs([f"Table {i+1}" for i in range(len(all_tables))])

        for i, tab in enumerate(table_tabs):

            with tab:

                table_metrics = all_tables[i].get("metrics", {})

                score = table_metrics.get("overall_score", 0)

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("Confidence Score", f"{round(score*100,2)}%")

                with col2:
                    if score > 0.9:
                        st.success("High Reliability")
                    elif score > 0.75:
                        st.warning("Medium Reliability")
                    else:
                        st.error("Low Reliability")


                with st.expander("**Detailed Metrics**", expanded=False):

                    st.markdown("**OCR Metrics**")
                    st.json(table_metrics.get("ocr_metrics", {}))

                    st.markdown("**Structure Metrics**")
                    st.json(table_metrics.get("structure_metrics", {}))

                    st.markdown("**Completeness Metrics**")
                    st.json(table_metrics.get("completeness_metrics", {}))

                    st.markdown("**Numeric Metrics**")
                    st.json(table_metrics.get("numeric_metrics", {}))

# TAB 3 - RESULTS
with tab3:
    
    if "results" not in st.session_state:
        st.stop()

    results = st.session_state["results"]

    if "error" in results:
        st.error(results["error"])
        st.stop()

    all_tables = results.get("all_tables_metrics", [])

    if not all_tables:
        st.warning("No structured tables available.")
        st.stop()

    st.subheader("Extracted Tables")

    # CREATE TABS FOR EACH TABLE
    table_tabs = st.tabs([f"Table {i+1}" for i in range(len(all_tables))])

    edited_tables = []

    for i, tab in enumerate(table_tabs):

        with tab:

            table_data = all_tables[i].get("table", [])

            if not table_data:
                st.warning("Empty table")
                edited_tables.append([])
                continue

            # Convert to DataFrame
            import pandas as pd
            df = pd.DataFrame(table_data)

            st.caption("Editable Table")

            edited_df = st.data_editor(
                df,
                num_rows="dynamic",
                width='stretch',
                key=f"table_editor_{i}"
            )

            edited_tables.append(edited_df.values.tolist())

            # Show confidence
            metrics = all_tables[i].get("metrics", {})
            score = metrics.get("overall_score", 0)

            if score < 0.8:
                st.warning("Low confidence detected. Please review and correct the table.")

 
    # Prepare file once
    from export.excel_exporter import ExcelExporter
    import tempfile
    import os

    exporter = ExcelExporter()

    temp_dir = tempfile.gettempdir()
    edited_excel_path = os.path.join(temp_dir, "output.xlsx")

    exporter.export_multiple(edited_tables, edited_excel_path)

    # SINGLE CLICK DOWNLOAD
    with open(edited_excel_path, "rb") as f:
        st.download_button(
            label="Download Excel",
            data=f,
            file_name="DocuStruct_Result.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# TAB 4 - DEVELOPER LOGS 
with tab4:

    if not developer_mode:
        st.info("Enable 'Developer Logs' from the sidebar.")
        st.stop()

    if "results" not in st.session_state:
        st.info("No execution logs available. Run extraction first.")
        st.stop()

    st.subheader("Execution Logs")

    logs = logger.get_logs()

    if logs:
        st.text_area("Logs", "\n".join(logs), height=500)
    else:
        st.info("No logs recorded for this session.")

    if st.button("Clear Logs"):
        logger.clear()
        st.success("Logs cleared")