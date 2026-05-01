# Food Calorie Backend

A FastAPI service that classifies food images, estimates calories, and returns a simple ingredient breakdown for the detected dish.

## Features

- Image upload API for food classification
- TensorFlow model integration with a fallback prediction mode if the model cannot be loaded
- Calorie estimates for the supported food classes
- Saved upload tracking in the `uploads/` folder
- CORS enabled for frontend integration
- **Portion size adjustment** - Calculate calories for different portion sizes
- **Healthier alternatives** - Get healthier food suggestions with calorie comparisons
- **Batch processing** - Process multiple food images at once

## Supported Classes

The current model is set up for these labels:

- pizza
- burger
- dosa
- rice
- salad
- icecream
- biriyani
- pasta
- noodles
- chicken
- fish
- fries
- sandwich
- taco
- samosa
- momos
- paneer
- tandoori_chicken
- sushi
- steak
- cake
- waffle
- oats
- nuts

## Project Structure

- `app/` - FastAPI application code
- `app/main.py` - API routes and upload handling
- `app/model_loader.py` - model loading and prediction helpers
- `app/config.py` - class labels, ingredients, and calorie data
- `app/utils.py` - image preprocessing utilities
- `app/routers/predict.py` - prediction endpoints
- `app/services/prediction_service.py` - prediction and calculation services
- `app/schemas.py` - Pydantic models for request/response validation
- `model/` - trained model artifacts
- `dataset/` - image dataset organized by food class
- `uploads/` - saved uploaded images
- `run.py` - local development entry point
- `train_model.py` - model training script
- `download_images.py` - image collection helper
- `populate_dataset.py` - dataset preparation script
- `clean_dataset.py` - dataset cleanup script
- `topup_biriyani.py` - class-specific dataset helper
- `topup_icecream.py` - class-specific dataset helper

## REQUIRMENTS 

Install the Python dependencies listed in `requirements.txt`:

- fastapi
- uvicorn
- python-multipart
- numpy
- pillow
- tensorflow
- icrawler

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Make sure the trained model exists at `model/model.h5`.

## Run the API

Start the development server with:

```bash
python run.py
```

By default, the API runs at `http://0.0.0.0:8000`.

## API Endpoints

### 1. **Food Detection** (Single Image)
```
POST /predict
```
Upload a single food image to detect the food, get calories, and nutrition breakdown.

**Request:** Multipart form with `file` parameter (image file)

**Response Example:**
```json
{
  "food": "pizza",
  "confidence": 0.92,
  "ingredients": ["pizza base", "cheese", "tomato sauce", "vegetables"],
  "ingredient_predictions": [],
  "ingredient_source": "config_fallback",
  "calories": 320.0,
  "nutrition": {
    "totals": {
      "calories": 320.0,
      "protein": 14.2,
      "carbs": 47.0,
      "fat": 12.4
    },
    "by_ingredient": [...]
  },
  "saved_file": "uploads/20260501_143022_abc123.jpg",
  "cache_hit": false
}
```

### 2. **Portion Size Adjustment**
```
POST /adjust-portion
```
Calculate calories for a different portion size.

**Request:**
```json
{
  "original_calories": 320.0,
  "portion_multiplier": 0.5,
  "description": "half portion"
}
```

**Response:**
```json
{
  "original_calories": 320.0,
  "portion_multiplier": 0.5,
  "adjusted_calories": 160.0,
  "description": "half portion",
  "message": "Adjusted from 320.0kcal to 160.0kcal"
}
```

### 3. **Get Healthier Alternatives**
```
GET /alternatives/{food}?calories={calories}
```
Get healthier food alternatives with calorie comparison.

**Parameters:**
- `food`: Food name (e.g., "pizza", "burger", "fries")
- `calories`: Original calorie count (optional)

**Response Example:**
```json
{
  "detected_food": "pizza",
  "detected_food_calories": 320.0,
  "alternatives": [
    {
      "name": "Cauliflower crust pizza",
      "calories": 150,
      "reduction_percent": 40,
      "benefits": ["Lower carbs", "More fiber", "Lower calories"]
    },
    {
      "name": "Whole wheat pizza",
      "calories": 220,
      "reduction_percent": 25,
      "benefits": ["More fiber", "Complex carbs"]
    }
  ],
  "message": "Found 2 healthier alternatives for pizza"
}
```

### 4. **Batch Processing** (Multiple Images)
```
POST /predict-batch
```
Process up to 10 food images at once.

**Request:** Multipart form with multiple `files` parameter

