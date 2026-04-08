---
title: DocuStruct                
emoji: "📄"
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
---

# DocuStruct – Structured Table Extraction System

## Live Demo
https://huggingface.co/spaces/shivam2k2/DocuStruct
---

## Overview
DocuStruct is an AI-powered system designed to extract structured tables from invoices and business documents (images/PDFs).  
It combines layout detection, OCR, and custom table reconstruction logic to generate reliable tabular outputs.

---

## Features
- Table detection using YOLO (DocLayNet-based model)
- OCR using PaddleOCR
- Custom fallback logic for table reconstruction
- Multi-table handling
- Editable table UI with download support
- Confidence score and detailed metrics

---

## Tech Stack
- Python, Streamlit  
- YOLO (Ultralytics) for layout detection  
- PaddleOCR for text extraction  
- OpenCV & NumPy for preprocessing  
- Custom rule-based table reconstruction  

---

## Project Flow
1. Upload document (Image/PDF – single page)
2. Detect table regions using YOLO
3. Extract text using OCR
4. Group words → detect rows
5. Cluster X positions → detect columns
6. Construct logical table
7. Display results + metrics

---

