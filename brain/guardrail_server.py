from fastapi import FastAPI
from pydantic import BaseModel
from transformers import pipeline

app = FastAPI()

# Load once at startup
toxicity_classifier = pipeline(
    "text-classification",
    model="unitary/unbiased-toxic-roberta",
    top_k=None
)

THRESHOLD = 0.8


class InputText(BaseModel):
    text: str


def check_input_safety(text: str):
    """
    Returns (is_safe, scores)
    """
    results = toxicity_classifier(text)[0]

    scores = {item["label"]: item["score"] for item in results}

    unsafe = any(score > THRESHOLD for score in scores.values())

    return (not unsafe), scores


@app.post("/check")
def check_text(req: InputText):
    safe, scores = check_input_safety(req.text)

    return {
        "safe": safe,
        "scores": scores
    }