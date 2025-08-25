# src/radioreports/io/messages_loader.py
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd
import re
from zoneinfo import ZoneInfo

from .. import settings

# --- Константи ---
_KYIV = ZoneInfo("Europe/Kyiv")
# dd.mm.yyyy[, ]HH:MM[:SS]
_DATE_RE = re.compile(r"(?P<d>\d{2}\.\d{2}\.\d{4})[,\s]+(?P<t>\d{1,2}:\d{2}(?::\d{2})?)")
COL_TEXT = r"р\обмін"  # текст повідомлення
COL_FREQ = "Частота"  # частота/маска у таблиці повідомлень


# ---------------- Внутрішні допоміжні ----------------
def _normalize_kyiv(ts: pd.Series) -> pd.Series:
    """Перетворити Series datetime у часову зону Europe/Kyiv (з урахуванням наявної TZ)."""
    ts = pd.to_datetime(ts, dayfirst=True, errors="coerce", utc=False)
    # Якщо tz-naive — локалізуємо; якщо aware — конвертуємо
    try:
        aware_mask = ts.dt.tz.notna()
        ts.loc[~aware_mask] = ts.loc[~aware_mask].dt.tz_localize(_KYIV, nonexistent="NaT", ambiguous="NaT")
        ts.loc[aware_mask] = ts.loc[aware_mask].dt.tz_convert(_KYIV)
    except Exception:
        # на випадок якщо це не datetime64 — залишаємо як є
        pass
    return ts


def _parse_dt_from_text(text: str) -> pd.Timestamp:
    """Витягнути дату/час із тексту поля 'р\\обмін'."""
    m = _DATE_RE.search(str(text))
    if not m:
        return pd.NaT
    s = f"{m.group('d')} {m.group('t')}"
    ts = pd.to_datetime(s, dayfirst=True, errors="coerce")
    if pd.isna(ts):
        return pd.NaT
    return ts.tz_localize(_KYIV) if ts.tzinfo is None else ts.tz_convert(_KYIV)


def _find_latest_report(dir_path: Path, prefix: str) -> Optional[Path]:
    """Повернути найсвіжіший report_*.xlsx у теці або None."""
    if not dir_path.exists():
        return None
    files = sorted(dir_path.glob(f"{prefix}*.xlsx"), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


# ---------------- Публічна API ----------------
def load_latest_messages(xlsx_path: str | Path | None = None) -> pd.DataFrame:
    """
    Завантажує таблицю повідомлень.

    Повертає DataFrame, який гарантовано містить:
      - 'dt'        : datetime з tz Europe/Kyiv
      - 'day_label' : рядок 'DD.MM' з 'dt'
      - 'Частота'   : як у вихідному файлі (може бути число/маска/порожньо)
      - 'р\\обмін'  : вихідний текст повідомлення (якщо є)

    Якщо `xlsx_path` не заданий — шукає найсвіжіший файл за шаблоном
    `{settings.REPORT_FILE}*.xlsx` у теці `settings.DATA_DIR`.
    """
    # 1) Визначити шлях до файла
    if xlsx_path:
        path = Path(xlsx_path)
    else:
        data_dir = settings.DATA_DIR if isinstance(settings.DATA_DIR, Path) else Path(str(settings.DATA_DIR))
        prefix = getattr(settings, "REPORT_FILE", "report_")
        path = _find_latest_report(data_dir, prefix)

    if not path or not path.exists():
        raise FileNotFoundError(f"Не знайдено файл звіту у '{settings.DATA_DIR}'. " f"Очікував шаблон '{getattr(settings, 'REPORT_FILE', 'report_')}*.xlsx'.")

    # 2) Зчитати Excel
    df = pd.read_excel(path, engine="openpyxl")

    # 3) Стовпець 'dt'
    if "dt" in df.columns:
        df["dt"] = _normalize_kyiv(df["dt"])
    elif "Дата/час" in df.columns:
        df["dt"] = _normalize_kyiv(df["Дата/час"])
    else:
        # пробуємо дістати з тексту
        src = df[COL_TEXT] if COL_TEXT in df.columns else pd.Series([None] * len(df))
        df["dt"] = src.apply(_parse_dt_from_text)

    # 4) day_label
    df["day_label"] = df["dt"].dt.strftime("%d.%m").fillna("")

    # 5) Переконаємось, що критичні колонки існують
    if COL_TEXT not in df.columns:
        df[COL_TEXT] = ""
    if COL_FREQ not in df.columns:
        df[COL_FREQ] = ""

    return df
