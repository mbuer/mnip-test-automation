#!/bin/sh
set -eu

CONFIG_PATH="${MNIP_CONFIG_PATH:-/mnip-config/config.yaml}"
CONFIG_DIR="$(dirname "$CONFIG_PATH")"
MODE="${MNIP_MODE:-watch}"

mkdir -p "$CONFIG_DIR"

if [ "$MODE" = "hold" ]; then
    echo "Configuration container is ready."
    exec sleep infinity
fi

if [ ! -f "$CONFIG_PATH" ]; then
    cp /app/config.example.yaml "$CONFIG_PATH"

    echo "Created initial configuration: $CONFIG_PATH"
    echo "Configure the persistent storage before starting the watcher."
    exit 2
fi

exec python -m mnip_test_automation.app
