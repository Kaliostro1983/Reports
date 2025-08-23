import importlib

import pytest


def test_get_fresh_communitify_report_no_files(tmp_path, monkeypatch):
    # DATA_DIR -> порожня тимчасова тека
    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    monkeypatch.delenv("OUTPUT_DIR", raising=False)
    monkeypatch.setenv("LOG_LEVEL", "INFO")

    # перезавантажити settings і file_utils, щоб вони підхопили нове оточення
    settings = importlib.import_module("radioreports.settings")
    importlib.reload(settings)
    file_utils = importlib.import_module("radioreports.file_utils")
    importlib.reload(file_utils)

    with pytest.raises(FileNotFoundError):
        file_utils.get_fresh_communitify_report("report_*.xlsx")
