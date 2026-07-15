"""大厨做菜 - 主界面程序"""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, simpledialog, ttk

from database import (
    get_cuisine_by_id,
    get_cuisines_by_region,
    get_recipe_by_id,
    get_recipes_by_cuisine,
)
from models import CuisineInfo, Recipe, Step
from storage import (
    create_empty_recipe,
    delete_my_recipe,
    get_my_recipe_by_id,
    load_my_recipes,
    save_my_recipe,
)
from timer_widget import CookingTimer

COLORS = {
    "bg": "#FFFFFF",
    "primary": "#111827",
    "primary_dark": "#374151",
    "secondary": "#F9FAFB",
    "card": "#FFFFFF",
    "text": "#111827",
    "text_light": "#6B7280",
    "accent": "#111827",
    "success": "#059669",
    "border": "#E5E7EB",
}


class ScrollableFrame(ttk.Frame):
    """可滚动容器"""

    def __init__(self, master: tk.Misc, **kwargs):
        super().__init__(master, **kwargs)
        self._canvas = tk.Canvas(self, highlightthickness=0, bg=COLORS["bg"])
        scrollbar = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self._canvas.yview)
        self.inner = ttk.Frame(self._canvas)

        self.inner.bind(
            "<Configure>",
            lambda e: self._canvas.configure(scrollregion=self._canvas.bbox("all")),
        )
        self._canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self._canvas.configure(yscrollcommand=scrollbar.set)

        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self._mousewheel_handler = self._on_mousewheel
        self._canvas.bind("<Enter>", self._bind_mousewheel)
        self._canvas.bind("<Leave>", self._unbind_mousewheel)

    def _on_mousewheel(self, event: tk.Event) -> None:
        self._canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _bind_mousewheel(self, _event: tk.Event) -> None:
        self._canvas.bind_all("<MouseWheel>", self._mousewheel_handler)

    def _unbind_mousewheel(self, _event: tk.Event) -> None:
        self._canvas.unbind_all("<MouseWheel>")


