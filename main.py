"""大厨做菜 - 程序入口"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


def _fix_tcl_env() -> None:
    """修复部分环境下 Tcl/Tk 路径冲突导致 GUI 无法启动的问题"""
    if sys.platform != "win32":
        return
    prefix = Path(sys.base_prefix)
    tcl_dir = prefix / "tcl" / "tcl8.6"
    tk_dir = prefix / "tcl" / "tk8.6"
    if tcl_dir.is_dir() and tk_dir.is_dir():
        os.environ["TCL_LIBRARY"] = str(tcl_dir)
        os.environ["TK_LIBRARY"] = str(tk_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="大厨做菜")
    parser.add_argument("--desktop", action="store_true", help="启动桌面版 (Tkinter)")
    parser.add_argument("--port", type=int, default=5000, help="Web 版端口 (默认 5000)")
    args = parser.parse_args()

    if args.desktop:
        _fix_tcl_env()
        from app import run_app

        run_app()
    else:
        from web_app import run_web

        run_web(port=args.port)


if __name__ == "__main__":
    main()
