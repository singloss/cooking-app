(function () {
  "use strict";

  var LS_KEY = "chef_my_recipes_v1";
  var audioCtx = null;

  function unlockAudio() {
    try {
      if (!audioCtx) {
        audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      }
      if (audioCtx.state === "suspended") {
        audioCtx.resume();
      }
    } catch (e) { /* noop */ }
  }

  class StepTimer {
    constructor(el) {
      this.el = el;
      this.total = parseInt(el.dataset.seconds, 10) || 0;
      this.remaining = this.total;
      this.running = false;
      this.interval = null;
      this.endAt = 0;
      this.display = el.querySelector(".timer-display");
      this.btnStart = el.querySelector(".btn-start");
      this.btnPause = el.querySelector(".btn-pause");
      this.btnReset = el.querySelector(".btn-reset");
      this.customMin = el.querySelector(".timer-custom-min");
      this.btnApply = el.querySelector(".btn-apply-duration");
      this.render();
      this.btnStart?.addEventListener("click", () => this.start());
      this.btnPause?.addEventListener("click", () => this.pause());
      this.btnReset?.addEventListener("click", () => this.reset());
      this.btnApply?.addEventListener("click", () => this.applyCustomDuration());
    }

    applyCustomDuration() {
      if (!this.customMin) return;
      var minutes = parseInt(this.customMin.value, 10);
      if (!minutes || minutes <= 0) return;
      this.total = minutes * 60;
      this.remaining = this.total;
      this.el.dataset.seconds = String(this.total);
      if (this.btnStart) this.btnStart.disabled = false;
      this.render();
    }

    format(sec) {
      var m = Math.floor(sec / 60);
      var s = sec % 60;
      return String(m).padStart(2, "0") + ":" + String(s).padStart(2, "0");
    }

    render() {
      if (!this.display) return;
      this.display.textContent = this.format(this.remaining);
      this.display.classList.toggle("running", this.running);
      this.display.classList.toggle("done", !this.running && this.remaining === 0 && this.total > 0);
    }

    tick() {
      if (!this.running) return;
      this.remaining = Math.max(0, Math.ceil((this.endAt - Date.now()) / 1000));
      if (this.remaining <= 0) {
        this.remaining = 0;
        this.pause();
        this.display?.classList.add("done");
        this.playAlarm();
        return;
      }
      this.render();
    }

    start() {
      if (this.total <= 0) return;
      unlockAudio();
      if (this.remaining <= 0) this.remaining = this.total;
      this.endAt = Date.now() + this.remaining * 1000;
      this.running = true;
      this.render();
      clearInterval(this.interval);
      this.tick();
      this.interval = setInterval(() => this.tick(), 250);
      requestWakeLock();
    }

    pause() {
      this.running = false;
      clearInterval(this.interval);
      this.interval = null;
      this.render();
    }

    reset() {
      this.pause();
      this.remaining = this.total;
      this.display?.classList.remove("done");
      this.render();
    }

    playAlarm() {
      try {
        unlockAudio();
        if (audioCtx) {
          [0, 0.3, 0.6].forEach(function (delay) {
            var osc = audioCtx.createOscillator();
            var gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.frequency.value = 880;
            gain.gain.value = 0.3;
            osc.start(audioCtx.currentTime + delay);
            osc.stop(audioCtx.currentTime + delay + 0.15);
          });
        }
      } catch (e) { /* noop */ }
      if ("vibrate" in navigator) navigator.vibrate([200, 100, 200]);
    }
  }

  document.querySelectorAll(".step-timer").forEach(function (el) {
    new StepTimer(el);
  });

  function initStepTimers(root) {
    (root || document).querySelectorAll(".step-timer").forEach(function (el) {
      if (el.dataset.timerBound) return;
      el.dataset.timerBound = "1";
      new StepTimer(el);
    });
  }

  function getLocalRecipeById(id) {
    return readLocalRecipes().find(function (r) { return r.id === id; }) || null;
  }

  function readLocalRecipes() {
    try {
      var raw = localStorage.getItem(LS_KEY);
      if (!raw) return [];
      var data = JSON.parse(raw);
      return Array.isArray(data) ? data : [];
    } catch (e) {
      return [];
    }
  }

  function writeLocalRecipes(list) {
    try {
      localStorage.setItem(LS_KEY, JSON.stringify(list));
    } catch (e) { /* noop */ }
  }

  function upsertLocalRecipe(recipe) {
    if (!recipe || !recipe.id) return;
    var list = readLocalRecipes();
    var idx = list.findIndex(function (r) { return r.id === recipe.id; });
    if (idx >= 0) list[idx] = recipe;
    else list.push(recipe);
    writeLocalRecipes(list);
  }

  function removeLocalRecipe(id) {
    writeLocalRecipes(readLocalRecipes().filter(function (r) { return r.id !== id; }));
  }

  function syncRecipeToServer(recipe) {
    return fetch("/api/my-recipes/sync", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(recipe),
    }).then(function (res) { return res.json(); });
  }

  function backupRecipeFromPage() {
    var node = document.getElementById("recipe-backup");
    if (!node || !node.textContent) return;
    try {
      var recipe = JSON.parse(node.textContent);
      if (recipe && recipe.id) upsertLocalRecipe(recipe);
    } catch (e) { /* noop */ }
  }

  function restoreLocalRecipesToServer() {
    var node = document.getElementById("server-recipe-ids");
    if (!node) return;
    var serverIds = [];
    try {
      serverIds = JSON.parse(node.textContent || "[]");
    } catch (e) { /* noop */ }
    var local = readLocalRecipes();
    var missing = local.filter(function (r) {
      return r.id && serverIds.indexOf(r.id) === -1;
    });
    if (!missing.length) return;
    Promise.all(missing.map(syncRecipeToServer)).then(function () {
      if (missing.length) window.location.reload();
    });
  }

  function collectRecipeFromForm(form) {
    if (!form) return null;
    var id = form.dataset.recipeId;
    if (!id) return null;
    var nameEl = form.querySelector('[name="name"]');
    var descEl = form.querySelector('[name="description"]');
    var diffEl = form.querySelector('[name="difficulty"]');
    var prepEl = form.querySelector('[name="prep_time"]');
    var ingredients = [];
    form.querySelectorAll('[name="ingredient"]').forEach(function (el) {
      var v = el.value.trim();
      if (v) ingredients.push(v);
    });
    var steps = [];
    var descs = form.querySelectorAll('[name="step_desc"]');
    var durs = form.querySelectorAll('[name="step_dur"]');
    descs.forEach(function (el, i) {
      var desc = el.value.trim();
      if (!desc) return;
      var dur = 0;
      if (durs[i]) {
        dur = parseInt(durs[i].value, 10);
        if (isNaN(dur) || dur < 0) dur = 0;
      }
      steps.push({ order: steps.length + 1, description: desc, duration_minutes: dur });
    });
    return {
      id: id,
      name: nameEl ? nameEl.value.trim() : "",
      cuisine: "custom",
      description: descEl ? descEl.value.trim() : "",
      ingredients: ingredients.length ? ingredients : [""],
      steps: steps.length ? steps : [{ order: 1, description: "", duration_minutes: 5 }],
      difficulty: diffEl ? (diffEl.value || "中等") : "中等",
      prep_time: prepEl ? (prepEl.value || "30分钟") : "30分钟",
      is_custom: true,
    };
  }

  function bindEditFormLocalSave() {
    var form = document.getElementById("edit-recipe-form");
    if (!form) return;
    form.addEventListener("submit", function () {
      var recipe = collectRecipeFromForm(form);
      if (recipe && recipe.name) {
        upsertLocalRecipe(recipe);
        syncRecipeToServer(recipe);
      }
    });
  }

  function loadLocalRecipeIntoEditForm() {
    var form = document.getElementById("edit-recipe-form");
    if (!form) return;
    var id = form.dataset.recipeId;
    var localOnly = form.dataset.localOnly === "true";
    var local = id ? getLocalRecipeById(id) : null;
    if (!local) return;
    if (!localOnly && form.querySelector('[name="name"]')?.value.trim()) return;
    var setVal = function (sel, val) {
      var el = form.querySelector(sel);
      if (el) el.value = val || "";
    };
    setVal('[name="name"]', local.name);
    setVal('[name="description"]', local.description);
    setVal('[name="prep_time"]', local.prep_time);
    var diffEl = form.querySelector('[name="difficulty"]');
    if (diffEl && local.difficulty) diffEl.value = local.difficulty;
    var ingList = document.getElementById("ingredient-list");
    if (ingList && local.ingredients && local.ingredients.length) {
      ingList.innerHTML = "";
      local.ingredients.forEach(function (ing) {
        var row = document.createElement("div");
        row.className = "dynamic-row";
        row.innerHTML = '<input type="text" name="ingredient" class="form-input" placeholder="食材名称及用量">' +
          '<button type="button" class="btn-remove" aria-label="删除">✕</button>';
        row.querySelector("input").value = ing;
        ingList.appendChild(row);
      });
    }
    var stepList = document.getElementById("step-list");
    if (stepList && local.steps && local.steps.length) {
      stepList.innerHTML = "";
      local.steps.forEach(function (step) {
        var row = document.createElement("div");
        row.className = "dynamic-row-step";
        row.innerHTML = '<input type="text" name="step_desc" class="form-input" placeholder="步骤描述">' +
          '<div class="step-dur-row"><span class="form-label" style="margin:0">计时(分)</span>' +
          '<input type="number" name="step_dur" class="form-input dur-input" value="5" min="0">' +
          '<button type="button" class="btn-remove" aria-label="删除">✕</button></div>';
        row.querySelector('[name="step_desc"]').value = step.description || "";
        row.querySelector('[name="step_dur"]').value = step.duration_minutes || 0;
        stepList.appendChild(row);
      });
    }
    bindDynamicForms();
  }

  function stepTimerHtml(step) {
    var dur = step.duration_minutes || 0;
    if (dur > 0) {
      return '<div class="step-timer timer-block" data-seconds="' + (dur * 60) + '">' +
        '<span class="timer-hint">建议计时 ' + dur + ' 分钟</span>' +
        '<span class="timer-display">00:00</span>' +
        '<div class="timer-btns">' +
        '<button type="button" class="btn-timer btn-timer-primary btn-start">开始</button>' +
        '<button type="button" class="btn-timer btn-pause">暂停</button>' +
        '<button type="button" class="btn-timer btn-reset">重置</button></div></div>';
    }
    return '<div class="step-timer timer-block timer-custom" data-seconds="0">' +
      '<span class="timer-hint">未设置计时，输入分钟数后开始</span>' +
      '<div class="timer-custom-row">' +
      '<input type="number" class="form-input dur-input timer-custom-min" min="1" placeholder="分钟" inputmode="numeric">' +
      '<button type="button" class="btn-timer btn-timer-primary btn-apply-duration">设定</button></div>' +
      '<span class="timer-display">00:00</span>' +
      '<div class="timer-btns">' +
      '<button type="button" class="btn-timer btn-timer-primary btn-start" disabled>开始</button>' +
      '<button type="button" class="btn-timer btn-pause">暂停</button>' +
      '<button type="button" class="btn-timer btn-reset">重置</button></div></div>';
  }

  function mountLocalRecipeDetail() {
    var mount = document.getElementById("local-recipe-mount");
    if (!mount) return;
    var id = mount.dataset.recipeId;
    var recipe = getLocalRecipeById(id);
    if (!recipe) {
      mount.innerHTML = '<div class="empty-state"><div class="empty-icon">📝</div>' +
        '<div class="empty-title">菜谱未找到</div>' +
        '<div class="empty-desc">可能尚未保存到本机，请返回编辑后点「完成并退出」</div>' +
        '<a href="/my" class="btn btn-primary">返回我的菜谱</a></div>';
      return;
    }
    upsertLocalRecipe(recipe);
    var ingHtml = (recipe.ingredients || []).filter(function (i) { return i && i.trim(); })
      .map(function (i) { return "<li>" + i + "</li>"; }).join("");
    var stepsHtml = (recipe.steps || []).map(function (step) {
      return '<article class="step-card"><div class="step-header">' +
        '<span class="step-num">' + step.order + '</span>' +
        '<p class="step-desc">' + step.description + '</p></div>' +
        stepTimerHtml(step) + '</article>';
    }).join("");
    mount.innerHTML =
      '<div class="detail-header">' +
      '<div class="detail-hero-badge">🍽️</div>' +
      '<h1 class="detail-title">' + (recipe.name || "未命名") + '</h1>' +
      '<div class="detail-meta">' +
      '<span class="tag tag-accent">' + (recipe.difficulty || "中等") + '</span>' +
      '<span class="tag">⏱ ' + (recipe.prep_time || "30分钟") + '</span>' +
      '<span class="tag">我的菜谱</span><span class="tag">本机保存</span></div>' +
      (recipe.description ? '<p class="detail-desc">' + recipe.description + '</p>' : '') +
      '</div>' +
      '<section class="detail-section"><h2 class="section-title">食材清单</h2>' +
      '<ul class="ingredient-list">' + ingHtml + '</ul></section>' +
      '<section class="detail-section"><h2 class="section-title">制作步骤</h2>' + stepsHtml + '</section>' +
      '<div class="btn-row" style="margin-top:24px">' +
      '<a href="/my/' + recipe.id + '/edit" class="btn btn-outline btn-block">编辑菜谱</a></div>';
    initStepTimers(mount);
  }

  function createMyRecipeRow(recipe) {
    var wrap = document.createElement("div");
    wrap.className = "recipe-item my-recipe-item";
    wrap.dataset.recipeId = recipe.id;
    var stepCount = (recipe.steps && recipe.steps.length) || 0;
    var meta = (recipe.difficulty || "中等") + " · " + (recipe.prep_time || "30分钟") + " · " + stepCount + " 步";
    wrap.innerHTML =
      '<a href="/recipe/' + recipe.id + '?custom=1" class="recipe-item-link">' +
      '<div class="recipe-item-left"><div class="recipe-item-name"></div>' +
      '<div class="recipe-item-meta"></div></div><span class="recipe-item-arrow">›</span></a>' +
      '<div class="my-recipe-actions">' +
      '<a href="/my/' + recipe.id + '/edit" class="btn btn-sm btn-outline">编辑</a>' +
      '<form action="/my/' + recipe.id + '/delete" method="post">' +
      '<button type="submit" class="btn btn-sm btn-danger">删除</button></form></div>';
    wrap.querySelector(".recipe-item-name").textContent = recipe.name || "未命名";
    wrap.querySelector(".recipe-item-meta").textContent = meta;
    var delForm = wrap.querySelector("form");
    delForm.addEventListener("submit", function (e) {
      if (!confirm("确定删除「" + (recipe.name || "未命名") + "」？")) {
        e.preventDefault();
        return;
      }
      removeLocalRecipe(recipe.id);
    });
    return wrap;
  }

  function mergeLocalRecipesIntoList() {
    var list = document.getElementById("my-recipe-list");
    var empty = document.getElementById("my-recipe-empty");
    var idsNode = document.getElementById("server-recipe-ids");
    if (!list || !idsNode) return;
    var serverIds = [];
    try {
      serverIds = JSON.parse(idsNode.textContent || "[]");
    } catch (e) { /* noop */ }
    var added = 0;
    readLocalRecipes().forEach(function (recipe) {
      if (!recipe.id || serverIds.indexOf(recipe.id) >= 0) return;
      list.appendChild(createMyRecipeRow(recipe));
      serverIds.push(recipe.id);
      added += 1;
    });
    if (added > 0) {
      list.hidden = false;
      if (empty) empty.hidden = true;
      var countEl = document.querySelector(".section-link");
      if (countEl) countEl.textContent = list.querySelectorAll(".my-recipe-item").length + " 道";
    }
  }

  function bindDynamicForms() {
    function bindRemove(row, list, selector) {
      var btn = row.querySelector(".btn-remove");
      if (!btn) return;
      btn.addEventListener("click", function () {
        if (list.querySelectorAll(selector).length <= 1) return;
        row.remove();
      });
    }

    document.querySelectorAll("[data-add-ingredient]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var list = document.getElementById("ingredient-list");
        if (!list) return;
        var row = document.createElement("div");
        row.className = "dynamic-row";
        row.innerHTML = '<input type="text" name="ingredient" class="form-input" placeholder="食材名称及用量">' +
          '<button type="button" class="btn-remove" aria-label="删除">✕</button>';
        list.appendChild(row);
        bindRemove(row, list, ".dynamic-row");
      });
    });

    document.querySelectorAll("[data-add-step]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var list = document.getElementById("step-list");
        if (!list) return;
        var row = document.createElement("div");
        row.className = "dynamic-row-step";
        row.innerHTML = '<input type="text" name="step_desc" class="form-input" placeholder="步骤描述">' +
          '<div class="step-dur-row"><span class="form-label" style="margin:0">计时(分)</span>' +
          '<input type="number" name="step_dur" class="form-input dur-input" value="5" min="0">' +
          '<button type="button" class="btn-remove" aria-label="删除">✕</button></div>';
        list.appendChild(row);
        bindRemove(row, list, ".dynamic-row-step");
      });
    });

    var ingList = document.getElementById("ingredient-list");
    if (ingList) {
      ingList.querySelectorAll(".dynamic-row").forEach(function (row) {
        bindRemove(row, ingList, ".dynamic-row");
      });
    }
    var stepList = document.getElementById("step-list");
    if (stepList) {
      stepList.querySelectorAll(".dynamic-row-step").forEach(function (row) {
        bindRemove(row, stepList, ".dynamic-row-step");
      });
    }
  }

  function bindMyRecipeDelete() {
    document.querySelectorAll(".my-recipe-item form").forEach(function (form) {
      form.addEventListener("submit", function () {
        var id = form.closest(".my-recipe-item")?.dataset.recipeId;
        if (id) removeLocalRecipe(id);
      });
    });
  }

  bindDynamicForms();
  bindEditFormLocalSave();
  bindMyRecipeDelete();
  backupRecipeFromPage();
  loadLocalRecipeIntoEditForm();
  mountLocalRecipeDetail();
  restoreLocalRecipesToServer();
  mergeLocalRecipesIntoList();

  document.querySelectorAll(".flash").forEach(function (el) {
    setTimeout(function () {
      el.style.transition = "opacity 0.3s";
      el.style.opacity = "0";
      setTimeout(function () { el.remove(); }, 300);
    }, 3000);
  });

  var wakeLock = null;

  async function requestWakeLock() {
    if (!("wakeLock" in navigator)) return;
    try {
      wakeLock = await navigator.wakeLock.request("screen");
    } catch (e) { /* noop */ }
  }

  async function releaseWakeLock() {
    if (wakeLock) {
      try { await wakeLock.release(); } catch (e) { /* noop */ }
      wakeLock = null;
    }
  }

  document.addEventListener("visibilitychange", function () {
    if (document.visibilityState === "visible") {
      document.querySelectorAll(".step-timer").forEach(function (el) {
        if (el.querySelector(".timer-display.running")) requestWakeLock();
      });
    } else {
      releaseWakeLock();
    }
  });
})();