class CookingApp(tk.Tk):
    """大厨做菜主窗口"""

    def __init__(self) -> None:
        super().__init__()
        self.title("大厨做菜")
        self.geometry("960x680")
        self.minsize(800, 600)
        self.configure(bg=COLORS["bg"])

        self._setup_styles()
        self.container = ttk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        self.frames: dict[str, ttk.Frame] = {}
        for FrameClass in (
            HomeFrame,
            RecipeBrowserFrame,
            CuisineListFrame,
            RecipeDetailFrame,
            MyRecipesFrame,
            RecipeEditorFrame,
        ):
            frame = FrameClass(self.container, self)
            self.frames[FrameClass.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomeFrame")

    def _setup_styles(self) -> None:
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(".", background=COLORS["bg"], foreground=COLORS["text"], font=("Microsoft YaHei UI", 10))
        style.configure("TFrame", background=COLORS["bg"])
        style.configure("Card.TFrame", background=COLORS["card"])
        style.configure("Title.TLabel", font=("Microsoft YaHei UI", 24, "bold"), foreground=COLORS["primary"], background=COLORS["bg"])
        style.configure("Subtitle.TLabel", font=("Microsoft YaHei UI", 12), foreground=COLORS["text_light"], background=COLORS["bg"])
        style.configure("Heading.TLabel", font=("Microsoft YaHei UI", 16, "bold"), foreground=COLORS["text"], background=COLORS["bg"])
        style.configure("Primary.TButton", font=("Microsoft YaHei UI", 12, "bold"), padding=12)
        style.configure("Nav.TButton", font=("Microsoft YaHei UI", 10), padding=8)
        style.map("Primary.TButton", background=[("active", COLORS["primary_dark"])])

    def show_frame(self, name: str, **kwargs) -> None:
        frame = self.frames[name]
        frame.tkraise()
        if hasattr(frame, "on_show"):
            frame.on_show(**kwargs)


class BaseFrame(ttk.Frame):
    """页面基类"""

    def __init__(self, master: tk.Misc, app: CookingApp):
        super().__init__(master)
        self.app = app

    def on_show(self, **kwargs) -> None:
        pass


class HomeFrame(BaseFrame):
    """主页：菜谱 / 我的菜谱"""

    def __init__(self, master: tk.Misc, app: CookingApp):
        super().__init__(master, app)
        self.configure(style="TFrame")

        wrapper = ttk.Frame(self)
        wrapper.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(wrapper, text="大厨做菜", style="Title.TLabel").pack(pady=(0, 8))
        ttk.Label(wrapper, text="探索中外美食，记录你的拿手好菜", style="Subtitle.TLabel").pack(pady=(0, 40))

        btn_frame = ttk.Frame(wrapper)
        btn_frame.pack()

        tk.Button(
            btn_frame,
            text="📖 菜谱\n\n浏览中外各大菜系",
            font=("Microsoft YaHei UI", 14, "bold"),
            bg=COLORS["primary"],
            fg="white",
            activebackground=COLORS["primary_dark"],
            activeforeground="white",
            width=16,
            height=5,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: app.show_frame("RecipeBrowserFrame"),
        ).grid(row=0, column=0, padx=20)

        tk.Button(
            btn_frame,
            text="📝 我的菜谱\n\n记录与珍藏私房菜",
            font=("Microsoft YaHei UI", 14, "bold"),
            bg=COLORS["success"],
            fg="white",
            activebackground="#1B4332",
            activeforeground="white",
            width=16,
            height=5,
            relief=tk.FLAT,
            cursor="hand2",
            command=lambda: app.show_frame("MyRecipesFrame"),
        ).grid(row=0, column=1, padx=20)


class RecipeBrowserFrame(BaseFrame):
    """菜谱浏览：国内 / 国外菜系"""

    def __init__(self, master: tk.Misc, app: CookingApp):
        super().__init__(master, app)
        self.scroll = ScrollableFrame(self)
        self.scroll.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)
        self.content = self.scroll.inner

    def on_show(self, **kwargs) -> None:
        for widget in self.content.winfo_children():
            widget.destroy()

        header = ttk.Frame(self.content)
        header.pack(fill=tk.X, pady=(0, 16))
        ttk.Button(header, text="← 返回", style="Nav.TButton", command=lambda: self.app.show_frame("HomeFrame")).pack(side=tk.LEFT)
        ttk.Label(header, text="菜谱库", style="Heading.TLabel").pack(side=tk.LEFT, padx=16)

        for region in ("国内", "国外"):
            cuisines = get_cuisines_by_region(region)
            if not cuisines:
                continue
            ttk.Label(self.content, text=f"【{region}菜系】", font=("Microsoft YaHei UI", 14, "bold")).pack(anchor=tk.W, pady=(12, 8))
            grid = ttk.Frame(self.content)
            grid.pack(fill=tk.X, pady=(0, 8))

            for i, cuisine in enumerate(cuisines):
                self._create_cuisine_card(grid, cuisine, i)

    def _create_cuisine_card(self, parent: ttk.Frame, cuisine: CuisineInfo, index: int) -> None:
        row, col = divmod(index, 3)
        card = tk.Frame(parent, bg=COLORS["card"], highlightbackground=COLORS["border"], highlightthickness=1, cursor="hand2")
        card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        parent.columnconfigure(col, weight=1)

        inner = tk.Frame(card, bg=COLORS["card"], padx=16, pady=16)
        inner.pack(fill=tk.BOTH, expand=True)

        tk.Label(inner, text=cuisine.emoji, font=("Segoe UI Emoji", 28), bg=COLORS["card"]).pack(anchor=tk.W)
        tk.Label(inner, text=cuisine.name, font=("Microsoft YaHei UI", 13, "bold"), bg=COLORS["card"], fg=COLORS["text"]).pack(anchor=tk.W, pady=(4, 2))
        tk.Label(inner, text=cuisine.description, font=("Microsoft YaHei UI", 9), bg=COLORS["card"], fg=COLORS["text_light"], wraplength=200, justify=tk.LEFT).pack(anchor=tk.W)

        def click(_event=None, cid=cuisine.id):
            self.app.show_frame("CuisineListFrame", cuisine_id=cid)

        card.bind("<Button-1>", click)
        for child in inner.winfo_children():
            child.bind("<Button-1>", click)


