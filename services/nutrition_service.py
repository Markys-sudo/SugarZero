import httpx
import traceback
from config import SPOONACULAR_API

class NutritionService:
    def __init__(self):
        self.api_key = SPOONACULAR_API

    async def get_nutrition(self, ingredients: str) -> str:
        try:
            url = "https://api.spoonacular.com/recipes/parseIngredients"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            params = {"apiKey": self.api_key}
            data = {
                "ingredientList": ingredients,  # тут має бути str з \n розділювачами
                "servings": 1,
                "includeNutrition": True,
                "language": "en"
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                try:
                    # 🔧 ТУТ: передаємо `params=params` з ключем API
                    response = await client.post(url, data=data, headers=headers, params=params)
                    response.raise_for_status()
                except httpx.RequestError as e:
                    return f"❌ Помилка запиту до API: {e}"
                except httpx.HTTPStatusError as e:
                    return f"❌ Помилка відповіді API: {e.response.status_code} - {e.response.text}"

            items = response.json()

            if not items or not isinstance(items, list):
                return "❌ Не вдалося отримати інформацію про поживність."

            total_calories = 0
            lines = []

            for item in items:
                name = item.get("name", "невідомо")
                nutrients = item.get("nutrition", {}).get("nutrients", [])
                calories = 0

                for nutrient in nutrients:
                    if nutrient.get("name", "").lower() == "calories":
                        calories = nutrient.get("amount", 0)
                        break

                total_calories += calories
                lines.append(f"{name}: {int(calories)} ккал")

            return "\n".join(lines) + f"\n\n🔢 Загалом: {int(total_calories)} ккал"

        except Exception:
            error_details = traceback.format_exc()
            return f"❌ Помилка під час обрахунку калорій:\n{error_details}"
