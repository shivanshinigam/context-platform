#!/bin/bash
# ContextOS — Post-deploy hook: start Streamlit independently of Flask/gunicorn
# This runs AFTER gunicorn is already up. Streamlit gets its own auto-restart loop.
set -e

LOG="/var/log/streamlit.log"
echo "" >> $LOG
echo "=====================================" >> $LOG
echo "[$(date '+%Y-%m-%d %H:%M:%S')] EB post-deploy hook: starting Streamlit" >> $LOG

# ── Find the EB-managed virtualenv Python ──
PYTHON=$(find /var/app/venv -name python -maxdepth 5 -type f 2>/dev/null | head -1)
if [ -z "$PYTHON" ]; then
    PYTHON=$(which python3)
fi
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Python binary: $PYTHON" >> $LOG

APP_DIR="/var/app/current"

# ── Kill any stale Streamlit processes from a previous deploy ──
pkill -f "streamlit run" 2>/dev/null && echo "[$(date '+%Y-%m-%d %H:%M:%S')] Killed old Streamlit process" >> $LOG || true
sleep 3

# ── Start Streamlit in a self-healing background loop ──
# 'disown' detaches it from this shell so it survives after the hook exits.
(
    while true; do
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Launching Streamlit..." >> $LOG
        FLASK_API_URL="http://localhost:8000" \
        $PYTHON -m streamlit run "$APP_DIR/streamlit_app.py" \
            --server.port 8501 \
            --server.headless true \
            --server.address 0.0.0.0 \
            --server.enableCORS false \
            --server.enableXsrfProtection false \
            --server.baseUrlPath streamlit \
            --browser.gatherUsageStats false \
            >> $LOG 2>&1
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Streamlit exited — restarting in 5 s..." >> $LOG
        sleep 5
    done
) &
disown

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Streamlit background loop running (PID group $$)" >> $LOG
exit 0
