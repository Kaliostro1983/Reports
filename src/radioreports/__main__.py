# -*- coding: utf-8 -*-
from __future__ import annotations
import argparse
import importlib


def _call(module_relpath: str, func: str = "main") -> int:
    """Імпортує потрібний модуль тільки під обрану команду та викликає main()."""
    mod = importlib.import_module(module_relpath, __package__)
    rv = getattr(mod, func)()
    return 0 if rv is None else int(rv)  # дозволяємо main() повертати None


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="radioreports")
    sub = p.add_subparsers(dest="command")
    sub.add_parser("daily", help="Щоденний звіт")
    sub.add_parser("weekly", help="Тижневий звіт")
    sub.add_parser("audit", help="Аудит логів")
    sub.add_parser("active63", help="Звіт «Активні мережі (63)» старого типу")
    sub.add_parser("activity63", help="Аналіз активності по днях (63)")
    sub.add_parser("live_frequency", help="Alias на activity63 (для BAT)")
    return p


def main() -> int:
    args = build_parser().parse_args()
    cmd = args.command
    if cmd == "daily":
        return _call(".daily_report")
    elif cmd == "weekly":
        return _call(".weekly_report")
    elif cmd == "audit":
        return _call(".audit_report")
    elif cmd == "active63":
        return _call(".active_networks_63")
    elif cmd in ("activity63", "live_frequency"):
        return _call(".reports.networks_activity_63")
    else:
        print("Команди: daily | weekly | audit | active63 | activity63 | live_frequency")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
