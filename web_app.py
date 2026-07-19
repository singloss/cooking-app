"""大厨做菜 - 响应式 Web 应用"""
from __future__ import annotations

import os
import random
import socket
from pathlib import Path

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from database import (
    BUILTIN_RECIPES,
    CUISINES,
    get_cuisine_by_id,
    get_cuisines_by_region,
    get_recipe_by_id,
    get_recipes_by_cuisine,
    search_recipes,
)
from models import Recipe, Step
from storage import (
    StorageError,
    create_empty_recipe,
    delete_my_recipe,
    get_my_recipe_by_id,
    load_my_recipes,
    save_my_recipe,
)


def _parse_steps(descriptions: list[str], durations: list[str]) -> list[Step]:
    """按行配对步骤描述与计时，避免错位"""
    steps: list[Step] = []
    for desc, dur_str in zip(descriptions, durations):
        desc = desc.strip()
        if not desc:
            continue
        try:
            duration = max(0, int(str(dur_str).strip() or 0))
        except ValueError:
            duration = 0
        steps.append(Step(order=len(steps) + 1, description=desc, duration_minutes=duration))
    return steps


def _recipe_from_form(recipe: Recipe, form) -> Recipe:
    """用表单内容更新菜谱草稿（校验失败时回填表单）"""
    recipe.name = form.get("name", "").strip()
    recipe.description = form.get("description", "").strip()
    recipe.difficulty = form.get("difficulty", "中等").strip() or "中等"
    recipe.prep_time = form.get("prep_time", "30分钟").strip() or "30分钟"
    recipe.ingredients = [x.strip() for x in form.getlist("ingredient") if x.strip()]
    if not recipe.ingredients:
        recipe.ingredients = [""]
    recipe.steps = _parse_steps(form.getlist("step_desc"), form.getlist("step_dur"))
    if not recipe.steps:
        recipe.steps = [Step(order=1, description="", duration_minutes=5)]
    return recipe

APP_DIR = Path(__file__).parent
app = Flask(
    __name__,
    template_folder=str(APP_DIR / "templates"),
    static_folder=str(APP_DIR / "static"),
)
app.secret_key = os.environ.get("SECRET_KEY", "chef-cooking-app-local")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.context_processor
def inject_globals():
    endpoint = request.endpoint or ""
    if endpoint == "home":
        tab = "home"
    elif endpoint in ("recipes", "cuisine_detail", "recipe_detail"):
        tab = "recipes"
    elif endpoint in ("my_recipes", "my_recipe_new", "my_recipe_edit"):
        tab = "my"
    else:
        tab = "home"

    hide_nav = endpoint in ("my_recipe_edit", "my_recipe_new", "recipe_detail")

    def cuisine_recipe_count(cuisine_id: str) -> int:
        return len(get_recipes_by_cuisine(cuisine_id))

    return {
        "active_tab": tab,
        "hide_nav": hide_nav,
        "recipe_count": len(BUILTIN_RECIPES),
        "cuisine_count": len(CUISINES),
        "cuisine_recipe_count": cuisine_recipe_count,
    }


def _featured_recipes(limit: int = 12) -> list[dict]:
    pool = BUILTIN_RECIPES.copy()
    random.shuffle(pool)
    featured = []
    for recipe in pool[:limit]:
        cuisine = get_cuisine_by_id(recipe.cuisine)
        featured.append({"recipe": recipe, "emoji": cuisine.emoji if cuisine else "🍽️"})
    return featured


@app.route("/")
def home():
    return render_template(
        "home.html",
        recipe_count=len(BUILTIN_RECIPES),
        cuisine_count=len(CUISINES),
        featured=_featured_recipes(12),
    )


@app.route("/recipes")
def recipes():
    q = request.args.get("q", "").strip()
    difficulty = request.args.get("difficulty", "").strip()
    results = search_recipes(q, difficulty=difficulty) if q else []
    return render_template(
        "recipes.html",
        domestic=get_cuisines_by_region("国内"),
        foreign=get_cuisines_by_region("国外"),
        q=q,
        difficulty=difficulty,
        results=results,
    )


@app.route("/recipes/<cuisine_id>")
def cuisine_detail(cuisine_id):
    cuisine = get_cuisine_by_id(cuisine_id)
    if not cuisine:
        flash("菜系不存在", "error")
        return redirect(url_for("recipes"))
    return render_template(
        "cuisine.html",
        cuisine=cuisine,
        recipes=get_recipes_by_cuisine(cuisine_id),
    )


