# -*- coding: utf-8 -*-
from __future__ import annotations
import os
import sys
import pandas as pd

from .. import settings
from ..io.freqs_loader import load_freqs
from ..io.messages_loader import load_latest_messages
from ..logic.activity import compute_activity
from ..render.excel_writer import save_activity_xlsx


def open_file(path: str):
    try:
        if os.name == "nt":
            os.startfile(path)  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            os.system(f'open "{path}"')
        else:
            os.system(f'xdg-open "{path}"')
    except Exception:
        print(f"Відкрий вручну: {path}")


def main():
    # 1) Дані
    freqs = load_freqs()  # з FREQS_FILE, виключає 'За межами'
    msgs = load_latest_messages()  # найсвіжіший report_*.xlsx у DATA_DIR

    # 2) Аггрегація
    table, day_labels = compute_activity(freqs, msgs)

    # 3) Результат
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)
    out_path = os.path.join(settings.OUTPUT_DIR, "result.xlsx")
    out_path = save_activity_xlsx(table, day_labels, out_path)
    print(f"[OK] Збережено: {out_path}")

    # 4) Автовідкриття
    open_file(out_path)
    return 0


if __name__ == "__main__":
    main()
