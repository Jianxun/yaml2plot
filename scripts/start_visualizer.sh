#!/usr/bin/env bash
set -euo pipefail

# Start the React Flow visualizer in dev mode

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET_DIR="$PROJECT_ROOT/prototype/visualizer_react_flow"

if [[ ! -d "$TARGET_DIR" ]]; then
  echo "Error: visualizer directory not found: $TARGET_DIR" >&2
  exit 1
fi

cd "$TARGET_DIR"

if [[ ! -d node_modules ]]; then
  echo "Installing dependencies..."
  npm install
fi

echo "Starting dev server (press Ctrl+C to stop)..."
npm run dev


