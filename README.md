# Radio Reports

Генерація щоденних / тижневих / аудит-звітів з XLSX (COMMUNITIFY) у DOCX.

## Вимоги
- Windows 10/11
- Python 3.12 (рекомендовано)
- Право запису в папку `output/`

## Структура
project-root/
├─ scripts/ # ярлики запуску
│ ├─ run_daily_report.bat
│ ├─ run_weekly_report.bat
│ └─ run_audit_report.bat
├─ src/
│ └─ radioreports/
│ ├─ init.py
│ ├─ main.py # єдиний вхід: python -m src.radioreports <cmd>
│ ├─ daily_report.py
│ ├─ weekly_report.py
│ ├─ audit_report.py
│ ├─ file_utils.py
│ ├─ docx_utils.py
│ ├─ report_utils.py
│ ├─ logging_cfg.py
│ └─ settings.py
├─ .env # налаштування середовища (локально)
├─ requirements.txt
├─ setup.bat # створення .venv та встановлення залежностей
└─ output/ # згенеровані звіти


## Швидкий старт
1. **Створити середовище та встановити залежності**
   - двічі клікнути `setup.bat` (або `.\setup.bat` у терміналі)

2. **Налаштувати змінні середовища**  
   Створити файл `.env` (без лапок в значеннях), наприклад:

DATA_DIR=C:\Downloads
OUTPUT_DIR=output
LOG_LEVEL=INFO


3. **Запустити будь-який звіт**
- через ярлик: `scripts\run_daily_report.bat`  
- або через модуль:
  ```
  python -m src.radioreports daily
  python -m src.radioreports weekly
  python -m src.radioreports audit
  ```

## Формат вхідних файлів
У теці `DATA_DIR` мають бути Excel-файли з маскою: report_*.xlsx


Скрипт автоматично бере **найсвіжіший** файл.

## Логи
- Консоль + файл: `output\app.log` (ротація до 500 КБ, 3 копії)
- Рівень логування керується `LOG_LEVEL` у `.env`.

## Типові проблеми
- **Файли не знайдено**
  - перевірити `DATA_DIR` у `.env`
  - маска має бути `report_*.xlsx`
- **Модулі не знайдено (`No module named ...`)**
  - спочатку запустити `setup.bat`
  - у VS Code обрати інтерпретатор: `.venv\Scripts\python.exe`

## Розробка
- Єдиний вхід у пакет:  
  `python -m src.radioreports <daily|weekly|audit>`
- Точки входу в модулях: функції `main()`.




