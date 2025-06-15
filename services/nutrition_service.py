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
        results = {}

        for ingredient in ingredient_list:
            cached = await self.cache.get(ingredient)
            if cached:
                logger.info(f"[{user_id}] [Nutrition] ✅ З кешу: {ingredient}")
                results[ingredient] = cached
            else:
                logger.info(f"[{user_id}] [Nutrition] ⚠️ Кеш не знайдено: {ingredient}")
                item = await self._fetch_from_api(ingredient, user_id)
                if isinstance(item, dict):
                    await self.cache.set(ingredient, item)
                    logger.info(f"[{user_id}] [Nutrition] 📥 Додано в кеш: {ingredient}")
                    results[ingredient] = item
                elif isinstance(item, str):
                    logger.warning(f"[{user_id}] [Nutrition] ❌ API error for '{ingredient}': {item}")
                    return item

        summary = self._format_summary(results, ingredient_list)
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

    def _format_summary(self, results: dict, ingredient_order: list) -> str:
        total_calories = total_protein = total_fat = total_carbs = 0
        lines = []

        for ingredient in ingredient_order:
            item = results.get(ingredient)
            if not isinstance(item, dict):
                continue

            name = item.get("name", ingredient)
            nutrients = item.get("nutrition", {}).get("nutrients", [])

            # За замовчуванням
            calories = protein = fat = carbs = 0
            cal_unit = prot_unit = fat_unit = carb_unit = ""

            for nutrient in nutrients:
                name_lower = nutrient.get("name", "").lower()
                amount = nutrient.get("amount", 0)
                unit = nutrient.get("unit", "")

                if name_lower == "calories":
                    calories = amount
                    cal_unit = unit
                elif name_lower == "protein":
                    protein = amount
                    prot_unit = unit
                elif name_lower == "fat":
                    fat = amount
                    fat_unit = unit
                elif name_lower == "carbohydrates":
                    carbs = amount
                    carb_unit = unit

            total_calories += calories
            total_protein += protein
            total_fat += fat
            total_carbs += carbs

            lines.append(
                f"{name}:\n"
                f"  🔥 {int(calories)} {cal_unit}\n"
                f"  🥩 Б: {protein:.1f} {prot_unit}\n"
                f"  🧈 Ж: {fat:.1f} {fat_unit}\n"
                f"  🍞 В: {carbs:.1f} {carb_unit}"
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
