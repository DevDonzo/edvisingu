#!/usr/bin/env bash
# start.sh - Start EdVisingU backend services for development on the VPS.
# Run from /opt/edvisingu (or project root). For the local demo+dashboard use
# `bash demo.sh` instead.

set -e

echo "=== EdVisingU AI Ecosystem - Starting Services ==="

# Activate venv
source venv/bin/activate 2>/dev/null || true

# Default to offline mock mode ($0, no keys). Set ARCH_BACKEND=live to go live.
export ARCH_BACKEND="${ARCH_BACKEND:-mock}"
echo "Backend: $ARCH_BACKEND"

# Start n8n via Docker (optional)
if [ -d automation ]; then
    (cd automation && docker compose up -d 2>/dev/null && echo "✓ n8n running on :5678" || echo "⚠ n8n skipped (Docker not available)")
fi

# Start the OpenAI-compatible multi-model router (the real VPS entrypoint;
# same image docker-compose builds). It serves the 25-agent fleet and falls
# back to the in-process mock when ARCH_BACKEND=mock.
cd fastapi-router
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
ROUTER_PID=$!
echo "✓ Router running on :8000 (PID: $ROUTER_PID)"
cd ..

echo ""
echo "=== Services Running ==="
echo "  Router:   http://localhost:8000/health"
echo "  Models:   http://localhost:8000/v1/models"
echo "  n8n:      http://localhost:5678"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $ROUTER_PID 2>/dev/null; echo 'Stopped.'" EXIT
wait
