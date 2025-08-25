# -*- coding: utf-8 -*-
from __future__ import annotations
from pathlib import Path
import pandas as pd
from typing import Optional
from .. import settings

ALLOWED_STATUSES = {"За межами", "Спостерігається", "Мертва", "Розвідується"}


def _norm_mask_key(val: object) -> Optional[str]:
    """
    Канонізація значення маски:
    - якщо числове або виглядає як число: замінюємо кому на крапку, -> float, -> формат '0.000'
    - інакше: трім + верхній регістр
    Повертаємо рядок-ключ або None.
    """
    if pd.isna(val):
        return None
    s = str(val).strip().lstrip("$").strip()
    if not s:
        return None
    s = s.replace(",", ".")
    try:
        f = float(s)
        return f"{f:.3f}"
    except ValueError:
        return s.upper()


def load_freqs() -> pd.DataFrame:
    """Завантажує таблицю радіомереж. Викидає 'За межами', нормалізує ключі."""
    if not settings.FREQS_FILE or not Path(settings.FREQS_FILE).exists():
        raise FileNotFoundError(f"FREQS_FILE не знайдено: {settings.FREQS_FILE}")

    df = pd.read_excel(settings.FREQS_FILE)

    # статуси
    df["Статус"] = df["Статус"].astype(str).str.strip()
    df = df[df["Статус"].isin(ALLOWED_STATUSES)].copy()
    df = df[~df["Статус"].str.lower().eq("за межами")].copy()

    # числова частота + ключ частоти (для канонізації частот)
    df["Частота"] = pd.to_numeric(df["Частота"], errors="coerce")
    df["freq_key"] = df["Частота"].round(3)

    # маски -> канонічні ключі
    df["mask3_key"] = df["Маска_3"].map(_norm_mask_key)
    df["maskw_key"] = df["Маска_Ш"].map(_norm_mask_key)

    # Маска_А у довіднику теж нормалізується (перший токен)
    def _first_token(x):
        if pd.isna(x):
            return None
        t = str(x).strip()
        if not t:
            return None
        return t.split()[0]

    df["maskA_key"] = df["Маска_А"].map(_first_token).map(_norm_mask_key)

    # сортування за зростанням частоти (NaN униз)
    df = df.sort_values(["Частота"], ascending=[True], na_position="last").reset_index(drop=True)
    return df
