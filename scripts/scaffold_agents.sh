#!/usr/bin/env bash
# scaffold_agents.sh - Copies the hermes-core template to all other agents
# Run from /opt/edvisingu (or project root)

set -e

AGENTS=(
    hermes-content hermes-advisor hermes-credihire hermes-ops hermes-social
    hermes-builder hermes-research hermes-finance hermes-email
    hermes-ads hermes-seo hermes-funnel hermes-etsy hermes-outreach
    hermes-proposals hermes-crm hermes-crediversity hermes-hireed
    hermes-educonnect hermes-whop hermes-tiktok hermes-campaign
    hermes-gumroad hermes-pinterest
)

TEMPLATE_DIR="vps-agents/agents/hermes-core"

for agent in "${AGENTS[@]}"; do
    TARGET="vps-agents/agents/$agent"
    if [ ! -f "$TARGET/app.py" ]; then
        echo "Scaffolding $agent..."
        cp "$TEMPLATE_DIR/Dockerfile" "$TARGET/Dockerfile"
        cp "$TEMPLATE_DIR/requirements.txt" "$TARGET/requirements.txt"
        # Create app.py with correct agent name
        sed "s/hermes-core/$agent/g" "$TEMPLATE_DIR/app.py" > "$TARGET/app.py"
    else
        echo "Skipping $agent (already exists)"
    fi
done

echo "All agents scaffolded."
