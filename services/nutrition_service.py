import httpx
import traceback
from config import SPOONACULAR_API
from services.nutrition_cache import NutritionCache
from utils.logger import logger

class NutritionService:
    def __init__(self):
        self.api_key = SPOONACULAR_API
        self.cache = NutritionCache()

    async def get_nutrition(self, ingredients: str, user_id: int = 0) -> str:
        ingredient_list = [i.strip() for i in ingredients.strip().split("\n") if i.strip()]
        all_items = []
        uncached = []

        for ingredient in ingredient_list:
            cached = await self.cache.get(ingredient)
            if cached:
                logger.info(f"[{user_id}] [Nutrition] ✅ З кешу: {ingredient}")
                all_items.append(cached)
            else:
                logger.info(f"[{user_id}] [Nutrition] ⚠️ Кеш не знайдено: {ingredient}")
                uncached.append(ingredient)

        for ingredient in uncached:
            item = await self._fetch_from_api(ingredient, user_id)
            if isinstance(item, dict):
                await self.cache.set(ingredient, item)
                all_items.append(item)
                logger.info(f"[{user_id}] [Nutrition] 📥 Додано в кеш: {ingredient}")
            elif isinstance(item, str):  # помилка
                logger.warning(f"[{user_id}] [Nutrition] ❌ API error for '{ingredient}': {item}")
                return item

        summary = self._format_summary(all_items)
        logger.info(f"[{user_id}] [Nutrition] 📊 Готово. Повернено результат")
        return summary

    async def _fetch_from_api(self, ingredient: str, user_id: int):
        try:
            url = "https://api.spoonacular.com/recipes/parseIngredients"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            params = {"apiKey": self.api_key}
            data = {
                "ingredientList": ingredient,
                "servings": 1,
                "includeNutrition": True,
                "language": "en"
            }

            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, data=data, headers=headers, params=params)
                response.raise_for_status()

            items = response.json()
            if isinstance(items, list) and items:
                logger.info(f"[{user_id}] [Nutrition] 📡 Отримано дані від Spoonacular: {ingredient}")
                return items[0]
            else:
                return f"❌ Spoonacular не повернув даних по '{ingredient}'"

        except httpx.RequestError as e:
            return f"❌ Помилка запиту до API: {e}"
        except httpx.HTTPStatusError as e:
            return f"❌ Помилка відповіді API: {e.response.status_code} - {e.response.text}"
        except Exception:
            return f"❌ Помилка:\n{traceback.format_exc()}"


    def _format_summary(self, all_items: list) -> str:
        total_calories = 0
        lines = []

        for item in all_items:
            # 🧪 Додано перевірку, якщо item = [dict]
            if isinstance(item, list) and len(item) == 1 and isinstance(item[0], dict):
                item = item[0]

            if not isinstance(item, dict):
                continue  # або лог warning, якщо хочеш

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
