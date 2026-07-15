"""单元测试"""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

# 确保项目根目录在 path 中
sys.path.insert(0, str(Path(__file__).parent))

from models import Recipe, Step
import database
import storage


class TestModels(unittest.TestCase):
    def test_step_roundtrip(self) -> None:
        step = Step(order=1, description="切菜", duration_minutes=5)
        restored = Step.from_dict(step.to_dict())
        self.assertEqual(restored.description, "切菜")
        self.assertEqual(restored.duration_minutes, 5)

    def test_recipe_roundtrip(self) -> None:
        recipe = Recipe(
            id="test",
            name="测试菜",
            cuisine="sichuan",
            description="描述",
            ingredients=["食材1"],
            steps=[Step(1, "步骤1", 3)],
            is_custom=True,
        )
        restored = Recipe.from_dict(recipe.to_dict())
        self.assertEqual(restored.name, "测试菜")
        self.assertEqual(len(restored.steps), 1)


class TestDatabase(unittest.TestCase):
    def test_cuisines_have_regions(self) -> None:
        cuisines = database.get_cuisines()
        self.assertGreaterEqual(len(cuisines), 10)
        regions = {c.region for c in cuisines}
        self.assertIn("国内", regions)
        self.assertIn("国外", regions)

    def test_recipes_per_cuisine(self) -> None:
        for cuisine in database.get_cuisines():
            recipes = database.get_recipes_by_cuisine(cuisine.id)
            self.assertGreater(len(recipes), 0, f"{cuisine.name} 应有至少一道菜")

    def test_get_recipe_by_id(self) -> None:
        recipe = database.get_recipe_by_id("mapo_tofu")
        self.assertIsNotNone(recipe)
        assert recipe is not None
        self.assertEqual(recipe.name, "麻婆豆腐")

    def test_all_recipes_valid(self) -> None:
        for recipe in database.BUILTIN_RECIPES:
            self.assertTrue(recipe.name)
            self.assertTrue(recipe.ingredients)
            self.assertTrue(recipe.steps)
            for step in recipe.steps:
                self.assertTrue(step.description)


class TestStorage(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        self._orig_file = storage.MY_RECIPES_FILE
        storage.MY_RECIPES_FILE = Path(self._tmpdir.name) / "my_recipes.json"
        storage.DATA_DIR = Path(self._tmpdir.name)

    def tearDown(self) -> None:
        storage.MY_RECIPES_FILE = self._orig_file
        storage.DATA_DIR = self._orig_file.parent
        self._tmpdir.cleanup()

    def test_save_and_load(self) -> None:
        recipe = storage.create_empty_recipe("我的红烧肉")
        recipe.ingredients = ["五花肉 500g", "冰糖 适量"]
        recipe.steps = [Step(1, "焯水", 10), Step(2, "炖煮", 60)]
        storage.save_my_recipe(recipe)

        loaded = storage.load_my_recipes()
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].name, "我的红烧肉")
        self.assertEqual(len(loaded[0].steps), 2)

    def test_update_recipe(self) -> None:
        recipe = storage.create_empty_recipe("旧名字")
        storage.save_my_recipe(recipe)
        recipe.name = "新名字"
        storage.save_my_recipe(recipe)
        loaded = storage.load_my_recipes()
        self.assertEqual(loaded[0].name, "新名字")
        self.assertEqual(len(loaded), 1)

    def test_delete_recipe(self) -> None:
        recipe = storage.create_empty_recipe("待删除")
        storage.save_my_recipe(recipe)
        self.assertTrue(storage.delete_my_recipe(recipe.id))
        self.assertEqual(len(storage.load_my_recipes()), 0)
        self.assertFalse(storage.delete_my_recipe("nonexistent"))

    def test_corrupted_json_returns_empty(self) -> None:
        storage.MY_RECIPES_FILE.write_text("{bad json", encoding="utf-8")
        self.assertEqual(storage.load_my_recipes(), [])


class TestTimerLogic(unittest.TestCase):
    def test_format_time(self) -> None:
        from timer_widget import format_time

        self.assertEqual(format_time(125), "02:05")
        self.assertEqual(format_time(0), "00:00")
        self.assertEqual(format_time(3661), "61:01")


if __name__ == "__main__":
    unittest.main()
