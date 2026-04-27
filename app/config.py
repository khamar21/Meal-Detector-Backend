CLASSES = [
	"pizza",
	"burger",
	"dosa",
	"rice",
	"salad",
	"icecream",
	"biriyani",
]

INGREDIENTS = {
	"pizza": [
		{"name": "pizza base", "calories": 180},
		{"name": "cheese", "calories": 80},
		{"name": "tomato sauce", "calories": 20},
		{"name": "vegetables", "calories": 40},
	],
	"burger": [
		{"name": "bun", "calories": 140},
		{"name": "patty", "calories": 120},
		{"name": "cheese", "calories": 70},
		{"name": "lettuce and sauce", "calories": 40},
	],
	"dosa": [
		{"name": "dosa batter", "calories": 140},
		{"name": "oil", "calories": 25},
		{"name": "sambar", "calories": 30},
		{"name": "chutney", "calories": 25},
	],
	"rice": [
		{"name": "cooked rice", "calories": 130},
	],
	"salad": [
		{"name": "leafy vegetables", "calories": 20},
		{"name": "tomato", "calories": 10},
		{"name": "cucumber", "calories": 10},
		{"name": "dressing", "calories": 40},
	],
	"icecream": [
		{"name": "milk", "calories": 110},
		{"name": "sugar", "calories": 70},
		{"name": "cream", "calories": 27},
	],
	"biriyani": [
		{"name": "rice", "calories": 180},
		{"name": "meat or vegetables", "calories": 70},
		{"name": "oil and spices", "calories": 40},
	],
}

CALORIES = {food: sum(item["calories"] for item in ingredients) for food, ingredients in INGREDIENTS.items()}
INGREDIENT_CALORIES = {}
for _food, _ingredients in INGREDIENTS.items():
	for _item in _ingredients:
		name = _item["name"]
		INGREDIENT_CALORIES[name] = max(INGREDIENT_CALORIES.get(name, 0), _item["calories"])

# Nutrition values are approximate per serving used by this project.
NUTRITION_DB = {
	"pizza base": {"calories": 180, "protein": 6.0, "carbs": 34.0, "fat": 4.0},
	"cheese": {"calories": 80, "protein": 5.0, "carbs": 1.0, "fat": 6.0},
	"tomato sauce": {"calories": 20, "protein": 0.7, "carbs": 4.0, "fat": 0.1},
	"vegetables": {"calories": 40, "protein": 1.5, "carbs": 8.0, "fat": 0.3},
	"bun": {"calories": 140, "protein": 4.0, "carbs": 26.0, "fat": 2.0},
	"patty": {"calories": 120, "protein": 11.0, "carbs": 3.0, "fat": 7.0},
	"lettuce and sauce": {"calories": 40, "protein": 0.8, "carbs": 4.0, "fat": 2.2},
	"dosa batter": {"calories": 140, "protein": 3.0, "carbs": 24.0, "fat": 3.0},
	"oil": {"calories": 25, "protein": 0.0, "carbs": 0.0, "fat": 2.8},
	"sambar": {"calories": 30, "protein": 1.2, "carbs": 4.0, "fat": 0.9},
	"chutney": {"calories": 25, "protein": 0.5, "carbs": 2.0, "fat": 1.8},
	"cooked rice": {"calories": 130, "protein": 2.4, "carbs": 28.0, "fat": 0.3},
	"leafy vegetables": {"calories": 20, "protein": 1.5, "carbs": 3.0, "fat": 0.2},
	"tomato": {"calories": 10, "protein": 0.4, "carbs": 2.2, "fat": 0.1},
	"cucumber": {"calories": 10, "protein": 0.3, "carbs": 1.8, "fat": 0.1},
	"dressing": {"calories": 40, "protein": 0.2, "carbs": 3.0, "fat": 3.0},
	"milk": {"calories": 110, "protein": 5.8, "carbs": 8.0, "fat": 6.0},
	"sugar": {"calories": 70, "protein": 0.0, "carbs": 18.0, "fat": 0.0},
	"cream": {"calories": 27, "protein": 0.2, "carbs": 0.6, "fat": 2.8},
	"rice": {"calories": 180, "protein": 3.2, "carbs": 40.0, "fat": 0.4},
	"meat or vegetables": {"calories": 70, "protein": 5.0, "carbs": 3.0, "fat": 4.0},
	"oil and spices": {"calories": 40, "protein": 0.5, "carbs": 2.0, "fat": 3.5},
	"onion": {"calories": 16, "protein": 0.4, "carbs": 3.7, "fat": 0.0},
	"ginger": {"calories": 8, "protein": 0.2, "carbs": 1.8, "fat": 0.1},
	"garlic": {"calories": 10, "protein": 0.5, "carbs": 2.3, "fat": 0.0},
	"chili": {"calories": 6, "protein": 0.3, "carbs": 1.3, "fat": 0.1},
	"turmeric": {"calories": 8, "protein": 0.2, "carbs": 1.4, "fat": 0.1},
	"coriander": {"calories": 5, "protein": 0.4, "carbs": 0.9, "fat": 0.1},
	"salt": {"calories": 0, "protein": 0.0, "carbs": 0.0, "fat": 0.0},
	"black pepper": {"calories": 3, "protein": 0.1, "carbs": 0.7, "fat": 0.0},
	"carrot": {"calories": 12, "protein": 0.3, "carbs": 2.8, "fat": 0.1},
}

CONFIDENCE_THRESHOLD = 0.6
INGREDIENT_CONFIDENCE_THRESHOLD = 0.5
ALLOWED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
MAX_IMAGE_SIZE_BYTES = 8 * 1024 * 1024
CACHE_TTL_SECONDS = 300
