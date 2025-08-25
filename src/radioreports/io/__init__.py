# src/radioreports/__main__.py
from __future__ import annotations

import argparse
import importlib
import sys
from typing import Callable, Dict, Tuple

# Команда -> (module_path, callable_name)
# Додаємо зручні синоніми, щоб не ламати звички
COMMANDS: Dict[str, Tuple[str, str]] = {
    # щоденний звіт
    "daily": (".daily_report", "main"),
    "daily_report": (".daily_report", "main"),
    # тижневий (залишаємо як є)
    "weekly": (".weekly_report", "main"),
    "weekly_report": (".weekly_report", "main"),
    # аудит
    "audit": (".audit_report", "main"),
    "audit_report": (".audit_report", "main"),
    # активні мережі (63 омсбр)
    "active63": (".reports.active_networks_63", "main"),
    "active_networks": (".reports.active_networks_63", "main"),
    # активність по днях (63 омсбр)
    "activity63": (".reports.networks_activity_63", "main"),
    "activity_by_day": (".reports.networks_activity_63", "main"),
    # короткий синонім для live_frequency
    "live_frequency": (".live_frequency", "main"),
    "live": (".live_frequency", "main"),
}


def _call(module_relpath: str, func: str = "main") -> int:
    """Імпортує модуль відносно пакета і викликає функцію. Повертає код виходу."""
    mod = importlib.import_module(module_relpath, __package__)
    callable_obj: Callable[..., int | None] = getattr(mod, func)
    rc = callable_obj()
    # Захист від None/не-int
    try:
        return int(rc) if rc is not None else 0
    except Exception:
        return 0


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="radioreports",
        description="Запуск генераторів звітів та утиліт пакета src.radioreports",
    )
    parser.add_argument(
        "command",
        help="Команда для виконання (див. --list, щоб глянути всі варіанти)",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="Показати доступні команди та вийти",
    )
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()

    if args.list:
        print("Доступні команди:")
        # показуємо тільки унікальні (без дублікатів-синонімів поруч)
        # але для простоти — виведемо все як є, це також зручно
        for name in sorted(COMMANDS.keys()):
            print(f"  - {name}")
        return 0

    cmd = str(args.command).strip()
    if cmd not in COMMANDS:
        # дружнє повідомлення з переліком (коротке й зрозуміле)
        choices = ", ".join(sorted(COMMANDS.keys()))
        print(f"radioreports: error: невідома команда: '{cmd}'\n" f"Обери одну з: {choices}", file=sys.stderr)
        return 2

    module_relpath, func = COMMANDS[cmd]
    return _call(module_relpath, func)


if __name__ == "__main__":
    sys.exit(main())
