# -*- coding: utf-8 -*-
from __future__ import annotations
import os, re
from typing import Optional, Set, Tuple

_NUM_RE = re.compile(r"[-+]?\d+(?:[.,]\d+)?")


def _first_numeric_token(s: str) -> Optional[str]:
    m = _NUM_RE.search(s)
    return m.group(0) if m else None


def _to_float3(val: object) -> Optional[float]:
    """
    Стає значно терпимішим:
      '200,224' -> 200.224
      ' 200.224 М ' -> 200.224
      '200.224#' -> 200.224
      '$ 200.224' -> 200.224
    Беремо ПЕРШИЙ числовий токен у рядку.
    """
    if val is None:
        return None
    s = str(val).strip()
    if not s:
        return None
    tok = _first_numeric_token(s.replace("\u00a0", " "))  # NBSP -> space
    if not tok:
        return None
    tok = tok.replace(",", ".")
    try:
        return round(float(tok), 3)
    except ValueError:
        return None


def _to_text_key(val: object) -> Optional[str]:
    if val is None:
        return None
    s = str(val).strip().lstrip("$").strip()
    return s.upper() if s else None


def _parse_freqs(s: Optional[str]) -> Set[float]:
    out: Set[float] = set()
    if not s:
        return out
    for part in s.split(","):
        f = _to_float3(part)
        if f is not None:
            out.add(f)
    return out


def _parse_masks(s: Optional[str]) -> Tuple[Set[float], Set[str]]:
    nums: Set[float] = set()
    txts: Set[str] = set()
    if not s:
        return nums, txts
    for part in s.split(","):
        f = _to_float3(part)
        if f is not None:
            nums.add(f)
        t = _to_text_key(part)
        if t:
            txts.add(t)
    return nums, txts


class Tracer:
    def __init__(self):
        self.freqs = _parse_freqs(os.getenv("TRACE_FREQS"))
        self.mask_nums, self.mask_txts = _parse_masks(os.getenv("TRACE_MASKS"))
        self.active = bool(self.freqs or self.mask_nums or self.mask_txts)

    def want_freq(self, fk: Optional[float]) -> bool:
        return self.active and fk is not None and fk in self.freqs

    def want_mask_val(self, raw) -> bool:
        if not self.active:
            return False
        f = _to_float3(raw)
        t = _to_text_key(raw)
        return (f is not None and f in self.mask_nums) or (t is not None and t in self.mask_txts)

    def log(self, *parts):
        if self.active:
            try:
                print("[TRACE]", *parts, flush=True)
            except Exception:
                pass

    def map_mask(self, label: str, raw, fk: Optional[float], key_num: Optional[float], key_txt: Optional[str]):
        if self.active and (self.want_freq(fk) or self.want_mask_val(raw)):
            self.log(f"mask-map: {label}: raw={raw!r} -> num={key_num!r} txt={key_txt!r} -> freq_key={fk!r}")

    def row_begin(self, row_idx: int, raw_val, raw_text):
        if self.active and (self.want_mask_val(raw_val) or raw_text):
            self.log(f"row#{row_idx}: in 'Частота'={raw_val!r}, in 'р\\обмін'={str(raw_text)[:80]!r}")

    def row_try_mask(self, row_idx: int, label: str, key_repr: str, fk: Optional[float]):
        if self.active:
            self.log(f"row#{row_idx}: as {label} -> key={key_repr} -> freq_key={fk!r}")

    def row_try_real(self, row_idx: int, f: Optional[float], ok: bool):
        if self.active:
            self.log(f"row#{row_idx}: as REAL freq f={f!r} -> {'HIT' if ok else 'MISS'}")

    def row_try_maskA_text(self, row_idx: int, token: str, fk: Optional[float]):
        if self.active:
            self.log(f"row#{row_idx}: from r\\obmin token={token!r} -> freq_key={fk!r}")

    def row_result(self, row_idx: int, fk: Optional[float]):
        if self.active:
            self.log(f"row#{row_idx}: RESULT -> freq_key={fk!r}")


tracer = Tracer()
