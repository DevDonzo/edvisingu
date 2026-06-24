#!/usr/bin/env bash
# start.sh - Start all EdVisingU AI services for development
# Run from /opt/edvisingu (or project root)

set -e

echo "=== EdVisingU AI Ecosystem - Starting Services ==="

# Activate venv
source venv/bin/activate 2>/dev/null || true

# Default to offline mock mode ($0, no keys). Set ARCH_BACKEND=live to go live.
export ARCH_BACKEND="${ARCH_BACKEND:-mock}"
echo "Backend: $ARCH_BACKEND"

# Start Ollama (if installed)
if command -v ollama &>/dev/null; then
    pgrep ollama >/dev/null || (ollama serve >/tmp/ollama.log 2>&1 &)
    echo "✓ Ollama running"
fi

# Start n8n via Docker
cd automation
docker compose up -d 2>/dev/null && echo "✓ n8n running on :5678" || echo "⚠ n8n skipped (Docker not available)"
cd ..

# Start FastAPI
cd agents
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
FASTAPI_PID=$!
echo "✓ FastAPI running on :8000 (PID: $FASTAPI_PID)"
cd ..

echo ""
echo "=== Services Running ==="
echo "  FastAPI:  http://localhost:8000/health"
echo "  n8n:      http://localhost:5678"
echo "  Ollama:   http://localhost:11434"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $FASTAPI_PID 2>/dev/null; echo 'Stopped.'" EXIT
wait
