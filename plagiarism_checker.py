import os
import re
from typing import List, Tuple

from extract_text import extract_text_from_file, SUPPORTED_EXTENSIONS
from sentence_transformers import SentenceTransformer, util


# -----------------------------
# LAZY MODEL LOADING
# -----------------------------
_model = None

def get_model():
    """Load the SentenceTransformer model only once."""
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


# -----------------------------
# OCR REPAIR ENGINE
# -----------------------------
def repair_ocr(text: str) -> str:
    """
    Repairs common OCR errors found in crochet patterns.
    This dramatically improves matching between PDF and image versions.
    """

    # Fix common OCR misreads
    replacements = {
        "eh": "ch",
        "c h": "ch",
        "cl": "ch",
        "dh": "ch",
        "d c": "dc",
        "de": "dc",
        "do": "dc",
        "s1 st": "sl st",
        "si st": "sl st",
        "slst": "sl st",
        "5c": "sc",
        "s c": "sc",
        "t r": "tr",
        "trr": "tr",
        "rcw": "row",
        "rno": "rnd",
        "rmd": "rnd",
    }

    for wrong, right in replacements.items():
        text = text.replace(wrong, right)

    # Fix spacing issues
    text = re.sub(r"(\d+)\s+(st|sts)", r"\1 \2", text)
    text = re.sub(r"(ch|sc|dc|tr|sl st)\s+(\d+)", r"\1 \2", text)

    return text


# -----------------------------
# CANONICALIZATION (GENTLE VERSION)
# -----------------------------
def canonicalize(text: str) -> str:
    """
    Gentle canonicalization designed specifically for crochet patterns.
    Keeps numbers, stitch counts, and structure intact.
    Removes only noise and OCR artifacts.
    """

    # Lowercase
    text = text.lower()

    # Repair OCR BEFORE canonicalization
    text = repair_ocr(text)

    # Fix common OCR ligatures
    text = text.replace("ﬁ", "fi").replace("ﬂ", "fl")

    # Replace long dashes with spaces
    text = text.replace("—", " ").replace("–", " ")

    # Remove page numbers and headers/footers
    text = re.sub(r"page\s*\d+", " ", text)
    text = re.sub(r"\b\d+\s*/\s*\d+\b", " ", text)

    # Normalize spacing around punctuation
    text = re.sub(r"[,;:]", " ", text)

    # Normalize stitch abbreviations (gentle)
    stitch_map = {
        r"\bsl\s*st\b": "sl st",
        r"\bslst\b": "sl st",
        r"\bchain\b": "ch",
        r"\bch\b": "ch",
        r"\bsc\b": "sc",
        r"\bdc\b": "dc",
        r"\btr\b": "tr",
        r"\binc\b": "inc",
        r"\bdec\b": "dec",
    }
    for pattern, replacement in stitch_map.items():
        text = re.sub(pattern, replacement, text)

    # Remove stray non-alphanumeric characters but KEEP numbers
    text = re.sub(r"[^\w\s]", " ", text)

    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


# -----------------------------
# SHINGLING
# -----------------------------
def shingle_text(text: str, k: int = 2):
    """Break text into overlapping k-word shingles."""
    words = text.split()
    return [" ".join(words[i:i+k]) for i in range(len(words) - k + 1)]


# -----------------------------
# JACCARD SIMILARITY
# -----------------------------
def jaccard_similarity(set_a: set, set_b: set) -> float:
    if not set_a and not set_b:
        return 0.0
    return len(set_a & set_b) / len(set_a | set_b)


# -----------------------------
# SEMANTIC SIMILARITY
# -----------------------------
def semantic_similarity(text1: str, text2: str) -> float:
    """Compute cosine similarity between embeddings."""
    model = get_model()
    emb1 = model.encode(text1, convert_to_tensor=True)
    emb2 = model.encode(text2, convert_to_tensor=True)
    return float(util.cos_sim(emb1, emb2).item())


# -----------------------------
# HYBRID SIMILARITY
# -----------------------------
def hybrid_similarity(text1: str, text2: str, mode="loose") -> float:
    """
    Combine semantic similarity + shingle similarity.
    Canonicalization ensures stable matching across formats.
    """

    # Canonicalize both texts
    text1 = canonicalize(text1)
    text2 = canonicalize(text2)

    # Shingles
    shingles1 = set(shingle_text(text1, 2))
    shingles2 = set(shingle_text(text2, 2))

    shingle_score = jaccard_similarity(shingles1, shingles2)
    semantic_score = semantic_similarity(text1, text2)

    if mode == "strict":
        # Balanced weighting
        return (semantic_score * 0.5) + (shingle_score * 0.5)
    else:
        # Semantic-heavy for OCR robustness
        return (semantic_score * 0.85) + (shingle_score * 0.15)


# -----------------------------
# FILE vs FILE
# -----------------------------
def compare_files(path1: str, path2: str, mode="loose") -> float:
    text1 = extract_text_from_file(path1)
    text2 = extract_text_from_file(path2)
    return hybrid_similarity(text1, text2, mode)


# -----------------------------
# FILE vs FOLDER
# -----------------------------
def compare_file_to_folder(file_path: str, folder_path: str, mode="loose"):
    base_text = extract_text_from_file(file_path)
    base_text = canonicalize(base_text)
    base_shingles = set(shingle_text(base_text, 2))

    results = []

    for filename in os.listdir(folder_path):
        full = os.path.join(folder_path, filename)

        if not os.path.isfile(full):
            continue

        ext = os.path.splitext(filename)[1].lower()
        if ext not in SUPPORTED_EXTENSIONS:
            continue

        other_text = extract_text_from_file(full)
        other_text = canonicalize(other_text)
        other_shingles = set(shingle_text(other_text, 2))

        shingle_score = jaccard_similarity(base_shingles, other_shingles)
        semantic_score = semantic_similarity(base_text, other_text)

        if mode == "strict":
            score = (semantic_score * 0.5) + (shingle_score * 0.5)
        else:
            score = (semantic_score * 0.85) + (shingle_score * 0.15)

        results.append((filename, score))

    results.sort(key=lambda x: x[1], reverse=True)
    return results