**Response Example:**
```json
{
  "total_images": 3,
  "successful_predictions": 3,
  "failed_predictions": 0,
  "results": [
    {
      "file_name": "pizza.jpg",
      "food": "pizza",
      "confidence": 0.92,
      "calories": 320.0,
      "nutrition": {...},
      "success": true,
      "error": ""
    },
    {
      "file_name": "burger.jpg",
      "food": "burger",
      "confidence": 0.88,
      "calories": 370.0,
      "nutrition": {...},
      "success": true,
      "error": ""
    }
  ],
  "total_calories": 690.0,
  "average_confidence": 0.90
}
```

## Healthier Alternatives Available

The following foods have healthier alternatives configured:
- **Pizza** → Cauliflower crust pizza, Whole wheat pizza
- **Burger** → Grilled chicken burger, Veggie burger
- **Fries** → Baked sweet potato fries, Air-fried regular fries
- **Ice cream** → Greek yogurt frozen dessert, Fruit sorbet
- **Cake** → Almond flour cake, Whole wheat cake
- **Pasta** → Whole wheat pasta, Zucchini noodles
- **Noodles** → Brown rice noodles, Vegetable noodles
- **Samosa** → Baked samosa, Vegetable spring roll
- **Waffle** → Whole grain waffle, Protein waffle
- **Steak** → Lean grilled steak, Grilled salmon
- **Sandwich** → Whole wheat sandwich, Lettuce wrap sandwich

## Train Models

Train dish classifier:

```bash
python train_model.py
```

## Usage Example (cURL)

### Single Image Prediction
```bash
curl -X POST -F "file=@pizza.jpg" http://localhost:8000/predict
```

### Batch Processing
```bash
curl -X POST -F "files=@pizza.jpg" -F "files=@burger.jpg" http://localhost:8000/predict-batch
```

### Portion Adjustment
```bash
curl -X POST -H "Content-Type: application/json" \
  -d '{"original_calories": 320, "portion_multiplier": 0.5, "description": "half portion"}' \
  http://localhost:8000/adjust-portion
```

### Get Alternatives
```bash
curl "http://localhost:8000/alternatives/pizza?calories=320"
```

Train ingredient detector (multi-label):

```bash
python train_ingredient_model.py
```

Before running ingredient training, create `dataset/ingredient_annotations.json` using true per-image labels.

Example format:

```json
[
  {
    "image": "salad/salad_001.jpg",
    "labels": ["lettuce", "tomato", "cucumber", "carrot", "salt", "black pepper"]
  },
  {
    "image": "biriyani/biriyani_001.jpg",
    "labels": ["rice", "onion", "tomato", "ginger", "garlic", "chili", "turmeric"]
  }
]
```

- `image` is the relative path under `dataset/`
- `labels` are the actual ingredients visible/used for that image
- minimum recommended size is 500+ labeled images

## API Endpoints

### `GET /`

Health check endpoint.

Response:

```json
{
  "message": "Food Calorie API Running"
}
```

### `POST /predict`

Upload an image file using multipart form data with the field name `file`.

Example using `curl`:

```bash
curl -X POST "http://127.0.0.1:8000/predict" -F "file=@sample.jpg"
```

Successful response example:

```json
{
  "food": "pizza",
  "ingredients": ["pizza base", "cheese", "tomato sauce", "vegetables"],
  "ingredient_predictions": [
    {"name": "cheese", "confidence": 0.91},
    {"name": "tomato sauce", "confidence": 0.84}
  ],
  "ingredient_source": "ingredient_model",
  "calories": 320,
  "nutrition": {
    "totals": {"calories": 320.0, "protein": 13.2, "carbs": 47.0, "fat": 10.4},
    "by_ingredient": [
      {"name": "pizza base", "calories": 180.0, "protein": 6.0, "carbs": 34.0, "fat": 4.0},
      {"name": "cheese", "calories": 80.0, "protein": 5.0, "carbs": 1.0, "fat": 6.0}
    ]
  },
  "confidence": 0.92,
  "saved_file": "uploads/20260423_120000_123456_abcd1234.jpg",
  "cache_hit": false
}
```

If the uploaded image cannot be processed, the API returns:

```json
{
  "error": "Invalid image file",
  "saved_file": "uploads/..."
}
```

If the uploaded file is invalid, the API returns HTTP 400 with a structured error JSON.

If the same image is uploaded repeatedly within the cache TTL window, `cache_hit` becomes `true` for faster responses.

## Notes

- Uploaded files are saved automatically in `uploads/`.
- If `model/model.h5` is missing or cannot be loaded, the app falls back to random predictions so the service still runs.
- The calorie values are defined in `app/config.py` and can be adjusted there.
