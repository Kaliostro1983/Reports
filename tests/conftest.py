# tests/conftest.py
import sys
from pathlib import Path

# додати <project-root>/src у sys.path
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))
