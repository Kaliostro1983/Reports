@echo off
setlocal
pushd "%~dp0\.."
set PYTHONUTF8=1
"%~dp0..\venv\Scripts\python.exe" -X utf8 -m src.radioreports live_frequency
set ERR=%ERRORLEVEL%
popd
echo.
if %ERR% neq 0 (
  echo [ERROR] Exit code %ERR%
) else (
  echo [OK]
)
pause
