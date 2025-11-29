import os
import re
from typing import Tuple
import joblib
from sentence_transformers import SentenceTransformer

BASE_DIR = os.path.dirname(__file__)
MODEL_DIR = os.path.abspath(os.path.join(BASE_DIR, "../models"))

ENC_DIR = os.path.join(MODEL_DIR, "sbert_encoder")
CLF_PATH = os.path.join(MODEL_DIR, "sbert_model.pkl")
THRESH_PATH = os.path.join(MODEL_DIR, "sbert_threshold.txt")

try:
    encoder = SentenceTransformer(ENC_DIR)
    clf = joblib.load(CLF_PATH)

    with open(THRESH_PATH, "r") as f:
        THRESH = float(f.read().strip())

    print("SBERT toxicity model loaded.")
except Exception as e:
    print(f"Failed to load SBERT model: {e}")
    encoder = None
    clf = None
    THRESH = 0.5

def clean_text(s: str) -> str:
    if not s:
        return ""
    s = s.lower()
    s = s.replace("\n", " ")
    s = re.sub(r"http\S+", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def predict_toxicity(text: str) -> Tuple[int, float]:
    if encoder is None or clf is None:
        return 0, 0.0

    text_clean = clean_text(text)

    emb = encoder.encode(
        [text_clean],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    prob = clf.predict_proba(emb)[0][1]
    pred = int(prob >= THRESH)

    return pred, float(prob)
