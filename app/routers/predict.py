from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import ALLOWED_IMAGE_SUFFIXES, MAX_IMAGE_SIZE_BYTES
from app.schemas import PredictionResponse
from app.services.prediction_service import get_prediction_payload

router = APIRouter(tags=["prediction"])
UPLOADS_DIR = Path("uploads")


@router.get("/")
def home() -> dict[str, str]:
    return {"message": "Food Calorie API Running"}


@router.post("/predict", response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)) -> dict:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(status_code=400, detail="Empty upload")

    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid content type")

    if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
        raise HTTPException(status_code=413, detail="Image too large")

    suffix = Path(file.filename or "").suffix.lower() or ".jpg"
    if suffix not in ALLOWED_IMAGE_SUFFIXES:
        raise HTTPException(status_code=400, detail="Unsupported image format")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    saved_name = f"{timestamp}_{uuid4().hex}{suffix}"
    saved_path = UPLOADS_DIR / saved_name
    saved_path.write_bytes(image_bytes)

    payload, cache_hit = await get_prediction_payload(image_bytes)
    payload["saved_file"] = str(saved_path)
    payload["cache_hit"] = cache_hit
    return payload
