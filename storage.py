"""我的菜谱持久化存储"""
from __future__ import annotations

import json
import uuid
from pathlib import Path

from models import Recipe, Step

DATA_DIR = Path(__file__).parent / "data"
MY_RECIPES_FILE = DATA_DIR / "my_recipes.json"


def _ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def _load_raw() -> list[dict]:
    _ensure_data_dir()
    if not MY_RECIPES_FILE.exists():
        return []
    try:
        with open(MY_RECIPES_FILE, encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, OSError):
        pass
    return []


def _save_raw(recipes: list[dict]) -> None:
    _ensure_data_dir()
    with open(MY_RECIPES_FILE, "w", encoding="utf-8") as f:
        json.dump(recipes, f, ensure_ascii=False, indent=2)


def load_my_recipes() -> list[Recipe]:
    return [Recipe.from_dict(item) for item in _load_raw()]


def save_my_recipe(recipe: Recipe) -> Recipe:
    recipes = _load_raw()
    recipe.is_custom = True
    payload = recipe.to_dict()

    for i, item in enumerate(recipes):
        if item.get("id") == recipe.id:
            recipes[i] = payload
            _save_raw(recipes)
            return recipe

    recipes.append(payload)
    _save_raw(recipes)
    return recipe


def delete_my_recipe(recipe_id: str) -> bool:
    recipes = _load_raw()
    new_recipes = [r for r in recipes if r.get("id") != recipe_id]
    if len(new_recipes) == len(recipes):
        return False
    _save_raw(new_recipes)
    return True


def create_empty_recipe(name: str = "新菜谱", cuisine: str = "custom") -> Recipe:
    return Recipe(
        id=f"custom_{uuid.uuid4().hex[:8]}",
        name=name,
        cuisine=cuisine,
        description="",
        ingredients=[""],
        steps=[Step(order=1, description="", duration_minutes=0)],
        difficulty="中等",
        prep_time="30分钟",
        is_custom=True,
    )


def get_my_recipe_by_id(recipe_id: str) -> Recipe | None:
    for recipe in load_my_recipes():
        if recipe.id == recipe_id:
            return recipe
    return None
