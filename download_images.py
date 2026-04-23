from pathlib import Path

from icrawler.builtin import BingImageCrawler

from app.config import CLASSES

DATASET_DIR = Path("dataset")
VALID_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

SEARCH_TERMS = {
    "pizza": [
        "pizza food close up",
        "cheese pizza slice",
        "pepperoni pizza plate",
        "margherita pizza close up",
    ],
    "burger": [
        "burger food close up",
        "cheeseburger meal",
        "burger with fries",
        "double burger close up",
    ],
    "dosa": [
        "masala dosa indian food",
        "crispy dosa plate",
        "south indian dosa close up",
        "paper dosa chutney",
    ],
    "rice": [
        "cooked rice food bowl",
        "steamed rice plate",
        "white rice bowl close up",
        "rice meal indian food",
    ],
    "salad": [
        "fresh salad food bowl",
        "mixed vegetable salad",
        "green salad close up",
        "healthy salad plate",
    ],
    "icecream": [
        "ice cream scoop dessert",
        "ice cream cone close up",
        "chocolate ice cream scoop",
        "assorted ice cream scoops",
    ],
    "biriyani": [
        "chicken biryani food plate",
        "hyderabadi biryani plate",
        "mutton biryani bowl",
        "spicy biryani rice dish",
    ],
}


def count_images(folder: Path) -> int:
    if not folder.exists():
        return 0
    return sum(
        1
        for path in folder.iterdir()
        if path.is_file() and path.suffix.lower() in VALID_SUFFIXES
    )


def download_class_images(class_name: str, keywords: list[str], target_count: int) -> None:
    output_dir = DATASET_DIR / class_name
    output_dir.mkdir(parents=True, exist_ok=True)

    crawler = BingImageCrawler(storage={"root_dir": str(output_dir)})
    remaining = max(0, target_count - count_images(output_dir))

    for keyword in keywords:
        if remaining <= 0:
            break

        print(f"  query: {keyword}")
        crawler.crawl(keyword=keyword, max_num=min(remaining, 75))
        remaining = max(0, target_count - count_images(output_dir))


def main() -> None:
    per_class = 250

    for class_name in CLASSES:
        keywords = SEARCH_TERMS.get(class_name, [class_name])
        print(f"Downloading {class_name} images...")
        download_class_images(class_name, keywords, per_class)


if __name__ == "__main__":
    main()