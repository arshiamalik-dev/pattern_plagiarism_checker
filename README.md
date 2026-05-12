# Pattern Plagiarism Checker

A desktop application made with the help of AI resources that detects similarity between crochet patterns using OCR, text canonicalization, shingling, and semantic embeddings.  
Designed to compare PDFs, images, and text-based patterns with high accuracy — even when formatting or OCR quality varies.

---

## Features

- Compare **File vs File** or **File vs Folder**
- Supports **PDF**, **PNG**, **JPG**, **JPEG**, **BMP**, **TIFF**
- OCR extraction for image-based patterns
- Gentle canonicalization for crochet terminology
- Hybrid similarity scoring:
  - Semantic similarity (SentenceTransformer)
  - Shingle-based Jaccard similarity
- Dark/Light mode toggle
- Loading popup during analysis
- Confidence meter with color-coded similarity levels
- Clean, modern Tkinter GUI

---

## Installation

### 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/pattern-plagiarism-checker.git (github.com in Bing)
cd pattern-plagiarism-checker


### 2. Install dependencies
pip install -r requirements.txt


### 3. Install Tesseract OCR  
Required for image-based pattern extraction.

- **Windows:**  
  Download installer: https://github.com/UB-Mannheim/tesseract/wiki

- **macOS:**  
brew install tesseract


- **Linux:**  
sudo apt install tesseract-ocr


---

## Usage

Run the application:

python main.py


The splash screen will load the model, then the main GUI will appear.

---

## Screenshots

> Add your screenshots inside a folder named `screenshots/` and reference them here.

Example:

### Main Interface
![Main GUI](screenshots/main_gui.png)

### Dark Mode
![Dark Mode](screenshots/dark_mode.png)

---

## Project Structure

pattern-plagiarism-checker/
│
├── main.py
├── main_app.py
├── plagiarism_checker.py
├── extract_text.py
├── requirements.txt
├── README.md
└── .gitignore


---

## Requirements

- Python 3.9+
- Tesseract OCR
- PyTorch (CPU)
- SentenceTransformer model: `all-MiniLM-L6-v2`

---

## License

MIT License  
Feel free to use, modify, and distribute this project.

---

## Author

Arshia — 2026  