class CuisineListFrame(BaseFrame):
    """某菜系下的菜谱列表"""

    def __init__(self, master: tk.Misc, app: CookingApp):
        super().__init__(master, app)
        self.scroll = ScrollableFrame(self)
        self.scroll.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)
        self.content = self.scroll.inner
        self.cuisine_id = ""

    def on_show(self, cuisine_id: str = "", **kwargs) -> None:
        self.cuisine_id = cuisine_id
        for widget in self.content.winfo_children():
            widget.destroy()

        cuisine = get_cuisine_by_id(cuisine_id)
        recipes = get_recipes_by_cuisine(cuisine_id)

        header = ttk.Frame(self.content)
        header.pack(fill=tk.X, pady=(0, 16))
        ttk.Button(header, text="← 返回菜系", style="Nav.TButton", command=lambda: self.app.show_frame("RecipeBrowserFrame")).pack(side=tk.LEFT)
        title = f"{cuisine.emoji} {cuisine.name}" if cuisine else "菜谱列表"
        ttk.Label(header, text=title, style="Heading.TLabel").pack(side=tk.LEFT, padx=16)

        if not recipes:
            ttk.Label(self.content, text="暂无菜谱", style="Subtitle.TLabel").pack(pady=40)
            return

        for recipe in recipes:
            self._create_recipe_row(recipe)

    def _create_recipe_row(self, recipe: Recipe) -> None:
        row = tk.Frame(self.content, bg=COLORS["card"], highlightbackground=COLORS["border"], highlightthickness=1, cursor="hand2")
        row.pack(fill=tk.X, pady=6, padx=4)

        inner = tk.Frame(row, bg=COLORS["card"], padx=16, pady=12)
        inner.pack(fill=tk.X)

        tk.Label(inner, text=recipe.name, font=("Microsoft YaHei UI", 13, "bold"), bg=COLORS["card"], fg=COLORS["text"]).pack(side=tk.LEFT)
        tk.Label(inner, text=f"  {recipe.difficulty} · {recipe.prep_time}", font=("Microsoft YaHei UI", 9), bg=COLORS["card"], fg=COLORS["text_light"]).pack(side=tk.LEFT)
        tk.Label(inner, text="查看详情 →", font=("Microsoft YaHei UI", 9), bg=COLORS["card"], fg=COLORS["primary"]).pack(side=tk.RIGHT)

        def click(_event=None, rid=recipe.id):
            self.app.show_frame("RecipeDetailFrame", recipe_id=rid, is_custom=False)

        row.bind("<Button-1>", click)
        for child in inner.winfo_children():
            child.bind("<Button-1>", click)


