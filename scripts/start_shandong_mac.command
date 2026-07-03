#!/bin/zsh
cd "$(dirname "$0")/.." || exit 1
echo "Starting Shandong local launcher on localhost only..."
python scripts/run_v539_local_launcher.py --run
status=$?
if [ "$status" -ne 0 ]; then
  echo "Launcher failed. Check reports/local_launcher/ for details."
fi
echo "Press Enter to close this window."
read
