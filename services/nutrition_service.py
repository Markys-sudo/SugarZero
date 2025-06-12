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

    # def _format_summary(self, all_items: list) -> str:
    #     total_calories = 0
    #     lines = []
    #
    #     for item in all_items:
    #         # 🧪 Додано перевірку, якщо item = [dict]
    #         if isinstance(item, list) and len(item) == 1 and isinstance(item[0], dict):
    #             item = item[0]
    #
    #         if not isinstance(item, dict):
    #             continue  # або лог warning, якщо хочеш
    #
    #         name = item.get("name", "невідомо")
    #         nutrients = item.get("nutrition", {}).get("nutrients", [])
    #         calories = 0
    #
    #         for nutrient in nutrients:
    #             if nutrient.get("name", "").lower() == "calories":
    #                 calories = nutrient.get("amount", 0)
    #                 break
    #
    #         total_calories += calories
    #         lines.append(f"{name}: {int(calories)} ккал")
    #
    #     return "\n".join(lines) + f"\n\n🔢 Загалом: {int(total_calories)} ккал"
    def _format_summary(self, all_items: list) -> str:
        total_calories = 0
        total_protein = 0
        total_fat = 0
        total_carbs = 0
        lines = []

        for item in all_items:
            if isinstance(item, list) and len(item) == 1 and isinstance(item[0], dict):
                item = item[0]

            if not isinstance(item, dict):
                continue

            name = item.get("name", "невідомо")
            nutrients = item.get("nutrition", {}).get("nutrients", [])

            calories = protein = fat = carbs = 0

            for nutrient in nutrients:
                name_lower = nutrient.get("name", "").lower()
                amount = nutrient.get("amount", 0)

                if name_lower == "calories":
                    calories = amount
                elif name_lower == "protein":
                    protein = amount
                elif name_lower == "fat":
                    fat = amount
                elif name_lower == "carbohydrates":
                    carbs = amount

            total_calories += calories
            total_protein += protein
            total_fat += fat
            total_carbs += carbs

            lines.append(
                f"{name}:\n"
                f"  🔥 {int(calories)} ккал\n"
                f"  🥩 Б: {protein:.1f} г\n"
                f"  🧈 Ж: {fat:.1f} г\n"
                f"  🍞 В: {carbs:.1f} г"
            )

        summary = (
            "\n".join(lines) +
            f"\n\n🔢 Загалом:\n"
            f"🔥 Калорії: {int(total_calories)} ккал\n"
            f"🥩 Білки: {total_protein:.1f} г\n"
            f"🧈 Жири: {total_fat:.1f} г\n"
            f"🍞 Вуглеводи: {total_carbs:.1f} г"
        )
        return summary
