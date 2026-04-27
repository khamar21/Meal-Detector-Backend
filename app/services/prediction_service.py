import hashlib
import asyncio
import time
from dataclasses import dataclass

from fastapi import HTTPException

from app.config import CACHE_TTL_SECONDS, CALORIES, CONFIDENCE_THRESHOLD
from app.config import INGREDIENT_CONFIDENCE_THRESHOLD, INGREDIENTS, NUTRITION_DB
from app.model_loader import predict_food, predict_ingredients
from app.utils import preprocess_image


@dataclass
class CacheItem:
    payload: dict
    expires_at: float


_prediction_cache: dict[str, CacheItem] = {}


def _hash_image(image_bytes: bytes) -> str:
    return hashlib.sha256(image_bytes).hexdigest()


def _cache_get(key: str) -> dict | None:
    item = _prediction_cache.get(key)
    if item is None:
        return None

    if item.expires_at < time.monotonic():
        _prediction_cache.pop(key, None)
        return None

    return item.payload


def _cache_set(key: str, payload: dict) -> None:
    _prediction_cache[key] = CacheItem(
        payload=payload,
        expires_at=time.monotonic() + CACHE_TTL_SECONDS,
    )


def _get_fallback_ingredients(food: str) -> list[str]:
    return [item["name"] for item in INGREDIENTS.get(food, [])]


def _build_nutrition(ingredients: list[str]) -> dict:
    by_ingredient = []
    totals = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}

    for ingredient_name in ingredients:
        values = NUTRITION_DB.get(
            ingredient_name,
            {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0},
        )
        row = {
            "name": ingredient_name,
            "calories": float(values["calories"]),
            "protein": float(values["protein"]),
            "carbs": float(values["carbs"]),
            "fat": float(values["fat"]),
        }
        by_ingredient.append(row)

        totals["calories"] += row["calories"]
        totals["protein"] += row["protein"]
        totals["carbs"] += row["carbs"]
        totals["fat"] += row["fat"]

    totals = {name: round(value, 2) for name, value in totals.items()}
    return {"totals": totals, "by_ingredient": by_ingredient}


async def get_prediction_payload(image_bytes: bytes) -> tuple[dict, bool]:
    cache_key = _hash_image(image_bytes)
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached, True

    try:
        img = await asyncio.to_thread(preprocess_image, image_bytes)
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid image file") from exc

    food, confidence = await asyncio.to_thread(predict_food, img)
    confidence = round(float(confidence), 2)

    if confidence < CONFIDENCE_THRESHOLD:
        payload = {
            "food": "unknown",
            "confidence": confidence,
            "ingredients": [],
            "ingredient_predictions": [],
            "ingredient_source": "none",
            "calories": 0.0,
            "nutrition": {
                "totals": {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0},
                "by_ingredient": [],
            },
        }
        _cache_set(cache_key, payload)
        return payload, False

    predicted_ingredients = await asyncio.to_thread(
        predict_ingredients,
        img,
        INGREDIENT_CONFIDENCE_THRESHOLD,
    )

    if predicted_ingredients:
        ingredients = [item["name"] for item in predicted_ingredients]
        ingredient_source = "ingredient_model"
    else:
        ingredients = _get_fallback_ingredients(food)
        ingredient_source = "config_fallback"

    nutrition = _build_nutrition(ingredients)

    payload = {
        "food": food,
        "confidence": confidence,
        "ingredients": ingredients,
        "ingredient_predictions": predicted_ingredients,
        "ingredient_source": ingredient_source,
        "calories": round(float(CALORIES.get(food, nutrition["totals"]["calories"])), 2),
        "nutrition": nutrition,
    }
    _cache_set(cache_key, payload)
    return payload, False
