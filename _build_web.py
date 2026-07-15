from pathlib import Path
ROOT = Path(r"C:\Users\siginloss\cooking_app")
(ROOT / "templates").mkdir(exist_ok=True)
(ROOT / "static/css").mkdir(parents=True, exist_ok=True)
(ROOT / "static/js").mkdir(parents=True, exist_ok=True)

files = {}

files["web_app.py"] = r'''"""大厨做菜 - 响应式 Web 应用"""
from __future__ import annotations
import socket
from pathlib import Path
from flask import Flask, flash, redirect, render_template, request, url_for
from database import BUILTIN_RECIPES, get_cuisine_by_id, get_cuisines_by_region, get_recipe_by_id, get_recipes_by_cuisine, search_recipes
from storage import create_empty_recipe, delete_my_recipe, get_my_recipe_by_id, load_my_recipes, save_my_recipe

APP_DIR = Path(__file__).parent
app = Flask(__name__, template_folder=str(APP_DIR / "templates"), static_folder=str(APP_DIR / "static"))
app.secret_key = "chef-cooking-app-local"

@app.context_processor
def inject_globals():
    return {"active_tab": request.endpoint}

@app.route("/")
def home():
    return render_template("home.html", recipe_count=len(BUILTIN_RECIPES))

@app.route("/recipes")
def recipes():
    q = request.args.get("q", "").strip()
    results = search_recipes(q) if q else []
    return render_template("recipes.html", domestic=get_cuisines_by_region("国内"), foreign=get_cuisines_by_region("国外"), q=q, results=results)

@app.route("/recipes/<cuisine_id>")
def cuisine_detail(cuisine_id):
    cuisine = get_cuisine_by_id(cuisine_id)
    if not cuisine:
        flash("菜系不存在", "error")
        return redirect(url_for("recipes"))
    return render_template("cuisine.html", cuisine=cuisine, recipes=get_recipes_by_cuisine(cuisine_id))

@app.route("/recipe/<recipe_id>")
def recipe_detail(recipe_id):
    is_custom = request.args.get("custom") == "1"
    recipe = get_my_recipe_by_id(recipe_id) if is_custom else get_recipe_by_id(recipe_id)
    if not recipe:
        recipe = get_recipe_by_id(recipe_id)
    if not recipe:
        flash("菜谱未找到", "error")
        return redirect(url_for("recipes"))
    return render_template("detail.html", recipe=recipe, cuisine=get_cuisine_by_id(recipe.cuisine), is_custom=is_custom or recipe.is_custom)

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
        save_my_recipe(recipe)
        return redirect(url_for("my_recipe_edit", recipe_id=recipe.id))
    return render_template("my_edit.html", recipe=None)

@app.route("/my/<recipe_id>/edit", methods=["GET", "POST"])
def my_recipe_edit(recipe_id):
    recipe = get_my_recipe_by_id(recipe_id)
    if not recipe:
        flash("菜谱不存在", "error")
        return redirect(url_for("my_recipes"))
    if request.method == "POST":
        from models import Step
        name = request.form.get("name", "").strip()
        if not name:
            flash("请填写菜名", "error")
            return render_template("my_edit.html", recipe=recipe)
        ingredients = [x.strip() for x in request.form.getlist("ingredient") if x.strip()]
        descriptions = request.form.getlist("step_desc")
        durations = request.form.getlist("step_dur")
        if not ingredients:
            flash("请至少添加一项食材", "error")
            return render_template("my_edit.html", recipe=recipe)
        steps = []
        for i, desc in enumerate(descriptions, start=1):
            desc = desc.strip()
            if not desc:
                continue
            try:
                dur = max(0, int(durations[i - 1] or 0))
            except (ValueError, IndexError):
                dur = 0
            steps.append(Step(order=len(steps) + 1, description=desc, duration_minutes=dur))
        if not steps:
            flash("请至少添加一个步骤", "error")
            return render_template("my_edit.html", recipe=recipe)
        recipe.name = name
        recipe.description = request.form.get("description", "").strip()
        recipe.difficulty = request.form.get("difficulty", "中等").strip() or "中等"
        recipe.prep_time = request.form.get("prep_time", "30分钟").strip() or "30分钟"
        recipe.ingredients = ingredients
        recipe.steps = steps
        save_my_recipe(recipe)
        flash("菜谱已保存", "success")
        return redirect(url_for("my_recipes"))
    return render_template("my_edit.html", recipe=recipe)

@app.route("/my/<recipe_id>/delete", methods=["POST"])
def my_recipe_delete(recipe_id):
    delete_my_recipe(recipe_id)
    flash("已删除", "success")
    return redirect(url_for("my_recipes"))

def _local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"

def run_web(host="0.0.0.0", port=5000, debug=False):
    ip = _local_ip()
    print("\n  大厨做菜 Web 版已启动")
    print(f"  电脑: http://127.0.0.1:{port}")
    print(f"  手机: http://{ip}:{port}  (同一 WiFi)\n")
    app.run(host=host, port=port, debug=debug, use_reloader=False)
'''

for name, content in files.items():
    (ROOT / name).write_text(content, encoding="utf-8")
print("web_app ok")
