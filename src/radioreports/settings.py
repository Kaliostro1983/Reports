# src/radioreports/settings.py
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv, find_dotenv  # type: ignore

# --- .env ---
if load_dotenv:
    # підвантажуємо значення з .env; якщо немає — просто беремо з оточення
    load_dotenv(find_dotenv(usecwd=True), override=True)


# ---------------- helpers ----------------
def _get_str(name: str, default: str = "") -> str:
    val = os.getenv(name, default)
    return val.strip() if isinstance(val, str) else default


def _get_int(name: str, default: int) -> int:
    try:
        return int(_get_str(name, str(default)))
    except Exception:
        return default


def _get_bool(name: str, default: bool = False) -> bool:
    val = _get_str(name, "1" if default else "0").lower()
    return val in {"1", "true", "yes", "y", "on"}


def _get_path(name: str) -> Path | None:
    raw = _get_str(name, "")
    if not raw:
        return None
    return Path(raw).expanduser().resolve()


# ---------------- базові налаштування ----------------
# Залишаю семантику як у наявному файлі (відносні шляхи теж працюють):
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output"))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Географічні ділянки / таблиці (як у чинному файлі)
AREAS = [
    {"id": 1, "names": ["ЯМПОЛІВКА"], "description": "у стику 60 омбр та 63 омбр:"},
    {"id": 2, "names": ["ТОРСЬКЕ"], "description": "у смузі відповідальності 105 мб – 106 мб:"},
    {
        "id": 3,
        "names": ["ДІБРОВА", "КРЕМІННА"],
        "description": "у смузі відповідальності 105 мб, 107 мб, 155 мб:",
    },
]
TB_CONFIG = [
    {"num": 1, "width_inch": 4.5, "v_align": 1, "h_align": 1},
    {"num": 2, "width_inch": 7, "v_align": 1, "h_align": 0},
]
REPORT_HUR_PATH = r"../../Templates/report_hur.docx"

DOWNLOADS_PATH = r"C:/Downloads/"
REPORT_FILE = r"report_"

FOOTER_TEXT_1 = (
    "* Добування розвідувальної інформації про противника здійснюється підрозділами РЕР, "
    "розгорнутими в смугах відповідальності ОТУ та надається для первинної обробки у відповідні "
    "підрозділи РЕР центрів (відділів) розвідки ОТУ, де інформація узагальнюється та надається "
    "короткий опис подій. "
)
FOOTER_TEXT_2 = (
    "Матеріали радіоперехоплень в узагальненому вигляді від підрозділів РЕР ЦР (ВР) ОТУ у визначений час "
    "надаються черговому розвідки ОКП ОСУВ “Хортиця”. Інформація, яка потребує невідкладного доведення "
    "до начальника центру розвідки ОКП ОСУВ “Хортиця”, надається черговому розвідки ОКП ОСУВ “Хортиця” "
    "негайно по тлф з подальшим документальним підтвердженням."
)

# ---------------- для «Активні мережі (63 омсбр)» ----------------
FREQS_FILE_RAW = os.getenv("FREQS_FILE", "").strip()
FREQS_FILE = Path(FREQS_FILE_RAW).expanduser().resolve() if FREQS_FILE_RAW else None

IMAGES_DIR = _get_path("IMAGES_DIR") or Path("./data/images").resolve()
HEADER_IMAGE = _get_str("HEADER_IMAGE", "header_63.png")

ACTIVE63_LOCATION = _get_str("ACTIVE63_LOCATION", "")
FOOTER_SIGN = _get_str("FOOTER_SIGN", "")

# --- нові змінні для підзаголовка та періоду ---
# година «зрізу» добового періоду (для тексту “з HH:00 … по HH:00 …”)
PERIOD_START_HOUR: int = _get_int("PERIOD_START_HOUR", 16)

# текст під зображенням; можна задати будь-яку з цих змінних
SUBHEADER_TITLE: str | None = _get_str("SUBHEADER_TITLE", "") or None
HEADER_TITLE: str | None = _get_str("HEADER_TITLE", "") or None
AREA_TITLE: str | None = _get_str("AREA_TITLE", "") or None
REGION_TITLE: str | None = _get_str("REGION_TITLE", "") or None
LOCATION_TITLE: str | None = _get_str("LOCATION_TITLE", "") or None
