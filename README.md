# DocuStruct – Automated Table Extraction and Structural Reconstruction System for Invoices

## Overview

DocuStruct is a document processing system designed to extract structured tabular data from invoice images and PDF documents.

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

# Important Notes

Before running the system ensure:

1. Required model files are present in the `models` directory.
2. PaddleOCR dependencies are properly installed.
3. PDF processing requires the `pdf2image` library.
4. The application currently runs using CPU inference.


# Author

Shivam Vishwakarma  
M.Sc. IT – Semester Project
