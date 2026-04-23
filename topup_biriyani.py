from pathlib import Path

from icrawler.builtin import BingImageCrawler

DATASET_DIR = Path("dataset")
CLASS_NAME = "biriyani"
SEARCH_TERMS = [
    "chicken biryani food plate",
    "hyderabadi biryani plate",
    "mutton biryani bowl",
    "indian biryani rice dish",
    "biryani close up",
    "dum biryani close up",
    "chicken dum biryani",
    "mutton dum biryani",
    "hyderabad chicken biryani",
    "south indian biryani",
    "pakistani biryani",
    "biryani rice bowl",
    "spicy biryani plate",
    "lamb biryani platter",
    "veg biryani bowl",
]
TARGET_COUNT = 250
VALID_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def count_images(folder: Path) -> int:
    if not folder.exists():
        return 0
    return sum(
        1
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in VALID_SUFFIXES
    )


def main() -> None:
    output_dir = DATASET_DIR / CLASS_NAME
    output_dir.mkdir(parents=True, exist_ok=True)

    current_count = count_images(output_dir)
    missing = max(0, TARGET_COUNT - current_count)

    print(f"Current biriyani images: {current_count}")
    print(f"Target biriyani images: {TARGET_COUNT}")
    print(f"Need to download: {missing}")

    if missing == 0:
        print("Biriyani already has enough images.")
        return

    crawler = BingImageCrawler(storage={"root_dir": str(output_dir)})
    remaining = missing

    for keyword in SEARCH_TERMS:
        if remaining <= 0:
            break

        print(f"Downloading biriyani images for query: {keyword}")
        crawler.crawl(keyword=keyword, max_num=remaining)
        current_count = count_images(output_dir)
        remaining = max(0, TARGET_COUNT - current_count)
        print(f"Biriyani images now: {current_count}, remaining: {remaining}")

    final_count = count_images(output_dir)
    print(f"Final biriyani images: {final_count}")


if __name__ == "__main__":
    main()
