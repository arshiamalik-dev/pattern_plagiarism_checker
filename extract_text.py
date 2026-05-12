import os
import pdfplumber
import pytesseract
from PIL import Image


SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".tiff"}


# -----------------------------
# PDF TEXT EXTRACTION
# -----------------------------
def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text


# -----------------------------
# IMAGE OCR EXTRACTION
# -----------------------------
def extract_text_from_image(file_path):
    try:
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img)
        return text
    except Exception:
        return ""
    

# -----------------------------
# UNIVERSAL EXTRACTOR
# -----------------------------
def extract_text_from_file(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        return extract_text_from_pdf(file_path)

    elif ext in {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}:
        return extract_text_from_image(file_path)

    else:
        raise ValueError(f"Unsupported file type: {ext}")
