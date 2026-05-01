from datetime import datetime
from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import ALLOWED_IMAGE_SUFFIXES, MAX_IMAGE_SIZE_BYTES
from app.schemas import (
    PredictionResponse, 
    PortionAdjustmentRequest,
    PortionAdjustmentResponse,
    HealthierAlternativesResponse,
    BatchPredictionResponse,
    BatchPredictionResult,
)
from app.services.prediction_service import (
    get_prediction_payload,
    adjust_portion,
    get_healthier_alternatives,
    adjust_nutrition_for_portion,
)

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


@router.post("/adjust-portion", response_model=PortionAdjustmentResponse)
async def adjust_calories_by_portion(request: PortionAdjustmentRequest) -> dict:
    """Adjust calorie count based on portion size (e.g., half, double, custom amount)"""
    return adjust_portion(
        request.original_calories,
        request.portion_multiplier,
        request.description,
    )


@router.get("/alternatives/{food}", response_model=HealthierAlternativesResponse)
async def get_alternatives(food: str, calories: float = 0.0) -> dict:
    """Get healthier food alternatives for a detected food"""
    if not food or not food.strip():
        raise HTTPException(status_code=400, detail="Food name is required")
    
    return get_healthier_alternatives(food, calories)


@router.post("/predict-batch", response_model=BatchPredictionResponse)
async def predict_batch(files: list[UploadFile] = File(...)) -> dict:
    """Process multiple food images at once"""
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    
    if not files:
        raise HTTPException(status_code=400, detail="At least one image is required")
    
    if len(files) > 10:
        raise HTTPException(status_code=413, detail="Maximum 10 images per batch")
    
    results = []
    total_calories = 0.0
    total_confidence = 0.0
    successful_count = 0
    
    for file in files:
        try:
            image_bytes = await file.read()
            if not image_bytes:
                results.append(
                    {
                        "file_name": file.filename or "unknown",
                        "food": "unknown",
                        "confidence": 0.0,
                        "calories": 0.0,
                        "nutrition": {
                            "totals": {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0},
                            "by_ingredient": [],
                        },
                        "success": False,
                        "error": "Empty file",
                    }
                )
                continue
            
            if file.content_type and not file.content_type.startswith("image/"):
                results.append(
                    {
                        "file_name": file.filename or "unknown",
                        "food": "unknown",
                        "confidence": 0.0,
                        "calories": 0.0,
                        "nutrition": {
                            "totals": {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0},
                            "by_ingredient": [],
                        },
                        "success": False,
                        "error": "Invalid content type",
                    }
                )
                continue
            
            if len(image_bytes) > MAX_IMAGE_SIZE_BYTES:
                results.append(
                    {
                        "file_name": file.filename or "unknown",
                        "food": "unknown",
                        "confidence": 0.0,
                        "calories": 0.0,
                        "nutrition": {
                            "totals": {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0},
                            "by_ingredient": [],
                        },
                        "success": False,
                        "error": "Image too large",
                    }
                )
                continue
            
            suffix = Path(file.filename or "").suffix.lower() or ".jpg"
            if suffix not in ALLOWED_IMAGE_SUFFIXES:
                results.append(
                    {
                        "file_name": file.filename or "unknown",
                        "food": "unknown",
                        "confidence": 0.0,
                        "calories": 0.0,
                        "nutrition": {
                            "totals": {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0},
                            "by_ingredient": [],
                        },
                        "success": False,
                        "error": "Unsupported image format",
                    }
                )
                continue
            
            # Save file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            saved_name = f"{timestamp}_{uuid4().hex}{suffix}"
            saved_path = UPLOADS_DIR / saved_name
            saved_path.write_bytes(image_bytes)
            
            # Get prediction
            payload, _ = await get_prediction_payload(image_bytes)
            
            result = {
                "file_name": file.filename or "unknown",
                "food": payload["food"],
                "confidence": payload["confidence"],
                "calories": payload["calories"],
                "nutrition": payload["nutrition"],
                "success": True,
                "error": "",
            }
            
            results.append(result)
            
            if payload["food"] != "unknown":
                total_calories += payload["calories"]
                total_confidence += payload["confidence"]
                successful_count += 1
        
        except Exception as e:
            results.append(
                {
                    "file_name": file.filename or "unknown",
                    "food": "unknown",
                    "confidence": 0.0,
                    "calories": 0.0,
                    "nutrition": {
                        "totals": {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0},
                        "by_ingredient": [],
                    },
                    "success": False,
                    "error": str(e),
                }
            )
    
    average_confidence = (
        total_confidence / successful_count if successful_count > 0 else 0.0
    )
    
    return {
        "total_images": len(files),
        "successful_predictions": successful_count,
        "failed_predictions": len(files) - successful_count,
        "results": results,
        "total_calories": round(total_calories, 2),
        "average_confidence": round(average_confidence, 2),
    }
