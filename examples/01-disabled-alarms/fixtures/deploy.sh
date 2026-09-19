#!/usr/bin/env bash
# Deploys the monitoring config to the plant-floor SCADA gateway.
set -euo pipefail
GATEWAY="${GATEWAY:-scada-gw.plant.internal}"
CONFIG="monitoring.yaml"

echo "Validating $CONFIG"
python3 -c "import yaml,sys; yaml.safe_load(open('$CONFIG'))"

echo "Pushing $CONFIG to $GATEWAY"
scp "$CONFIG" "ops@$GATEWAY:/etc/scada/monitoring.yaml"
ssh "ops@$GATEWAY" "sudo systemctl reload scada-monitor"
echo "Deploy complete"
