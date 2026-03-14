# StructuRAI – Invoice Table Extraction System

## Overview

StructuRAI is a document processing system designed to extract structured tabular data from invoice images and PDF documents.

The system analyzes the layout of the document, identifies table regions, extracts textual content with positional information, reconstructs table rows and columns, and converts the extracted information into a structured dataset.

The extracted table can then be exported to Excel format for further processing or analysis.

The application also provides a graphical interface built with Streamlit, allowing users to upload invoices, run the extraction process, and review the extracted results interactively.

---

# Key Features

- Automatic detection of invoice tables
- Text extraction with bounding box coordinates
- Row detection for grid and borderless tables
- Column detection using coordinate clustering
- Logical row reconstruction for multi-line descriptions
- Structured table matrix generation
- Export extracted tables to Excel format
- Extraction reliability metrics
- Debug visualization for rows and columns
- Support for image and PDF documents
- Interactive web-based interface

---

# System Workflow

The system processes documents through multiple stages to convert an unstructured invoice into a structured dataset.

```
Document Input
      ↓
Layout Detection
      ↓
Table Region Extraction
      ↓
Text Recognition
      ↓
Row Detection
      ↓
Column Detection
      ↓
Logical Row Reconstruction
      ↓
Table Matrix Construction
      ↓
Excel Export
      ↓
Extraction Metrics
```

---

# Processing Steps

## 1. Layout Detection

The document layout is analyzed to identify structural components such as tables and text regions.

A layout detection model trained on the DocLayNet dataset is used to locate tables inside the document.

**Output**

- Bounding box coordinates of detected tables

---

## 2. Table Region Extraction

After detecting the table location, the corresponding region is cropped from the original image.  
This ensures that all subsequent steps focus only on the relevant table area.

---

## 3. Text Recognition

Text inside the extracted table region is detected and recognized using PaddleOCR.

Each detected word includes:

- Text content
- Bounding box coordinates
- Recognition confidence score

Example structure:

```
{
  "text": "Nintendo Console",
  "x1": 120,
  "y1": 150,
  "x2": 260,
  "y2": 180,
  "confidence": 0.96
}
```

---

## 4. Row Detection

Rows are identified by analyzing the vertical alignment of text elements.

The detection method considers:

- Alignment of text baselines
- Numeric anchors
- Spacing patterns

This allows row detection even when tables do not contain visible grid lines.

---

## 5. Column Detection

Columns are detected by clustering text positions based on their horizontal coordinates.

A clustering approach groups words that align vertically into the same column.

This approach works for:

- Grid-based tables
- Borderless tables
- Irregular layouts

---

## 6. Logical Row Reconstruction

Invoices frequently contain multi-line item descriptions.

Example:

```
1. Nintendo Console
   White Japan Version
```

The system merges related row segments into a single logical row to preserve the correct item structure.

---

## 7. Table Matrix Construction

Detected rows and columns are mapped into a structured table matrix.

Example:

```
[No., Description, Qty, Unit, Price, Total]
```

Each cell is filled by assigning OCR words to the appropriate row and column.

---

## 8. Excel Export

The structured table is exported to Excel format using OpenPyXL.

Example output file:

```
test_outputs/invoice_output.xlsx
```

---

## 9. Extraction Metrics

The system calculates reliability metrics to evaluate extraction quality.

Metrics include:

- Average text recognition confidence
- Minimum recognition confidence
- Total detected words
- Logical row count
- Column count
- Numeric cell ratio
- Empty cell ratio
- Overall extraction score

Example:

```
Overall Score: 0.99
Status: High Reliability
```

---

# Models and Libraries Used

| Component | Library / Model |
|-----------|----------------|
| Layout Detection | YOLOv8 DocLayNet Model |
| Text Recognition | PaddleOCR |
| Image Processing | OpenCV |
| Column Clustering | Scikit-Learn |
| Table Export | OpenPyXL |
| User Interface | Streamlit |

---

# Project Structure

```
invoice_table_extractor/

layout_detection/
    layout_model.py

ocr/
    ocr_engine.py

structure/
    row_detector.py
    column_detector.py
    logical_row_builder.py
    table_builder.py

table_extraction/
    extractor.py

preprocessing/
    image_cleaner.py

metrics/
    confidence_analyzer.py

export/
    excel_exporter.py

models/
    yolov8-doclaynet.pt

app.py
run_pipeline.py
test.py
```

---

# Installation

## Create Virtual Environment

```
python -m venv venv
```

Activate environment

Windows:

```
venv\Scripts\activate
```

---

## Install Dependencies

```
pip install -r requirement.txt
```

---

# Running the Application

Start the application using Streamlit:

```
streamlit run app.py
```

The interface will open in the browser:

```
http://localhost:8501
```

---

# Supported Input Formats

Images

- PNG
- JPG
- JPEG

Documents

- PDF (maximum 5 pages)

---

# Performance

Typical processing time:

3–8 seconds per invoice depending on:

- Image resolution
- Number of detected text elements
- System hardware

---

# Limitations

The system performs best when:

- Tables are clearly structured
- Text is readable and not heavily distorted
- Documents are not severely rotated

Limitations:

- Extremely noisy scans may reduce recognition accuracy
- Handwritten invoices are not supported
- Very complex multi-table documents may require manual review

---

# Important Notes

Before running the system ensure:

1. Required model files are present in the `models` directory.
2. PaddleOCR dependencies are properly installed.
3. PDF processing requires the `pdf2image` library.
4. The application currently runs using CPU inference.

---

# Future Improvements

Possible enhancements include:

- Multi-table extraction from a single document
- Support for handwritten documents
- Automatic table header detection
- API-based deployment
- Batch document processing

---

# Author

Shivam Vishwakarma  
M.Sc. IT – Semester Project

Project Title:

**StructuRAI – Invoice Table Extraction System**
