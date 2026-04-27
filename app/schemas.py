from pydantic import BaseModel


class IngredientPrediction(BaseModel):
    name: str
    confidence: float


class NutritionTotals(BaseModel):
    calories: float
    protein: float
    carbs: float
    fat: float


class IngredientNutrition(BaseModel):
    name: str
    calories: float
    protein: float
    carbs: float
    fat: float


class NutritionBreakdown(BaseModel):
    totals: NutritionTotals
    by_ingredient: list[IngredientNutrition]


class PredictionResponse(BaseModel):
    food: str
    confidence: float
    ingredients: list[str]
    ingredient_predictions: list[IngredientPrediction]
    ingredient_source: str
    calories: float
    nutrition: NutritionBreakdown
    saved_file: str
    cache_hit: bool
