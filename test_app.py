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


class TestWebRecipeFlow(unittest.TestCase):
    def setUp(self) -> None:
        self._tmpdir = tempfile.TemporaryDirectory()
        storage.MY_RECIPES_FILE = Path(self._tmpdir.name) / "my_recipes.json"
        storage.DATA_DIR = Path(self._tmpdir.name)
        self.client = __import__("web_app", fromlist=["app"]).app.test_client()

    def tearDown(self) -> None:
        storage.MY_RECIPES_FILE = Path(__file__).parent / "data" / "my_recipes.json"
        storage.DATA_DIR = Path(__file__).parent / "data"
        self._tmpdir.cleanup()

    def test_validation_keeps_form_data(self) -> None:
        from web_app import _parse_steps

        steps = _parse_steps(["步骤1", ""], ["10", "5"])
        self.assertEqual(len(steps), 1)
        self.assertEqual(steps[0].duration_minutes, 10)

        r = self.client.post("/my/new", data={"name": "保留测试"}, follow_redirects=False)
        rid = r.headers["Location"].split("/")[-2]
        r2 = self.client.post(
            f"/my/{rid}/edit",
            data={
                "name": "保留测试",
                "description": "简介内容",
                "difficulty": "简单",
                "prep_time": "20分钟",
                "ingredient": "",
                "step_desc": "切菜",
                "step_dur": "5",
            },
        )
        self.assertIn("请至少添加一项食材", r2.data.decode("utf-8"))
        self.assertIn("简介内容", r2.data.decode("utf-8"))

    def test_save_redirects_to_detail_with_timer(self) -> None:
        r = self.client.post("/my/new", data={"name": "计时测试"}, follow_redirects=False)
        rid = r.headers["Location"].split("/")[-2]
        r2 = self.client.post(
            f"/my/{rid}/edit",
            data={
                "name": "计时测试",
                "description": "",
                "difficulty": "中等",
                "prep_time": "30分钟",
                "ingredient": "鸡蛋2个",
                "step_desc": "水煮",
                "step_dur": "8",
            },
            follow_redirects=False,
        )
        self.assertIn(f"/recipe/{rid}?custom=1", r2.headers["Location"])
        r3 = self.client.get(f"/recipe/{rid}?custom=1")
        html = r3.data.decode("utf-8")
        self.assertIn("step-timer", html)
        self.assertIn('data-seconds="480"', html)


    def test_api_sync_recipe(self) -> None:
        recipe = storage.create_empty_recipe("同步测试")
        recipe.ingredients = ["盐"]
        recipe.steps = [Step(1, "煮", 5)]
        payload = recipe.to_dict()
        r = self.client.post("/api/my-recipes/sync", json=payload)
        self.assertEqual(r.status_code, 200)
        self.assertTrue(r.get_json()["ok"])
        loaded = storage.get_my_recipe_by_id(recipe.id)
        self.assertIsNotNone(loaded)
        assert loaded is not None
        self.assertEqual(loaded.name, "同步测试")


class TestTimerLogic(unittest.TestCase):
    def test_format_time(self) -> None:
        from timer_widget import format_time

        self.assertEqual(format_time(125), "02:05")
        self.assertEqual(format_time(0), "00:00")
        self.assertEqual(format_time(3661), "61:01")


if __name__ == "__main__":
    unittest.main()
