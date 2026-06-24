#!/usr/bin/env bash
set -e
cd /Users/hparacha/Downloads/edvisingu

# API_PORT defaults to 8000. Override if 8000 is taken, e.g. `API_PORT=8088 bash demo.sh`.
API_PORT="${API_PORT:-8000}"
API_URL="http://localhost:${API_PORT}"

echo ""
echo "  ┌─────────────────────────────────────────────┐"
echo "  │  EdVisingU AI Ecosystem — Hamza Paracha       │"
echo "  │  Offline mode · \$0 · no API key required      │"
echo "  └─────────────────────────────────────────────┘"
echo ""

# Auto-bump the API port if the chosen one is already in use.
if lsof -ti:"$API_PORT" >/dev/null 2>&1; then
  echo "  ! Port $API_PORT busy — falling back to 8088"
  API_PORT=8088
  API_URL="http://localhost:${API_PORT}"
fi

source venv/bin/activate
export ARCH_BACKEND="${ARCH_BACKEND:-mock}"

uvicorn demo_server:app --host 0.0.0.0 --port "$API_PORT" > /tmp/cc-api.log 2>&1 &
API_PID=$!
sleep 1
echo "  ✓ API         $API_URL   (backend: $ARCH_BACKEND)"
echo "  ✓ Docs        $API_URL/docs"

cd dashboards/edvisingu-dashboard
# The dashboard reads NEXT_PUBLIC_API_URL (falls back to localhost:8000).
export NEXT_PUBLIC_API_URL="$API_URL"
npx next dev -p 3000 > /tmp/cc-dash.log 2>&1 &
DASH_PID=$!
sleep 3
echo "  ✓ Dashboard   http://localhost:3000"
echo ""
echo "  Pages:"
echo "    /dashboard            Overview"
echo "    /dashboard/hermes     Hermes AI chat"
echo "    /dashboard/content    Content Factory"
echo "    /dashboard/advisor    Student Advisor"
echo "    /dashboard/credihire  Resume Engine"
echo "    /dashboard/leads      CRM"
echo "    /dashboard/analytics  Analytics"
echo "    /dashboard/fleet      Agent Fleet (25)"
echo "    /dashboard/status     System Status"
echo ""
echo "  CLI:  python run.py selftest | chat | content | taskbus | fleet"
echo "  Ctrl+C to stop"

trap "kill $API_PID $DASH_PID 2>/dev/null; echo '  Stopped.'" EXIT INT
wait
