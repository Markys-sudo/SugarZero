import json
import os
import asyncio
from typing import Optional

CACHE_FILE = "nutrition_cache.json"

class NutritionCache:
    def __init__(self):
        self.cache = {}
        self.lock = asyncio.Lock()

        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    self.cache = json.load(f)
            except json.JSONDecodeError:
                self.cache = {}

    async def get(self, ingredient: str) -> Optional[dict]:
        key = ingredient.strip().lower()
        async with self.lock:
            return self.cache.get(key)

    async def set(self, ingredient: str, response: dict):
        key = ingredient.strip().lower()
        async with self.lock:
            self.cache[key] = response
            try:
                with open(CACHE_FILE, "w", encoding="utf-8") as f:
                    json.dump(self.cache, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"❌ Помилка при записі кешу: {e}")
