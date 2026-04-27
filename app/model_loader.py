import json
import random
from pathlib import Path

import numpy as np
import tensorflow as tf

from app.config import CLASSES

FOOD_MODEL_PATH = "model/model.h5"
INGREDIENT_MODEL_PATH = "model/ingredient_model.h5"
INGREDIENT_LABELS_PATH = "model/ingredient_labels.json"

try:
	food_model = tf.keras.models.load_model(FOOD_MODEL_PATH)
	FOOD_MODEL_LOADED = True
except Exception:
	print("Food model not found. Using random food predictions.")
	FOOD_MODEL_LOADED = False

try:
	ingredient_model = tf.keras.models.load_model(INGREDIENT_MODEL_PATH)
	ingredient_labels = json.loads(Path(INGREDIENT_LABELS_PATH).read_text(encoding="utf-8"))
	INGREDIENT_MODEL_LOADED = True
except Exception:
	ingredient_model = None
	ingredient_labels = []
	INGREDIENT_MODEL_LOADED = False


def predict_food(img=None):
	if FOOD_MODEL_LOADED and img is not None:
		prediction = food_model.predict(img, verbose=0)
		index = int(np.argmax(prediction))
		confidence = float(prediction[0][index])
		return CLASSES[index], confidence

	food = random.choice(CLASSES)
	confidence = random.uniform(0.5, 0.9)
	return food, confidence


def predict_ingredients(img=None, threshold: float = 0.5):
	if not INGREDIENT_MODEL_LOADED or img is None:
		return []

	prediction = ingredient_model.predict(img, verbose=0)[0]
	selected = []

	for index, confidence in enumerate(prediction):
		if float(confidence) >= threshold:
			selected.append(
				{
					"name": ingredient_labels[index],
					"confidence": round(float(confidence), 2),
				}
			)

	selected.sort(key=lambda item: item["confidence"], reverse=True)
	return selected
