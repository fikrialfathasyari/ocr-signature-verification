Note:
This project is based on a real-world internship case.

Due to data confidentiality, the original dataset (government financial documents) cannot be shared.
This repository uses simulated/sample data to demonstrate the workflow.

## 📄 OCR Signature Verification System

This project simulates a document verification system that compares scanned documents with digital versions using OCR and signature detection.

### Features
- Document text comparison using OCR
- Signature detection using YOLOv8
- Signature similarity checking (ORB)
- Automated validation system

### Tech Stack
- Python
- YOLOv8 (Ultralytics)
- OpenCV
- Tesseract OCR
- RapidFuzz

### How It Works
1. Convert PDF to image
2. Detect signature regions using YOLO
3. Extract text using OCR
4. Compare text similarity
5. Validate signatures

### 📊 Example Output
```json
{
  "Similarity Text (%)": 92.5,
  "Jumlah TTD A": 4,
  "Jumlah TTD B": 4,
  "Hasil": "DITERIMA: TTD VALID & LENGKAP"
}
