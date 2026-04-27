import json
from pathlib import Path

import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models

IMG_SIZE = (128, 128)
BATCH_SIZE = 32
EPOCHS = 12
VAL_SPLIT = 0.2
SEED = 42

DATASET_DIR = Path("dataset")
ANNOTATIONS_PATH = DATASET_DIR / "ingredient_annotations.json"
MODEL_DIR = Path("model")
MODEL_OUTPUT = MODEL_DIR / "ingredient_model.h5"
LABELS_OUTPUT = MODEL_DIR / "ingredient_labels.json"


def validate_dataset() -> None:
    if not DATASET_DIR.exists() or not DATASET_DIR.is_dir():
        raise FileNotFoundError("Dataset folder not found. Create dataset/ first.")


def load_annotations() -> list[dict]:
    if not ANNOTATIONS_PATH.exists():
        raise FileNotFoundError(
            f"Missing annotation file: {ANNOTATIONS_PATH}. "
            "Add per-image ingredient labels before training."
        )

    payload = json.loads(ANNOTATIONS_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError(
            "ingredient_annotations.json must be a non-empty JSON array of records."
        )

    valid_records = []
    for idx, item in enumerate(payload):
        if not isinstance(item, dict):
            raise ValueError(f"Annotation at index {idx} is not an object.")

        image_rel = item.get("image")
        labels = item.get("labels")

        if not isinstance(image_rel, str) or not image_rel.strip():
            raise ValueError(f"Annotation at index {idx} has invalid 'image'.")

        if not isinstance(labels, list) or not labels:
            raise ValueError(f"Annotation at index {idx} must include non-empty 'labels'.")

        labels = [label.strip() for label in labels if isinstance(label, str) and label.strip()]
        if not labels:
            raise ValueError(f"Annotation at index {idx} has no valid labels.")

        image_path = DATASET_DIR / image_rel
        if not image_path.exists() or not image_path.is_file():
            raise FileNotFoundError(
                f"Image file not found for annotation {idx}: {image_path}"
            )

        valid_records.append(
            {
                "image": image_path.as_posix(),
                "labels": sorted(set(labels)),
            }
        )

    return valid_records


def build_ingredient_labels(records: list[dict]) -> list[str]:
    labels = set()
    for item in records:
        labels.update(item["labels"])
    return sorted(labels)


def build_multi_hot_targets(records: list[dict], ingredient_labels: list[str]) -> np.ndarray:
    targets = np.zeros((len(records), len(ingredient_labels)), dtype=np.float32)
    index = {name: idx for idx, name in enumerate(ingredient_labels)}

    for row_idx, item in enumerate(records):
        for label in item["labels"]:
            targets[row_idx, index[label]] = 1.0

    return targets


def build_model(num_outputs: int) -> tf.keras.Model:
    model = models.Sequential(
        [
            layers.Input(shape=(128, 128, 3)),
            layers.Conv2D(32, (3, 3), activation="relu"),
            layers.MaxPooling2D(2, 2),
            layers.Conv2D(64, (3, 3), activation="relu"),
            layers.MaxPooling2D(2, 2),
            layers.Conv2D(128, (3, 3), activation="relu"),
            layers.MaxPooling2D(2, 2),
            layers.Flatten(),
            layers.Dense(128, activation="relu"),
            layers.Dropout(0.3),
            layers.Dense(num_outputs, activation="sigmoid"),
        ]
    )

    model.compile(
        optimizer="adam",
        loss="binary_crossentropy",
        metrics=[
            tf.keras.metrics.BinaryAccuracy(name="binary_accuracy"),
            tf.keras.metrics.Precision(name="precision"),
            tf.keras.metrics.Recall(name="recall"),
        ],
    )
    return model


def decode_and_resize(path: tf.Tensor, labels: tf.Tensor) -> tuple[tf.Tensor, tf.Tensor]:
    image_bytes = tf.io.read_file(path)
    image = tf.image.decode_image(image_bytes, channels=3, expand_animations=False)
    image = tf.image.resize(image, IMG_SIZE)
    image = tf.cast(image, tf.float32) / 255.0
    return image, labels


def main() -> None:
    validate_dataset()

    records = load_annotations()
    ingredient_labels = build_ingredient_labels(records)

    if len(records) < 10:
        raise ValueError(
            "Need at least 10 labeled images for ingredient training. "
            f"Found {len(records)}."
        )

    targets = build_multi_hot_targets(records, ingredient_labels)
    image_paths = np.array([item["image"] for item in records])

    rng = np.random.default_rng(SEED)
    indices = np.arange(len(records))
    rng.shuffle(indices)

    split_idx = max(1, int(len(indices) * (1.0 - VAL_SPLIT)))
    train_indices = indices[:split_idx]
    val_indices = indices[split_idx:]
    if len(val_indices) == 0:
        val_indices = train_indices[-1:]
        train_indices = train_indices[:-1]

    train_paths = image_paths[train_indices]
    train_targets = targets[train_indices]
    val_paths = image_paths[val_indices]
    val_targets = targets[val_indices]

    train_ds = tf.data.Dataset.from_tensor_slices((train_paths, train_targets))
    train_ds = train_ds.shuffle(buffer_size=len(train_paths), seed=SEED)
    train_ds = train_ds.map(decode_and_resize, num_parallel_calls=tf.data.AUTOTUNE)
    train_ds = train_ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

    val_ds = tf.data.Dataset.from_tensor_slices((val_paths, val_targets))
    val_ds = val_ds.map(decode_and_resize, num_parallel_calls=tf.data.AUTOTUNE)
    val_ds = val_ds.batch(BATCH_SIZE).prefetch(tf.data.AUTOTUNE)

    model = build_model(num_outputs=len(ingredient_labels))

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor="val_loss",
            patience=3,
            restore_best_weights=True,
        )
    ]
    model.fit(train_ds, validation_data=val_ds, epochs=EPOCHS, callbacks=callbacks)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model.save(str(MODEL_OUTPUT))

    LABELS_OUTPUT.write_text(
        json.dumps(ingredient_labels, indent=2),
        encoding="utf-8",
    )

    print(f"Ingredient model trained and saved to {MODEL_OUTPUT}")
    print(f"Ingredient labels saved to {LABELS_OUTPUT}")
    print(f"Training samples: {len(train_paths)}")
    print(f"Validation samples: {len(val_paths)}")
    print(f"Ingredient classes: {len(ingredient_labels)}")


if __name__ == "__main__":
    main()
