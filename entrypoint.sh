set -euo pipefail

REQ="/app/requirements.txt"
MAIN="/app/main.py"
SETUP="/app/setup.py"

if [ "${SKIP_PIP_INSTALL:-0}" != "1" ]; then
  if [ -f "$REQ" ]; then
    echo "[entrypoint] Ensuring deps..."
    python -m pip install --upgrade pip
    python -m pip install --no-cache-dir -r "$REQ"
  fi
fi

if [ -f "$MAIN" ]; then
  echo "[entrypoint] Starting ompbot..."
  python "$SETUP"
  python "$MAIN"
else
  echo "[entrypoint] No $MAIN found"; exec /bin/bash
fi
