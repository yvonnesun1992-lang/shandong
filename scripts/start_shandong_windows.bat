@echo off
cd /d "%~dp0\.."
echo Starting Shandong local launcher on localhost only...
python scripts\run_v539_local_launcher.py --run
if errorlevel 1 (
  echo Launcher failed. Check reports\local_launcher\ for details.
)
pause
