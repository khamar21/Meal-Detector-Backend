# Food Calorie Backend

A FastAPI service that classifies food images, estimates calories, and returns a simple ingredient breakdown for the detected dish.

## Features

- Image upload API for food classification
- TensorFlow model integration with a fallback prediction mode if the model cannot be loaded
- Calorie estimates for the supported food classes
- Saved upload tracking in the `uploads/` folder
- CORS enabled for frontend integration

## Supported Classes

The current model is set up for these labels:

- pizza
- burger
- dosa
- rice
- salad
- icecream
- biriyani

## Project Structure

- `app/` - FastAPI application code
- `app/main.py` - API routes and upload handling
- `app/model_loader.py` - model loading and prediction helpers
- `app/config.py` - class labels, ingredients, and calorie data
- `app/utils.py` - image preprocessing utilities
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

## Requirements

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
  "calories": 320,
  "ingredient_total_calories": 320,
  "confidence": 0.92,
  "saved_file": "uploads/20260423_120000_123456_abcd1234.jpg"
}
```

If the uploaded image cannot be processed, the API returns:

```json
{
  "error": "Invalid image file",
  "saved_file": "uploads/..."
}
```

If the model confidence is below the threshold, the response will use `food: "unknown"` and return `N/A` for calorie values.

## Notes

- Uploaded files are saved automatically in `uploads/`.
- If `model/model.h5` is missing or cannot be loaded, the app falls back to random predictions so the service still runs.
- The calorie values are defined in `app/config.py` and can be adjusted there.
