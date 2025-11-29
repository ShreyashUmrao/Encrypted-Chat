import os
import joblib
import pandas as pd
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from app.database.database import get_db
from app.models.models import Message
from app.services.toxicity import clean_text

router = APIRouter(prefix="/model", tags=["Model"])

MODEL_DIR = os.path.join(os.path.dirname(__file__), "../models")
VECT_PATH = os.path.abspath(os.path.join(MODEL_DIR, "vectorizer.pkl"))
MODEL_PATH = os.path.abspath(os.path.join(MODEL_DIR, "model.pkl"))

@router.get("/status")
def model_status():
    exists = os.path.exists(MODEL_PATH) and os.path.exists(VECT_PATH)
    size = (
        os.path.getsize(MODEL_PATH) + os.path.getsize(VECT_PATH)
        if exists
        else 0
    )
    return {
        "model_loaded": exists,
        "model_size_kb": round(size / 1024, 2),
        "model_dir": MODEL_DIR,
    }

@router.post("/retrain")
async def retrain_model(
    db: Session = Depends(get_db),
    file: UploadFile = File(None)
):

    print("Starting model retraining...")

    if file:
        try:
            df = pd.read_csv(file.file)
            if "text" not in df.columns or "label" not in df.columns:
                raise HTTPException(
                    status_code=400,
                    detail="CSV must contain 'text' and 'label' columns",
                )
            print(f"Loaded dataset from upload: {df.shape[0]} samples")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to read CSV: {e}")
    else:
        messages = db.query(Message).all()
        if not messages:
            raise HTTPException(status_code=400, detail="No messages available for retraining")
        df = pd.DataFrame(
            [{"text": clean_text(m.ciphertext), "label": int(m.is_toxic)} for m in messages]
        )
        print(f"Loaded {len(df)} messages from database for retraining")

    df["text"] = df["text"].astype(str).apply(clean_text)

    X_train, X_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.2, random_state=42
    )

    vectorizer = TfidfVectorizer(max_features=5000, ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)

    model = LogisticRegression(max_iter=200)
    model.fit(X_train_vec, y_train)

    y_pred = model.predict(X_test_vec)
    acc = accuracy_score(y_test, y_pred)
    print(f"Retrained model accuracy: {acc:.4f}")

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(vectorizer, VECT_PATH)
    joblib.dump(model, MODEL_PATH)
    print(f"Saved updated model + vectorizer to {MODEL_DIR}")

    return {
        "message": "Model retrained successfully",
        "samples": len(df),
        "accuracy": round(acc, 4),
        "model_path": MODEL_PATH,
        "vectorizer_path": VECT_PATH,
    }
