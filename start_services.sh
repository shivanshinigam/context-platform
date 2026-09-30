#!/bin/bash
# ContextOS startup script — starts Streamlit + Flask (gunicorn)
# This is the Procfile `web:` entry point on Elastic Beanstalk.
#
# Execution order:
#   1. Start Streamlit on :8501 in the background (nginx proxies /streamlit/ → :8501)
#   2. exec gunicorn (Flask API) on :8000 in the foreground
#      → EB health checks hit :8000 via nginx, so gunicorn must be the foreground proc

set -e

LOG_DIR="/var/log"
APP_DIR="$(pwd)"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] ContextOS start_services.sh — app dir: $APP_DIR"

# ── Kill any stale Streamlit from previous deploys ──────────────────────────
pkill -f "streamlit run streamlit_app" 2>/dev/null || true
sleep 1

# ── Start Streamlit in background ───────────────────────────────────────────
FLASK_API_URL=http://localhost:8000 \
python3 -m streamlit run "$APP_DIR/streamlit_app.py" \
    --server.port                8501 \
    --server.headless            true \
    --server.address             0.0.0.0 \
    --server.enableCORS          false \
    --server.enableXsrfProtection false \
    --server.baseUrlPath         streamlit \
    --browser.gatherUsageStats   false \
    >> "$LOG_DIR/streamlit.log" 2>&1 &

STREAMLIT_PID=$!
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Streamlit started — PID $STREAMLIT_PID"

# ── Start Flask/gunicorn in foreground ──────────────────────────────────────
# exec replaces this shell so gunicorn becomes PID for EB process management
exec gunicorn \
    --bind 0.0.0.0:8000 \
    --workers 1 \
    --threads 4 \
    --timeout 120 \
    application:application
