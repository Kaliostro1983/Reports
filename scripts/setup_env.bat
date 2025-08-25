@echo off
setlocal
chcp 65001 >nul

set "SCRIPT_DIR=%~dp0"
set "ROOT=%SCRIPT_DIR%.."
set "VENV=%ROOT%\venv"
set "VPY=%VENV%\Scripts\python.exe"
set "REQ=%ROOT%\requirements.txt"
set "LOGDIR=%ROOT%\output\logs"
set "LOG=%LOGDIR%\setup_env.log"

if not exist "%LOGDIR%" mkdir "%LOGDIR%"

echo [INFO] Root: "%ROOT%"
echo [INFO] Venv: "%VENV%"

REM --- Створюємо venv на Python 3.12 (якщо ще нема) ---
if not exist "%VPY%" (
  echo [INFO] Creating venv on Python 3.12...
  py -3.12 -m venv "%VENV%" 2>nul || (
    echo [WARN] Python 3.12 не знайдено. Спроба зі стандартним 'py -3'...
    py -3 -m venv "%VENV%"
  )
  if errorlevel 1 (
    echo [ERROR] Не вдалось створити venv. Переконайся, що Python встановлено.
    pause & exit /b 1
  )
)

call "%VENV%\Scripts\activate.bat"
if errorlevel 1 (
  echo [ERROR] Не вдалось активувати venv.
  pause & exit /b 1
)

set PYTHONUTF8=1

echo [INFO] Upgrading pip...
"%VPY%" -m pip install --upgrade pip >> "%LOG%" 2>&1

if exist "%REQ%" (
  echo [INFO] Installing requirements.txt...
  "%VPY%" -m pip install -r "%REQ%" >> "%LOG%" 2>&1
) else (
  echo [WARN] requirements.txt не знайдено. Ставлю мінімальний набір...
  "%VPY%" -m pip install pandas==2.2.2 openpyxl python-docx python-dotenv tzdata >> "%LOG%" 2>&1
)

echo [INFO] Verifying imports...
"%VPY%" -c "import pandas, openpyxl, docx, dotenv, tzdata; print('OK')" || (
  echo [ERROR] Імпорти не пройшли. Дивись лог: "%LOG%"
  pause & exit /b 1
)

echo [OK] Середовище готове.
echo Лог встановлення: "%LOG%"
echo.
pause
endlocal