class RecipeDetailFrame(BaseFrame):
    """菜谱详情：食材、步骤、计时器"""

    def __init__(self, master: tk.Misc, app: CookingApp):
        super().__init__(master, app)
        self.scroll = ScrollableFrame(self)
        self.scroll.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)
        self.content = self.scroll.inner
        self.timers: list[CookingTimer] = []

    def on_show(self, recipe_id: str = "", is_custom: bool = False, **kwargs) -> None:
        for timer in self.timers:
            timer.destroy()
        self.timers.clear()

        for widget in self.content.winfo_children():
            widget.destroy()

        recipe = get_my_recipe_by_id(recipe_id) if is_custom else get_recipe_by_id(recipe_id)
        if not recipe:
            recipe = get_recipe_by_id(recipe_id)
        if not recipe:
            ttk.Label(self.content, text="菜谱未找到").pack()
            return

        back_target = "MyRecipesFrame" if recipe.is_custom else "CuisineListFrame"
        back_kwargs = {} if recipe.is_custom else {"cuisine_id": recipe.cuisine}

        header = ttk.Frame(self.content)
        header.pack(fill=tk.X, pady=(0, 12))
        ttk.Button(
            header,
            text="← 返回",
            style="Nav.TButton",
            command=lambda: self.app.show_frame(back_target, **back_kwargs),
        ).pack(side=tk.LEFT)

        ttk.Label(self.content, text=recipe.name, style="Heading.TLabel").pack(anchor=tk.W)
        ttk.Label(self.content, text=f"{recipe.difficulty} · {recipe.prep_time}", style="Subtitle.TLabel").pack(anchor=tk.W, pady=(0, 8))

        if recipe.description:
            tk.Label(
                self.content,
                text=recipe.description,
                font=("Microsoft YaHei UI", 10),
                bg=COLORS["bg"],
                fg=COLORS["text"],
                wraplength=800,
                justify=tk.LEFT,
            ).pack(anchor=tk.W, pady=(0, 12))

        ttk.Label(self.content, text="食材", font=("Microsoft YaHei UI", 12, "bold")).pack(anchor=tk.W, pady=(8, 4))
        for ing in recipe.ingredients:
            if ing.strip():
                ttk.Label(self.content, text=f"  • {ing}").pack(anchor=tk.W)

        ttk.Label(self.content, text="制作步骤", font=("Microsoft YaHei UI", 12, "bold")).pack(anchor=tk.W, pady=(16, 8))
        for step in recipe.steps:
            self._render_step(step)

    def _render_step(self, step: Step) -> None:
        frame = tk.Frame(self.content, bg=COLORS["card"], highlightbackground=COLORS["border"], highlightthickness=1)
        frame.pack(fill=tk.X, pady=6, padx=4)

        inner = tk.Frame(frame, bg=COLORS["card"], padx=12, pady=10)
        inner.pack(fill=tk.X)

        tk.Label(inner, text=f"步骤 {step.order}", font=("Microsoft YaHei UI", 10, "bold"), bg=COLORS["card"], fg=COLORS["primary"]).pack(anchor=tk.W)
        tk.Label(inner, text=step.description, font=("Microsoft YaHei UI", 10), bg=COLORS["card"], fg=COLORS["text"], wraplength=780, justify=tk.LEFT).pack(anchor=tk.W, pady=(4, 6))

        if step.duration_minutes > 0:
            timer_row = tk.Frame(inner, bg=COLORS["card"])
            timer_row.pack(anchor=tk.W, fill=tk.X)
            tk.Label(timer_row, text=f"建议计时 {step.duration_minutes} 分钟", font=("Microsoft YaHei UI", 9), bg=COLORS["card"], fg=COLORS["text_light"]).pack(side=tk.LEFT, padx=(0, 12))
            timer = CookingTimer(timer_row, duration_minutes=step.duration_minutes)
            timer.pack(side=tk.LEFT)
            self.timers.append(timer)


