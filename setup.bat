@echo off
setlocal
cd /d "%~dp0"

REM 1) Створити venv, якщо немає
if not exist ".venv\Scripts\python.exe" (
  echo Creating .venv ...
  py -3.12 -m venv .venv
)

REM 2) Активувати venv
call ".venv\Scripts\activate.bat"

REM 3) Оновити pip та встановити залежності
python -m pip install --upgrade pip
pip install -r requirements.txt

echo.
echo ✅ Setup completed. Venv: %CD%\.venv
pause