@app.route("/recipe/<recipe_id>")
def recipe_detail(recipe_id):
    is_custom = request.args.get("custom") == "1"
    recipe = get_my_recipe_by_id(recipe_id) if is_custom else get_recipe_by_id(recipe_id)
    if not recipe:
        recipe = get_recipe_by_id(recipe_id)
    if not recipe and is_custom:
        return render_template(
            "detail.html",
            recipe=None,
            local_recipe_id=recipe_id,
            cuisine=None,
            is_custom=True,
            back_url=url_for("my_recipes"),
        )
    if not recipe:
        flash("菜谱未找到", "error")
        return redirect(url_for("recipes"))
    back_url = url_for("my_recipes") if (is_custom or recipe.is_custom) else url_for(
        "cuisine_detail", cuisine_id=recipe.cuisine
    )
    return render_template(
        "detail.html",
        recipe=recipe,
        local_recipe_id=None,
        cuisine=get_cuisine_by_id(recipe.cuisine),
        is_custom=is_custom or recipe.is_custom,
        back_url=back_url,
    )


@app.route("/my")
def my_recipes():
    return render_template("my_list.html", recipes=load_my_recipes())


@app.route("/my/new", methods=["GET", "POST"])
def my_recipe_new():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        if not name:
            flash("请填写菜名", "error")
            return render_template("my_edit.html", recipe=None)
        recipe = create_empty_recipe(name)
        try:
            save_my_recipe(recipe)
        except StorageError:
            flash("云端暂不可用，请编辑后点「完成并退出」保存到本机", "error")
        return redirect(url_for("my_recipe_edit", recipe_id=recipe.id))
    return render_template("my_edit.html", recipe=None)


@app.post("/api/my-recipes/sync")
def api_sync_recipe():
    data = request.get_json(silent=True)
    if not data or not data.get("id"):
        return jsonify({"ok": False, "error": "invalid recipe"}), 400
    try:
        recipe = Recipe.from_dict(data)
        recipe.is_custom = True
        save_my_recipe(recipe)
        return jsonify({"ok": True})
    except (StorageError, KeyError, TypeError, ValueError) as exc:
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.route("/my/<recipe_id>/edit", methods=["GET", "POST"])
def my_recipe_edit(recipe_id):
    recipe = get_my_recipe_by_id(recipe_id)
    local_only = False
    if not recipe:
        recipe = create_empty_recipe("未命名")
        recipe.id = recipe_id
        local_only = True
    if request.method == "POST":
        local_only = get_my_recipe_by_id(recipe_id) is None
        draft = _recipe_from_form(recipe, request.form)
        if not draft.name:
            flash("请填写菜名", "error")
            return render_template("my_edit.html", recipe=draft, local_only=local_only)
        ingredients = [x.strip() for x in request.form.getlist("ingredient") if x.strip()]
        steps = _parse_steps(request.form.getlist("step_desc"), request.form.getlist("step_dur"))
        if not ingredients:
            flash("请至少添加一项食材", "error")
            return render_template("my_edit.html", recipe=draft, local_only=local_only)
        if not steps:
            flash("请至少添加一个步骤", "error")
            return render_template("my_edit.html", recipe=draft, local_only=local_only)
        draft.ingredients = ingredients
        draft.steps = steps
        action = request.form.get("action", "save")
        try:
            save_my_recipe(draft)
            flash("菜谱已保存", "success")
            local_only = False
        except StorageError:
            flash("已保存到本机，云端暂不可用", "success" if action == "done" else "error")
            if action != "done":
                return render_template("my_edit.html", recipe=draft, local_only=True)
        if action == "done":
            return redirect(url_for("my_recipes"))
        return redirect(url_for("recipe_detail", recipe_id=draft.id, custom=1))
    return render_template("my_edit.html", recipe=recipe, local_only=local_only)


@app.route("/my/<recipe_id>/delete", methods=["POST"])
def my_recipe_delete(recipe_id):
    delete_my_recipe(recipe_id)
    flash("已删除", "success")
    return redirect(url_for("my_recipes"))


def _local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"


def run_web(host: str = "0.0.0.0", port: int = 5000, debug: bool = False) -> None:
    ip = _local_ip()
    print("\n  ═══════════════════════════════════")
    print("  大厨做菜 · Web 版")
    print("  ═══════════════════════════════════")
    print(f"  电脑访问: http://127.0.0.1:{port}")
    print(f"  手机访问: http://{ip}:{port}")
    print("  (手机需与电脑连接同一 WiFi)\n")
    app.run(host=host, port=port, debug=debug, use_reloader=False)