class MyRecipesFrame(BaseFrame):
    """我的菜谱列表"""

    def __init__(self, master: tk.Misc, app: CookingApp):
        super().__init__(master, app)
        self.scroll = ScrollableFrame(self)
        self.scroll.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)
        self.content = self.scroll.inner

    def on_show(self, **kwargs) -> None:
        for widget in self.content.winfo_children():
            widget.destroy()

        header = ttk.Frame(self.content)
        header.pack(fill=tk.X, pady=(0, 16))
        ttk.Button(header, text="← 返回", style="Nav.TButton", command=lambda: self.app.show_frame("HomeFrame")).pack(side=tk.LEFT)
        ttk.Label(header, text="我的菜谱", style="Heading.TLabel").pack(side=tk.LEFT, padx=16)
        ttk.Button(header, text="+ 新建菜谱", style="Nav.TButton", command=self._create_new).pack(side=tk.RIGHT)

        recipes = load_my_recipes()
        if not recipes:
            ttk.Label(self.content, text="还没有菜谱，点击「新建菜谱」开始记录吧", style="Subtitle.TLabel").pack(pady=40)
            return

        for recipe in recipes:
            self._create_row(recipe)

    def _create_row(self, recipe: Recipe) -> None:
        row = tk.Frame(self.content, bg=COLORS["card"], highlightbackground=COLORS["border"], highlightthickness=1)
        row.pack(fill=tk.X, pady=6, padx=4)

        inner = tk.Frame(row, bg=COLORS["card"], padx=16, pady=12)
        inner.pack(fill=tk.X)

        name_label = tk.Label(inner, text=recipe.name, font=("Microsoft YaHei UI", 13, "bold"), bg=COLORS["card"], fg=COLORS["text"], cursor="hand2")
        name_label.pack(side=tk.LEFT)
        tk.Label(inner, text=f"  {recipe.difficulty} · {recipe.prep_time}", font=("Microsoft YaHei UI", 9), bg=COLORS["card"], fg=COLORS["text_light"]).pack(side=tk.LEFT)

        btn_frame = tk.Frame(inner, bg=COLORS["card"])
        btn_frame.pack(side=tk.RIGHT)

        ttk.Button(btn_frame, text="查看", style="Nav.TButton", command=lambda r=recipe: self.app.show_frame("RecipeDetailFrame", recipe_id=r.id, is_custom=True)).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="编辑", style="Nav.TButton", command=lambda r=recipe: self.app.show_frame("RecipeEditorFrame", recipe_id=r.id)).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="删除", style="Nav.TButton", command=lambda r=recipe: self._delete(r)).pack(side=tk.LEFT, padx=2)

        name_label.bind("<Button-1>", lambda _e, r=recipe: self.app.show_frame("RecipeDetailFrame", recipe_id=r.id, is_custom=True))

    def _create_new(self) -> None:
        name = simpledialog.askstring("新建菜谱", "请输入菜名", parent=self)
        if not name or not name.strip():
            return
        recipe = create_empty_recipe(name.strip())
        save_my_recipe(recipe)
        self.app.show_frame("RecipeEditorFrame", recipe_id=recipe.id)

    def _delete(self, recipe: Recipe) -> None:
        if messagebox.askyesno("确认删除", f"确定要删除「{recipe.name}」吗？", parent=self):
            delete_my_recipe(recipe.id)
            self.on_show()


