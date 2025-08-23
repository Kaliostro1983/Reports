import importlib


def test_settings_reads_env(monkeypatch):
    monkeypatch.setenv("DATA_DIR", r"C:\TempData")
    monkeypatch.setenv("OUTPUT_DIR", r".\out_test")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")

    # перевантажити модуль, щоб він перечитав .env/ENV
    settings = importlib.import_module("radioreports.settings")
    importlib.reload(settings)

    assert str(settings.DATA_DIR).endswith("TempData")
    assert str(settings.OUTPUT_DIR).endswith("out_test")
    assert settings.LOG_LEVEL == "DEBUG"
