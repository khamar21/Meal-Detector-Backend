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


class PortionAdjustmentRequest(BaseModel):
    """Request for adjusting calories based on portion size"""
    original_calories: float
    portion_multiplier: float  # e.g., 0.5 for half, 2.0 for double
    description: str = ""  # e.g., "half portion", "1 cup", "200g"


class PortionAdjustmentResponse(BaseModel):
    """Response with adjusted calorie information"""
    original_calories: float
    portion_multiplier: float
    adjusted_calories: float
    description: str
    message: str


class HealthierAlternative(BaseModel):
    """A healthier alternative to a detected food"""
    name: str
    calories: float
    reduction_percent: int
    benefits: list[str]


class HealthierAlternativesResponse(BaseModel):
    """Response with healthier food alternatives"""
    detected_food: str
    detected_food_calories: float
    alternatives: list[HealthierAlternative]
    message: str


class BatchPredictionResult(BaseModel):
    """Result for a single prediction in batch processing"""
    file_name: str
    food: str
    confidence: float
    calories: float
    nutrition: NutritionBreakdown
    success: bool
    error: str = ""


class BatchPredictionResponse(BaseModel):
    """Response for batch image processing"""
    total_images: int
    successful_predictions: int
    failed_predictions: int
    results: list[BatchPredictionResult]
    total_calories: float
    average_confidence: float