class RecipeEditorFrame(BaseFrame):
    """编辑我的菜谱"""

    def __init__(self, master: tk.Misc, app: CookingApp):
        super().__init__(master, app)
        self.recipe: Recipe | None = None
        self.scroll = ScrollableFrame(self)
        self.scroll.pack(fill=tk.BOTH, expand=True, padx=24, pady=16)
        self.content = self.scroll.inner

        self.name_var = tk.StringVar()
        self.desc_var = tk.StringVar()
        self.difficulty_var = tk.StringVar(value="中等")
        self.prep_var = tk.StringVar(value="30分钟")
        self.ingredient_entries: list[tk.Entry] = []
        self.step_widgets: list[dict] = []

    def on_show(self, recipe_id: str = "", **kwargs) -> None:
        self.recipe = get_my_recipe_by_id(recipe_id)
        if not self.recipe:
            messagebox.showerror("错误", "菜谱不存在", parent=self)
            self.app.show_frame("MyRecipesFrame")
            return
        self._build_form()

    def _clear_form(self) -> None:
        for widget in self.content.winfo_children():
            widget.destroy()
        self.ingredient_entries.clear()
        self.step_widgets.clear()

    def _build_form(self) -> None:
        assert self.recipe is not None
        self._clear_form()

        header = ttk.Frame(self.content)
        header.pack(fill=tk.X, pady=(0, 12))
        ttk.Button(header, text="← 返回", style="Nav.TButton", command=lambda: self.app.show_frame("MyRecipesFrame")).pack(side=tk.LEFT)
        ttk.Label(header, text="编辑菜谱", style="Heading.TLabel").pack(side=tk.LEFT, padx=16)
        ttk.Button(header, text="保存", style="Nav.TButton", command=self._save).pack(side=tk.RIGHT)

        form = ttk.Frame(self.content)
        form.pack(fill=tk.X)

        self.name_var.set(self.recipe.name)
        self.desc_var.set(self.recipe.description)
        self.difficulty_var.set(self.recipe.difficulty)
        self.prep_var.set(self.recipe.prep_time)

        self._add_field(form, "菜名", self.name_var)
        self._add_field(form, "简介", self.desc_var)
        self._add_field(form, "难度", self.difficulty_var)
        self._add_field(form, "准备时间", self.prep_var)

        ttk.Label(form, text="食材（每行一项）", font=("Microsoft YaHei UI", 11, "bold")).pack(anchor=tk.W, pady=(12, 4))
        ing_frame = ttk.Frame(form)
        ing_frame.pack(fill=tk.X)
        for ing in self.recipe.ingredients:
            self._add_ingredient_row(ing_frame, ing)
        ttk.Button(ing_frame, text="+ 添加食材", command=lambda: self._add_ingredient_row(ing_frame, "")).pack(anchor=tk.W, pady=4)

        ttk.Label(form, text="步骤", font=("Microsoft YaHei UI", 11, "bold")).pack(anchor=tk.W, pady=(12, 4))
        steps_frame = ttk.Frame(form)
        steps_frame.pack(fill=tk.X)
        for step in self.recipe.steps:
            self._add_step_row(steps_frame, step.description, step.duration_minutes)
        ttk.Button(steps_frame, text="+ 添加步骤", command=lambda: self._add_step_row(steps_frame, "", 0)).pack(anchor=tk.W, pady=4)

    def _add_field(self, parent: ttk.Frame, label: str, var: tk.StringVar) -> None:
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=4)
        ttk.Label(row, text=label, width=8).pack(side=tk.LEFT)
        ttk.Entry(row, textvariable=var).pack(side=tk.LEFT, fill=tk.X, expand=True)

    def _add_ingredient_row(self, parent: ttk.Frame, value: str) -> None:
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=2)
        entry = ttk.Entry(row)
        entry.insert(0, value)
        entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.ingredient_entries.append(entry)
        ttk.Button(row, text="✕", width=3, command=lambda: self._remove_row(row, entry, self.ingredient_entries)).pack(side=tk.LEFT, padx=4)

    def _add_step_row(self, parent: ttk.Frame, desc: str, duration: int) -> None:
        row = ttk.Frame(parent)
        row.pack(fill=tk.X, pady=4)
        desc_entry = ttk.Entry(row)
        desc_entry.insert(0, desc)
        desc_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Label(row, text="分钟").pack(side=tk.LEFT, padx=(8, 2))
        dur_var = tk.StringVar(value=str(duration))
        ttk.Entry(row, textvariable=dur_var, width=6).pack(side=tk.LEFT)
        widget_info = {"row": row, "desc": desc_entry, "dur": dur_var}
        self.step_widgets.append(widget_info)
        ttk.Button(row, text="✕", width=3, command=lambda: self._remove_step(widget_info)).pack(side=tk.LEFT, padx=4)

    def _remove_row(self, row: ttk.Frame, entry: tk.Entry, collection: list) -> None:
        if entry in collection:
            collection.remove(entry)
        row.destroy()

    def _remove_step(self, info: dict) -> None:
        if info in self.step_widgets:
            self.step_widgets.remove(info)
        info["row"].destroy()

    def _save(self) -> None:
        if not self.recipe:
            return

        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("提示", "请填写菜名", parent=self)
            return

        ingredients = [e.get().strip() for e in self.ingredient_entries if e.get().strip()]
        if not ingredients:
            messagebox.showwarning("提示", "请至少添加一项食材", parent=self)
            return

        steps: list[Step] = []
        for i, info in enumerate(self.step_widgets, start=1):
            desc = info["desc"].get().strip()
            if not desc:
                continue
            try:
                duration = max(0, int(info["dur"].get() or 0))
            except ValueError:
                duration = 0
            steps.append(Step(order=i, description=desc, duration_minutes=duration))

        if not steps:
            messagebox.showwarning("提示", "请至少添加一个步骤", parent=self)
            return

        self.recipe.name = name
        self.recipe.description = self.desc_var.get().strip()
        self.recipe.difficulty = self.difficulty_var.get().strip() or "中等"
        self.recipe.prep_time = self.prep_var.get().strip() or "30分钟"
        self.recipe.ingredients = ingredients
        self.recipe.steps = steps

        save_my_recipe(self.recipe)
        messagebox.showinfo("成功", "菜谱已保存", parent=self)
        self.app.show_frame("MyRecipesFrame")


def run_app() -> None:
    app = CookingApp()
    app.mainloop()
