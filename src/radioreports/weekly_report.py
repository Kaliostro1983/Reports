from __future__ import annotations

from pathlib import Path
from datetime import datetime
import os
from typing import Optional

from docx import Document
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

from . import file_utils, docx_utils, report_utils
from .settings import AREAS, TB_CONFIG, FOOTER_SIGN, FOOTER_TEXT_1, FOOTER_TEXT_2

FILE_MASK: str = "report_*.xlsx"


# ---------- Main ----------
def main() -> None:
    print("Running weekly report...")
    # TODO: твоя реальна логіка тут
    # generate_weekly_report()


if __name__ == "__main__":
    main()
