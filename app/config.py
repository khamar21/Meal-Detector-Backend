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

CONFIDENCE_THRESHOLD = 0.6
