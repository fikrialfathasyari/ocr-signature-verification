import os
import cv2
import json
import numpy as np
from pdf2image import convert_from_path
from ultralytics import YOLO
from rapidfuzz import fuzz
import pytesseract
import pdfplumber
import re

MODEL_PATH = None  # Set your local Model (.pt) path
POPPLER_PATH = None  # Set your local Poppler path
TESSERACT_CMD = None  # Set your local Tesseract path
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

model = YOLO(MODEL_PATH)

def detect_and_crop(pdf, conf=0.3, dpi=350): #0.25 bisa
    pages = convert_from_path(pdf, dpi=dpi, poppler_path=POPPLER_PATH)
    img = np.array(pages[0])
    #results = model.predict(img, conf=conf, verbose=False)
    results = model.predict(img, conf=conf, imgsz=1280, verbose=False)

    boxes = results[0].boxes.xyxy.cpu().numpy() if results[0].boxes is not None else []
    h, w, _ = img.shape

    max_area = w * h * 0.35
    min_area = w * h * 0.002

    crops = []
    for b in boxes:
        x1, y1, x2, y2 = map(int, b)
        area = (x2 - x1) * (y2 - y1)
        if min_area < area < max_area:
            crop = img[y1:y2, x1:x2]
            crops.append(crop)

    return pages, crops

def signature_similarity(img1, img2):
    orb = cv2.ORB_create(2000)
    kp1, des1 = orb.detectAndCompute(img1, None)
    kp2, des2 = orb.detectAndCompute(img2, None)

    if des1 is None or des2 is None:
        return 9999

    bf = cv2.BFMatcher(cv2.NORM_HAMMING, True)
    matches = bf.match(des1, des2)

    if len(matches) == 0:
        return 9999

    score = sum(m.distance for m in matches) / len(matches)
    return score

def normalize_text(text):
    text = (text or "").lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-z0-9.,:/\-() ]", "", text)
    return text.strip()

def remove_dates(text):
    text = re.sub(r"\b\d{1,2}\s+[a-zA-Z]+\s+\d{4}\b", "", text)
    text = re.sub(r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b", "", text)
    return text

def verify(docA, docB, sim_threshold=45):

    pagesA, sigA = detect_and_crop(docA)
    pagesB, sigB = detect_and_crop(docB)

    try:
        with pdfplumber.open(docA) as pdf:
            textA = pdf.pages[0].extract_text() or ""
    except:
        textA = ""
    textB = pytesseract.image_to_string(np.array(pagesB[0]))

    tA = normalize_text(remove_dates(textA))
    tB = normalize_text(remove_dates(textB))

    text_score = fuzz.token_set_ratio(tA, tB)
    doc_same = text_score >= 80

    countA = len(sigA)
    countB = len(sigB)

    similarities = []
    for i in range(min(countA, countB)):
        s = signature_similarity(sigA[i], sigB[i])
        similarities.append(s)

    if not doc_same:
        status = "DITOLAK: DOKUMEN BERBEDA"
    elif countB == 0:
        status = "DITOLAK: TTD TIDAK ADA DI UPLOAD"
    elif countB < 4:
        status = "DITOLAK: TTD TIDAK LENGKAP"
    else:
        bad = [s for s in similarities if s > sim_threshold]
        if len(bad) > 0:
            status = "DITOLAK: TTD BEDA"
        else:
            status = "DITERIMA: TTD VALID & LENGKAP"

    return {
        "Similarity Text (%)": float(text_score),
        "Jumlah TTD A": countA,
        "Jumlah TTD B": countB,
        "Hasil": status
    }

if __name__ == "__main__":
    result = verify(
        r"sample_data/BeforeSignature.pdf",
        r"sample_data/AfterSignature.pdf"
    )
    print(json.dumps(result, indent=4))

