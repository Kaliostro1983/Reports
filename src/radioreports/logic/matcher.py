# -*- coding: utf-8 -*-
from __future__ import annotations
from typing import Dict, Optional, List, Tuple
import pandas as pd
import re

# ---------- нормалізація ----------

_NUM_RE = re.compile(r"[-+]?\d+(?:[.,]\d+)?")


def _first_numeric_token(s: str) -> Optional[str]:
    m = _NUM_RE.search(s)
    return m.group(0) if m else None


def _to_float3(val: object) -> Optional[float]:
    """
    Терпима нормалізація чисел:
      '200,224' -> 200.224
      ' 200.224 М ' -> 200.224
      '200.224#' -> 200.224
      '$ 200.224' -> 200.224
    Беремо ПЕРШИЙ числовий токен у рядку і округлюємо до 3-х знаків.
    """
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    s = str(val).strip()
    if not s or s.lower() == "nan":
        return None
    s = s.replace("\u00a0", " ")  # NBSP -> space
    tok = _first_numeric_token(s)
    if not tok:
        return None
    tok = tok.replace(",", ".")
    try:
        return round(float(tok), 3)
    except ValueError:
        return None


def _to_text_key(val: object) -> Optional[str]:
    """Канонічний текстовий ключ (trim, upper, без '$'); 'nan' і порожнє ігноруємо."""
    if val is None or (isinstance(val, float) and pd.isna(val)):
        return None
    s = str(val).strip().lstrip("$").strip()
    if not s or s.lower() == "nan":
        return None
    return s.upper()


# ---------- матчер ----------


class NetworkMatcher:
    """
    УСІ розрахунки ведемо по частоті як float (round(., 3)).
    Маски (3/Ш/А) мапляться безпосередньо у freq_key (float).
    Порядок визначення частоти для повідомлення:
      1) трактуємо значення в полі 'Частота' як МАСКУ (3 -> Ш -> А; число/текст)
      2) якщо не знайдено — трактуємо це значення як реальну частоту
      3) якщо в полі 'Частота' порожньо/не спрацювало — беремо Маску_А з 'р\\обмін' ($ ...).
    """

    def __init__(self, freqs_df: pd.DataFrame):
        # очікуємо колонки: 'Частота', 'Статус', 'Маска_3', 'Маска_Ш', 'Маска_А'
        self.freqs = freqs_df.reset_index(drop=True).copy()

        # частоти -> ключ (float, 3 знаки)
        self.freqs["freq_key"] = pd.to_numeric(self.freqs["Частота"], errors="coerce").round(3)

        # freq_key (float) -> індекс першого рядка з такою частотою
        self.canon_idx_by_freq: Dict[float, int] = {}
        self._build_freq_canons()

        # маски (числові/текстові) -> freq_key (float)
        self.mask3_num: Dict[float, float] = {}
        self.maskw_num: Dict[float, float] = {}
        self.maskA_num: Dict[float, float] = {}
        self.mask3_txt: Dict[str, float] = {}
        self.maskw_txt: Dict[str, float] = {}
        self.maskA_txt: Dict[str, float] = {}

        # діагностика конфліктів (можна виводити за потреби)
        self.ambiguous: List[Tuple[str, str, List[float]]] = []

        self._build_mask_maps()

    # ---- побудова індексів ----

    def _build_freq_canons(self) -> None:
        seen: Dict[float, int] = {}
        for i, fk in self.freqs["freq_key"].items():
            if pd.isna(fk):
                continue
            fk = float(fk)
            if fk not in seen:
                seen[fk] = i
        self.canon_idx_by_freq = seen  # float freq_key -> canonical row index

    def _note_amb(self, label: str, key_repr: str, old_fk: float, new_fk: float):
        if old_fk == new_fk:
            return
        pair = (label, key_repr, sorted({old_fk, new_fk}))
        if pair not in self.ambiguous:
            self.ambiguous.append(pair)

    def _put(self, mapping: Dict, key, freq_key: float, label: str):
        if key is None:
            return
        old = mapping.get(key)
        if old is not None and old != freq_key:
            self._note_amb(label, str(key), old, freq_key)
        mapping[key] = freq_key

    def _build_mask_maps(self) -> None:
        for _, row in self.freqs.iterrows():
            fk = row.get("freq_key")
            if pd.isna(fk):
                continue
            fk = float(fk)

            # Маска_3
            raw = row.get("Маска_3")
            self._put(self.mask3_num, _to_float3(raw), fk, "Маска_3")
            self._put(self.mask3_txt, _to_text_key(raw), fk, "Маска_3")

            # Маска_Ш
            raw = row.get("Маска_Ш")
            self._put(self.maskw_num, _to_float3(raw), fk, "Маска_Ш")
            self._put(self.maskw_txt, _to_text_key(raw), fk, "Маска_Ш")

            # Маска_А (беремо перший токен)
            raw = row.get("Маска_А")
            tok = None
            if pd.notna(raw):
                t = str(raw).strip()
                if t:
                    tok = t.split()[0]
            self._put(self.maskA_num, _to_float3(tok), fk, "Маска_А")
            self._put(self.maskA_txt, _to_text_key(tok), fk, "Маска_А")

        # (за бажанням) можна вивести self.ambiguous для ревізії довідника

    # ---- API ----

    def resolve_row_to_freq_key(self, row: pd.Series) -> Optional[float]:
        """
        Повертає частоту (float, 3 знаки), до якої слід зарахувати повідомлення.
        Порядок:
          1) 'Частота' як маска (3/Ш/А, число або текст);
          2) 'Частота' як реальна частота;
          3) '$ …' у 'р\\обмін' (Маска_А).
        """
        raw_val = row.get("Частота")
        raw_text = row.get("р\\обмін")

        # 1) 'Частота' як маска — числова
        f = _to_float3(raw_val)
        if f is not None:
            for mapping in (self.mask3_num, self.maskw_num, self.maskA_num):
                fk = mapping.get(f)
                if fk is not None:
                    return fk

        # 1b) 'Частота' як маска — текстова
        t = _to_text_key(raw_val)
        if t:
            for mapping in (self.mask3_txt, self.maskw_txt, self.maskA_txt):
                fk = mapping.get(t)
                if fk is not None:
                    return fk

        # 2) 'Частота' як реальна частота
        rf = _to_float3(raw_val)
        if rf is not None and rf in self.canon_idx_by_freq:
            return rf

        # 3) '$' у 'р\обмін' -> Маска_А (перший токен після '$')
        if raw_text is not None and not (isinstance(raw_text, float) and pd.isna(raw_text)):
            s = str(raw_text).strip()
            if s.startswith("$"):
                s = s[1:].strip()
            token = s.split()[0] if s else ""
            if token:
                ft = _to_float3(token)
                if ft is not None:
                    fk = self.maskA_num.get(ft)
                    if fk is not None:
                        return fk
                tt = _to_text_key(token)
                if tt:
                    fk = self.maskA_txt.get(tt)
                    if fk is not None:
                        return fk

        return None
