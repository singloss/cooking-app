"""烹饪计时器组件"""
from __future__ import annotations

import sys
import tkinter as tk
from tkinter import ttk


def format_time(seconds: int) -> str:
    """将秒数格式化为 MM:SS"""
    minutes, secs = divmod(max(0, seconds), 60)
    return f"{minutes:02d}:{secs:02d}"


def play_alarm() -> None:
    """计时结束提示音（跨平台）"""
    if sys.platform == "win32":
        try:
            import winsound

            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            return
        except Exception:
            pass
    print("\a", end="", flush=True)


class CookingTimer(ttk.Frame):
    """可启动/暂停/重置的倒计时计时器"""

    def __init__(self, master: tk.Misc, duration_minutes: int = 0, **kwargs):
        super().__init__(master, **kwargs)
        self.total_seconds = max(0, duration_minutes * 60)
        self.remaining = self.total_seconds
        self._running = False
        self._after_id: str | None = None

        self.time_var = tk.StringVar(value=format_time(self.remaining))
        self.status_var = tk.StringVar(value="就绪")

        ttk.Label(self, textvariable=self.time_var, font=("Microsoft YaHei UI", 14, "bold")).pack(side=tk.LEFT, padx=(0, 8))
        ttk.Button(self, text="开始", width=6, command=self.start).pack(side=tk.LEFT, padx=2)
        ttk.Button(self, text="暂停", width=6, command=self.pause).pack(side=tk.LEFT, padx=2)
        ttk.Button(self, text="重置", width=6, command=self.reset).pack(side=tk.LEFT, padx=2)
        ttk.Label(self, textvariable=self.status_var, foreground="#666").pack(side=tk.LEFT, padx=8)

    def _tick(self) -> None:
        if not self._running:
            return
        if self.remaining <= 0:
            self._running = False
            self.status_var.set("时间到！")
            self._play_alarm()
            return
        self.remaining -= 1
        self.time_var.set(format_time(self.remaining))
        self._after_id = self.after(1000, self._tick)

    def _play_alarm(self) -> None:
        play_alarm()
        try:
            self.bell()
        except Exception:
            pass

    def start(self) -> None:
        if self.total_seconds <= 0:
            self.status_var.set("无需计时")
            return
        if self.remaining <= 0:
            self.remaining = self.total_seconds
        self._running = True
        self.status_var.set("计时中...")
        if self._after_id:
            self.after_cancel(self._after_id)
        self._tick()

    def pause(self) -> None:
        self._running = False
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
        self.status_var.set("已暂停")

    def reset(self) -> None:
        self.pause()
        self.remaining = self.total_seconds
        self.time_var.set(format_time(self.remaining))
        self.status_var.set("就绪")

    def destroy(self) -> None:
        self.pause()
        super().destroy()
