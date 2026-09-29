#!/usr/bin/env bash
# Wyvern Fintech OS Launcher
set -e

PORT=${PORT:-8000}
HOST=${HOST:-"0.0.0.0"}

echo "--------------------------------------------------------"
echo "  WYVERN // FINTECH OPERATING SYSTEM (Nothing OS Edition)"
echo "--------------------------------------------------------"
echo "  [+] Starting FastAPI Application Server on http://${HOST}:${PORT}"
echo "  [+] ML Categorizer: Online (TF-IDF + Calibrated Logistic Regression)"
echo "  [+] Savings Forecaster: Online (Ridge Polynomial Regression)"
echo "  [+] Anomaly Radar: Online (Isolation Forest + MAD Statistics)"
echo "  [+] Plaid Engine: Online (Sandbox & Production OAuth Ready)"
echo "  [+] Live Market Feed: Online (NSE, BSE, S&P 500, NASDAQ)"
echo "--------------------------------------------------------"

cd /home/eqzinit/wyvern
exec python3 -m uvicorn server.main:app --host "${HOST}" --port "${PORT}" --reload
