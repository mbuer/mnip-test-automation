#!/bin/sh
set -eu

CONFIG_PATH="${MNIP_CONFIG_PATH:-/mnip-config/config.yaml}"
CONFIG_DIR="$(dirname "$CONFIG_PATH")"

mkdir -p "$CONFIG_DIR"

if [ ! -f "$CONFIG_PATH" ]; then
    cp /app/config.example.yaml "$CONFIG_PATH"

    echo "Created initial configuration: $CONFIG_PATH"
    echo "Update the configuration before running the watcher."
    exit 2
fi

exec python -m mnip_test_automation.app
