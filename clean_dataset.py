from pathlib import Path

from PIL import Image, UnidentifiedImageError

from app.config import CLASSES

DATASET_DIR = Path("dataset")
MIN_WIDTH = 64
MIN_HEIGHT = 64
VALID_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def is_valid_image(path: Path) -> tuple[bool, str]:
    if path.suffix.lower() not in VALID_SUFFIXES:
        return False, "unsupported-extension"

    try:
        with Image.open(path) as img:
            img.verify()

        with Image.open(path) as img:
            width, height = img.size
            if width < MIN_WIDTH or height < MIN_HEIGHT:
                return False, "too-small"

    except (UnidentifiedImageError, OSError, ValueError):
        return False, "corrupt"

    return True, "ok"


def clean_class_folder(class_name: str) -> dict[str, int]:
    folder = DATASET_DIR / class_name
    folder.mkdir(parents=True, exist_ok=True)

    stats = {
        "kept": 0,
        "deleted_corrupt": 0,
        "deleted_too_small": 0,
        "deleted_unsupported": 0,
    }

    for path in folder.iterdir():
        if not path.is_file():
            continue

        valid, reason = is_valid_image(path)
        if valid:
            stats["kept"] += 1
            continue

        path.unlink(missing_ok=True)
        if reason == "corrupt":
            stats["deleted_corrupt"] += 1
        elif reason == "too-small":
            stats["deleted_too_small"] += 1
        else:
            stats["deleted_unsupported"] += 1

    return stats


def main() -> None:
    if not DATASET_DIR.exists():
        raise FileNotFoundError("dataset folder not found. Run image download first.")

    total = {
        "kept": 0,
        "deleted_corrupt": 0,
        "deleted_too_small": 0,
        "deleted_unsupported": 0,
    }

    print("Cleaning dataset...")
    for class_name in CLASSES:
        stats = clean_class_folder(class_name)
        for key, value in stats.items():
            total[key] += value

        print(
            f"{class_name}: kept={stats['kept']}, "
            f"corrupt={stats['deleted_corrupt']}, "
            f"small={stats['deleted_too_small']}, "
            f"unsupported={stats['deleted_unsupported']}"
        )

    print("Done.")
    print(
        "Summary: "
        f"kept={total['kept']}, "
        f"corrupt={total['deleted_corrupt']}, "
        f"small={total['deleted_too_small']}, "
        f"unsupported={total['deleted_unsupported']}"
    )


if __name__ == "__main__":
    main()