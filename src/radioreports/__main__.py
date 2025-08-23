# src/radioreports/__main__.py
import argparse

from .daily_report import main as daily_main
from .weekly_report import main as weekly_main
from .audit_report import main as audit_main

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m src.radioreports",
        description="Запуск генераторів звітів",
    )
    sub = p.add_subparsers(dest="command", required=True)

    sub.add_parser("daily", help="Згенерувати щоденний звіт")
    sub.add_parser("weekly", help="Згенерувати тижневий звіт")
    sub.add_parser("audit", help="Згенерувати аудит-звіт")

    return p

def main() -> None:
    args = build_parser().parse_args()
    if args.command == "daily":
        daily_main()
    elif args.command == "weekly":
        weekly_main()
    elif args.command == "audit":
        audit_main()
    else:
        raise SystemExit(2)

if __name__ == "__main__":
    main()
