import random

import numpy as np
import tensorflow as tf

from app.config import CLASSES

MODEL_PATH = "model/model.h5"

try:
	model = tf.keras.models.load_model(MODEL_PATH)
	MODEL_LOADED = True
except Exception:
	print("Model not found. Using random predictions.")
	MODEL_LOADED = False


def predict_food(img=None):
	if MODEL_LOADED and img is not None:
		prediction = model.predict(img)
		index = int(np.argmax(prediction))
		confidence = float(prediction[0][index])
		return CLASSES[index], confidence

	food = random.choice(CLASSES)
	confidence = random.uniform(0.5, 0.9)
	return food, confidence
