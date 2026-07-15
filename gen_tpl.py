from pathlib import Path

T = Path(__file__).parent / "templates"

TEMPLATES = {
    "recipes.html": """{% extends "base.html" %}
{% block title %}菜谱库 - 大厨做菜{% endblock %}
{% block top_right %}{% if q %}<span class="top-action">{{ results|length }} 个结果</span>{% endif %}{% endblock %}
{% block content %}
<form class="search-bar" action="{{ url_for('recipes') }}" method="get">
  <span class="search-icon">🔍</span>
  <input type="search" name="q" value="{{ q }}" placeholder="搜索菜名、食材、描述…" autocomplete="off">
</form>
{% if q %}
<div class="section-header"><h2 class="section-title">搜索结果</h2></div>
{% if results %}
<div class="recipe-list">
{% for recipe in results %}
<a href="{{ url_for('recipe_detail', recipe_id=recipe.id) }}" class="recipe-item">
  <div class="recipe-item-left">
    <div class="recipe-item-name">{{ recipe.name }}</div>
    <div class="recipe-item-meta">{{ recipe.difficulty }} · {{ recipe.prep_time }}</div>
  </div>
  <span class="recipe-item-arrow">›</span>
</a>
{% endfor %}
</div>
{% else %}
<div class="empty-state">
  <div class="empty-icon">🔎</div>
  <div class="empty-title">未找到相关菜谱</div>
  <div class="empty-desc">试试其他关键词，如「豆腐」「意面」</div>
</div>
{% endif %}
{% else %}
<p class="region-label">国内菜系</p>
<div class="cuisine-grid">
{% for cuisine in domestic %}
<a href="{{ url_for('cuisine_detail', cuisine_id=cuisine.id) }}" class="cuisine-card">
  <span class="cuisine-emoji">{{ cuisine.emoji }}</span>
  <span class="cuisine-name">{{ cuisine.name }}</span>
  <span class="cuisine-desc">{{ cuisine.description }}</span>
  <span class="cuisine-count">{{ cuisine_recipe_count(cuisine.id) }} 道菜</span>
</a>
{% endfor %}
</div>
<p class="region-label">国外菜系</p>
<div class="cuisine-grid">
{% for cuisine in foreign %}
<a href="{{ url_for('cuisine_detail', cuisine_id=cuisine.id) }}" class="cuisine-card">
  <span class="cuisine-emoji">{{ cuisine.emoji }}</span>
  <span class="cuisine-name">{{ cuisine.name }}</span>
  <span class="cuisine-desc">{{ cuisine.description }}</span>
  <span class="cuisine-count">{{ cuisine_recipe_count(cuisine.id) }} 道菜</span>
</a>
{% endfor %}
</div>
{% endif %}
{% endblock %}
""",
    "cuisine.html": """{% extends "base.html" %}
{% block title %}{{ cuisine.name }} - 大厨做菜{% endblock %}
{% block top_left %}<a href="{{ url_for('recipes') }}" class="back-link">‹ 菜系</a>{% endblock %}
{% block top_right %}<span class="top-action">{{ recipes|length }} 道</span>{% endblock %}
{% block content %}
<div class="cuisine-hero">
  <span class="cuisine-hero-emoji">{{ cuisine.emoji }}</span>
  <h1 class="detail-title">{{ cuisine.name }}</h1>
  <p class="detail-desc">{{ cuisine.description }}</p>
  <div class="detail-meta">
    <span class="tag">{{ cuisine.region }}</span>
    <span class="tag tag-accent">{{ recipes|length }} 道菜谱</span>
  </div>
</div>
{% if recipes %}
<div class="recipe-list">
{% for recipe in recipes %}
<a href="{{ url_for('recipe_detail', recipe_id=recipe.id) }}" class="recipe-item">
  <div class="recipe-item-left">
    <div class="recipe-item-name">{{ recipe.name }}</div>
    <div class="recipe-item-meta">{{ recipe.difficulty }} · {{ recipe.prep_time }} · {{ recipe.steps|length }} 步</div>
  </div>
  <span class="recipe-item-arrow">›</span>
</a>
{% endfor %}
</div>
{% else %}
<div class="empty-state"><div class="empty-icon">{{ cuisine.emoji }}</div><div class="empty-title">暂无菜谱</div></div>
{% endif %}
{% endblock %}
""",
    "detail.html": """{% extends "base.html" %}
{% block title %}{{ recipe.name }} - 大厨做菜{% endblock %}
{% block top_left %}<a href="{{ back_url }}" class="back-link">‹ 返回</a>{% endblock %}
{% block content %}
<div class="detail-header">
  <div class="detail-hero-badge">{% if cuisine %}{{ cuisine.emoji }}{% else %}🍽️{% endif %}</div>
  <h1 class="detail-title">{{ recipe.name }}</h1>
  <div class="detail-meta">
    <span class="tag tag-accent">{{ recipe.difficulty }}</span>
    <span class="tag">⏱ {{ recipe.prep_time }}</span>
    <span class="tag">{{ recipe.steps|length }} 个步骤</span>
    {% if cuisine %}<span class="tag">{{ cuisine.name }}</span>{% endif %}
    {% if is_custom %}<span class="tag">我的菜谱</span>{% endif %}
  </div>
  {% if recipe.description %}<p class="detail-desc">{{ recipe.description }}</p>{% endif %}
</div>
<section class="detail-section">
  <h2 class="section-title">食材清单</h2>
  <ul class="ingredient-list">
  {% for ing in recipe.ingredients %}{% if ing.strip() %}<li>{{ ing }}</li>{% endif %}{% endfor %}
  </ul>
</section>
<section class="detail-section">
  <h2 class="section-title">制作步骤</h2>
  {% for step in recipe.steps %}
  <article class="step-card">
    <div class="step-header">
      <span class="step-num">{{ step.order }}</span>
      <p class="step-desc">{{ step.description }}</p>
    </div>
    {% if step.duration_minutes > 0 %}
    <div class="step-timer timer-block" data-seconds="{{ step.duration_minutes * 60 }}">
      <span class="timer-hint">建议计时 {{ step.duration_minutes }} 分钟</span>
      <span class="timer-display">00:00</span>
      <div class="timer-btns">
        <button type="button" class="btn-timer btn-timer-primary btn-start">开始</button>
        <button type="button" class="btn-timer btn-pause">暂停</button>
        <button type="button" class="btn-timer btn-reset">重置</button>
      </div>
    </div>
    {% endif %}
  </article>
  {% endfor %}
</section>
{% if is_custom %}
<div class="btn-row" style="margin-top:24px">
  <a href="{{ url_for('my_recipe_edit', recipe_id=recipe.id) }}" class="btn btn-outline btn-block">编辑菜谱</a>
</div>
{% endif %}
{% endblock %}
""",
    "my_list.html": """{% extends "base.html" %}
{% block title %}我的菜谱 - 大厨做菜{% endblock %}
{% block top_right %}<a href="{{ url_for('my_recipe_new') }}" class="top-action">+ 新建</a>{% endblock %}
{% block content %}
<div class="section-header">
  <h2 class="section-title">我的菜谱</h2>
  <span class="section-link">{{ recipes|length }} 道</span>
</div>
{% if recipes %}
<div class="recipe-list">
{% for recipe in recipes %}
<div class="recipe-item my-recipe-item">
  <a href="{{ url_for('recipe_detail', recipe_id=recipe.id, custom=1) }}" class="recipe-item-link">
    <div class="recipe-item-left">
      <div class="recipe-item-name">{{ recipe.name }}</div>
      <div class="recipe-item-meta">{{ recipe.difficulty }} · {{ recipe.prep_time }} · {{ recipe.steps|length }} 步</div>
    </div>
    <span class="recipe-item-arrow">›</span>
  </a>
  <div class="my-recipe-actions">
    <a href="{{ url_for('my_recipe_edit', recipe_id=recipe.id) }}" class="btn btn-sm btn-outline">编辑</a>
    <form action="{{ url_for('my_recipe_delete', recipe_id=recipe.id) }}" method="post" onsubmit="return confirm('确定删除「{{ recipe.name }}」？')">
      <button type="submit" class="btn btn-sm btn-danger">删除</button>
    </form>
  </div>
</div>
{% endfor %}
</div>
{% else %}
<div class="empty-state">
  <div class="empty-icon">📝</div>
  <div class="empty-title">还没有菜谱</div>
  <div class="empty-desc">记录你的拿手好菜，随时查看制作步骤</div>
  <a href="{{ url_for('my_recipe_new') }}" class="btn btn-primary">+ 新建菜谱</a>
</div>
{% endif %}
{% endblock %}
""",
    "my_edit.html": """{% extends "base.html" %}
{% block title %}{% if recipe %}编辑{% else %}新建{% endif %}菜谱 - 大厨做菜{% endblock %}
{% block top_left %}<a href="{{ url_for('my_recipes') }}" class="back-link">‹ 返回</a>{% endblock %}
{% block content %}
<h1 class="detail-title" style="margin-bottom:20px">{% if recipe %}编辑{% else %}新建{% endif %}菜谱</h1>
{% if recipe %}
<form method="post" class="edit-form">
  <div class="form-group">
    <label class="form-label">菜名 *</label>
    <input type="text" name="name" class="form-input" value="{{ recipe.name }}" required placeholder="例如：红烧肉">
  </div>
  <div class="form-group">
    <label class="form-label">简介</label>
    <textarea name="description" class="form-textarea" placeholder="简单描述这道菜的特点">{{ recipe.description }}</textarea>
  </div>
  <div class="form-row-2">
    <div class="form-group">
      <label class="form-label">难度</label>
      <select name="difficulty" class="form-select">
        {% for d in ['简单', '中等', '困难'] %}
        <option value="{{ d }}" {% if recipe.difficulty == d %}selected{% endif %}>{{ d }}</option>
        {% endfor %}
      </select>
    </div>
    <div class="form-group">
      <label class="form-label">准备时间</label>
      <input type="text" name="prep_time" class="form-input" value="{{ recipe.prep_time }}" placeholder="30分钟">
    </div>
  </div>
  <div class="form-group">
    <label class="form-label">食材 *</label>
    <div id="ingredient-list">
    {% for ing in recipe.ingredients %}
      <div class="dynamic-row">
        <input type="text" name="ingredient" class="form-input" value="{{ ing }}" placeholder="食材名称及用量">
        <button type="button" class="btn-remove" aria-label="删除">✕</button>
      </div>
    {% endfor %}
    </div>
    <button type="button" class="btn-add-row" data-add-ingredient>+ 添加食材</button>
  </div>
  <div class="form-group">
    <label class="form-label">步骤 *</label>
    <div id="step-list">
    {% for step in recipe.steps %}
      <div class="dynamic-row-step">
        <input type="text" name="step_desc" class="form-input" value="{{ step.description }}" placeholder="步骤描述">
        <div class="step-dur-row">
          <span class="form-label" style="margin:0">计时(分)</span>
          <input type="number" name="step_dur" class="form-input dur-input" value="{{ step.duration_minutes }}" min="0">
          <button type="button" class="btn-remove" aria-label="删除">✕</button>
        </div>
      </div>
    {% endfor %}
    </div>
    <button type="button" class="btn-add-row" data-add-step>+ 添加步骤</button>
  </div>
  <button type="submit" class="btn btn-primary btn-block">保存菜谱</button>
</form>
{% else %}
<form method="post" class="edit-form">
  <div class="form-group">
    <label class="form-label">菜名 *</label>
    <input type="text" name="name" class="form-input" required placeholder="给你的菜谱起个名字">
  </div>
  <button type="submit" class="btn btn-primary btn-block">创建并继续编辑</button>
</form>
{% endif %}
{% endblock %}
""",
}

if __name__ == "__main__":
    for name, content in TEMPLATES.items():
        (T / name).write_text(content, encoding="utf-8")
    print(f"wrote {len(TEMPLATES)} templates")
