@echo off
setlocal
rem === стабільна українська консоль ===
chcp 65001 >nul
set "PYTHONUTF8=1"

rem === перейти в корінь репозиторію (папка вище /scripts) ===
set "REPO=%~dp0.."
pushd "%REPO%"

rem === перевірити наявність віртуалки ===
if not exist ".venv\Scripts\python.exe" (
  echo [ERR] Не знайдено .venv\Scripts\python.exe
  echo Запусти setup.bat або створюй venv вручну.
  pause
  exit /b 1
)

rem === опційно: лог у файл (розкоментуй якщо треба) ===
rem set "TS=%date:~-4%%date:~3,2%%date:~0,2%_%time:~0,2%%time:~3,2%"
rem set "LOG=output\logs\daily_%TS%.log"
rem if not exist "output\logs" mkdir "output\logs"

rem === запуск модуля з venv (жодних відносних імпортів не ламається) ===
".venv\Scripts\python.exe" -m src.radioreports daily %*  ^
    || (echo.& echo [ERROR] Exit code %errorlevel% & pause & exit /b %errorlevel%)

echo.
echo ✅ Готово. (Exit code 0)
pause
endlocal
