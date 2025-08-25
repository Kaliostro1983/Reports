# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import List, Tuple, Dict
import pandas as pd
from .matcher import NetworkMatcher


def _sorted_unique_days(msgs_df: pd.DataFrame) -> List[str]:
    """Повертає ярлики днів у форматі 'дд.мм' у хронологічному порядку."""
    day_series = msgs_df["dt"].dt.floor("D")
    uniq_days = sorted(day_series.dropna().unique().tolist())
    return [pd.Timestamp(d).strftime("%d.%m") for d in uniq_days]


def compute_activity(freqs_df: pd.DataFrame, msgs_df: pd.DataFrame) -> Tuple[pd.DataFrame, List[str]]:
    """
    Формує підсумкову таблицю з колонками:
      '№ п/п' | 'Частота' | 'Статус' | <дні ...> | 'загалом'

    - Рахуємо по ключу частоти (float, округлення до 3 знаків).
    - У виводі 'Частота' залишається числом (формат '0.0000' застосовує writer).
    - 'загалом' = сума значень по денних колонках у рядку.
    """
    day_labels = _sorted_unique_days(msgs_df)

    matcher = NetworkMatcher(freqs_df)

    # Унікальні частоти (float3) -> базові рядки
    uniq_freq_keys = sorted(matcher.canon_idx_by_freq.keys())
    rows = []
    for fk in uniq_freq_keys:
        i = matcher.canon_idx_by_freq[fk]
        freq_val = float(freqs_df.loc[i, "Частота"]) if pd.notna(freqs_df.loc[i, "Частота"]) else float("nan")
        status = freqs_df.loc[i, "Статус"]
        base = {"Частота": freq_val, "Статус": status}
        for lab in day_labels:
            base[lab] = 0
        rows.append(base)

    out = pd.DataFrame(rows)
    out.insert(0, "№ п/п", range(1, len(out) + 1))

    # Мапа: freq_key -> позиція рядка у out
    pos_by_fk: Dict[float, int] = {fk: pos for pos, fk in enumerate(uniq_freq_keys)}

    # Підрахунок по днях
    for _, row in msgs_df.iterrows():
        fk = matcher.resolve_row_to_freq_key(row)
        if fk is None:
            continue
        pos = pos_by_fk.get(fk)
        if pos is None:
            continue
        dt = row.get("dt")
        if pd.notna(dt):
            lab = pd.Timestamp(dt).strftime("%d.%m")
            if lab in out.columns:
                out.at[pos, lab] = int(out.at[pos, lab]) + 1

    # Нова колонка: загальна кількість за період
    if day_labels:
        out["загалом"] = out[day_labels].sum(axis=1).astype(int)
    else:
        # на випадок порожнього періоду
        out["загалом"] = 0

    return out, day_labels
