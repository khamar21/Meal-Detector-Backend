from pathlib import Path
import shutil
import uuid

from icrawler.builtin import BingImageCrawler

DATASET_DIR = Path("dataset")
CLASS_NAME = "icecream"
SEARCH_TERMS = [
    "vanilla ice cream scoop",
    "chocolate ice cream scoop",
    "strawberry ice cream scoop",
    "mango ice cream scoop",
    "butterscotch ice cream scoop",
    "pistachio ice cream scoop",
    "cookies and cream ice cream",
    "mint chocolate chip ice cream",
    "blueberry ice cream scoop",
    "caramel ice cream scoop",
    "coffee ice cream scoop",
    "black currant ice cream scoop",
    "kulfi ice cream indian dessert",
    "gelato assorted flavors",
    "ice cream sundae bowl",
    "soft serve ice cream cone",
]
TARGET_COUNT = 300
VALID_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def count_images(folder: Path) -> int:
    if not folder.exists():
        return 0
    return sum(
        1
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in VALID_SUFFIXES
    )


def move_new_images(src_dir: Path, dst_dir: Path) -> int:
    moved = 0
    for path in src_dir.iterdir():
        if not path.is_file() or path.suffix.lower() not in VALID_SUFFIXES:
            continue

        new_name = f"{uuid.uuid4().hex}{path.suffix.lower()}"
        target = dst_dir / new_name
        shutil.move(str(path), str(target))
        moved += 1

    return moved


def main() -> None:
    output_dir = DATASET_DIR / CLASS_NAME
    output_dir.mkdir(parents=True, exist_ok=True)
    temp_root = DATASET_DIR / "_tmp_icecream"
    temp_root.mkdir(parents=True, exist_ok=True)

    current_count = count_images(output_dir)
    missing = max(0, TARGET_COUNT - current_count)

    print(f"Current icecream images: {current_count}")
    print(f"Target icecream images: {TARGET_COUNT}")
    print(f"Need to download: {missing}")

    if missing == 0:
        print("Icecream already has enough images.")
        return

    crawler = BingImageCrawler(storage={"root_dir": str(output_dir)})
    remaining = missing

    for keyword in SEARCH_TERMS:
        if remaining <= 0:
            break

        print(f"Downloading icecream images for query: {keyword}")
        query_tmp = temp_root / keyword.replace(" ", "_")
        if query_tmp.exists():
            shutil.rmtree(query_tmp)
        query_tmp.mkdir(parents=True, exist_ok=True)

        crawler = BingImageCrawler(storage={"root_dir": str(query_tmp)})
        crawler.crawl(keyword=keyword, max_num=min(remaining, 40))
        moved = move_new_images(query_tmp, output_dir)
        shutil.rmtree(query_tmp, ignore_errors=True)

        current_count = count_images(output_dir)
        remaining = max(0, TARGET_COUNT - current_count)
        print(
            f"Added {moved} images from query, "
            f"icecream images now: {current_count}, remaining: {remaining}"
        )

    final_count = count_images(output_dir)
    shutil.rmtree(temp_root, ignore_errors=True)
    print(f"Final icecream images: {final_count}")


if __name__ == "__main__":
    main()
