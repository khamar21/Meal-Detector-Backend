from pathlib import Path

import tensorflow as tf
from tensorflow.keras import layers, models
from tensorflow.keras.preprocessing.image import ImageDataGenerator

from app.config import CLASSES

IMG_SIZE = (128, 128)
BATCH_SIZE = 32
EPOCHS = 10

DATASET_DIR = Path("dataset")
MODEL_OUTPUT = Path("model") / "model.h5"


def validate_dataset() -> None:
    if not DATASET_DIR.exists() or not DATASET_DIR.is_dir():
        raise FileNotFoundError(
            "Dataset folder not found. Create dataset/<class_name>/... first."
        )

    missing_classes = [name for name in CLASSES if not (DATASET_DIR / name).is_dir()]
    if missing_classes:
        raise ValueError(
            "Missing class folders in dataset: " + ", ".join(missing_classes)
        )


def build_model(num_classes: int) -> tf.keras.Model:
    model = models.Sequential(
        [
            layers.Input(shape=(128, 128, 3)),
            layers.Conv2D(32, (3, 3), activation="relu"),
            layers.MaxPooling2D(2, 2),
            layers.Conv2D(64, (3, 3), activation="relu"),
            layers.MaxPooling2D(2, 2),
            layers.Flatten(),
            layers.Dense(128, activation="relu"),
            layers.Dense(num_classes, activation="softmax"),
        ]
    )

    model.compile(
        optimizer="adam",
        loss="categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def main() -> None:
    validate_dataset()

    data_gen = ImageDataGenerator(rescale=1.0 / 255.0, validation_split=0.2)

    # Force generator class order to match app.config.CLASSES.
    train_generator = data_gen.flow_from_directory(
        str(DATASET_DIR),
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="training",
        classes=CLASSES,
        shuffle=True,
    )

    val_generator = data_gen.flow_from_directory(
        str(DATASET_DIR),
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode="categorical",
        subset="validation",
        classes=CLASSES,
        shuffle=False,
    )

    model = build_model(train_generator.num_classes)
    model.fit(train_generator, validation_data=val_generator, epochs=EPOCHS)

    MODEL_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    model.save(str(MODEL_OUTPUT))

    print(f"Model trained and saved to {MODEL_OUTPUT}")


if __name__ == "__main__":
    main()