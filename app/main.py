from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware

from app.config import CALORIES, CONFIDENCE_THRESHOLD
from app.config import INGREDIENTS
from app.model_loader import predict_food
from app.utils import preprocess_image

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
UPLOADS_DIR = Path("uploads")


@app.get("/")
def home():
    return {"message": "Food Calorie API Running 🚀"}


@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    image_bytes = await file.read()
    suffix = Path(file.filename or "").suffix.lower() or ".jpg"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    saved_name = f"{timestamp}_{uuid4().hex}{suffix}"
    saved_path = UPLOADS_DIR / saved_name
    saved_path.write_bytes(image_bytes)

    try:
        img = preprocess_image(image_bytes)
    except Exception:
        return {"error": "Invalid image file", "saved_file": str(saved_path)}

    food, confidence = predict_food(img)

    if confidence < CONFIDENCE_THRESHOLD:
        return {
            "food": "unknown",
            "ingredients": [],
            "calories": "N/A",
            "ingredient_total_calories": "N/A",
            "confidence": round(confidence, 2),
            "saved_file": str(saved_path),
        }

    calories = CALORIES.get(food, "N/A")
    ingredients = [item["name"] for item in INGREDIENTS.get(food, [])]

    return {
        "food": food,
        "ingredients": ingredients,
        "calories": calories,
        "ingredient_total_calories": calories,
        "confidence": round(confidence, 2),
        "saved_file": str(saved_path),
    }


