#!/usr/bin/env bash
set -euo pipefail

if [ -z "${PHOENIX_API_KEY:-}" ]; then
  echo "PHOENIX_API_KEY is required."
  exit 1
fi

if [ -z "${PHOENIX_BASE_URL:-}" ]; then
  echo "PHOENIX_BASE_URL is required, for example: https://app.phoenix.arize.com/s/YOUR_SPACE"
  exit 1
fi

echo "Starting Phoenix MCP server smoke check..."
echo "Base URL: ${PHOENIX_BASE_URL}"
echo "Project: ${PHOENIX_PROJECT_NAME:-decision-council-demo}"

timeout 15s npx -y @arizeai/phoenix-mcp@latest \
  --baseUrl "${PHOENIX_BASE_URL}" \
  --apiKey "${PHOENIX_API_KEY}" || true

echo "Phoenix MCP server command launched. If no auth/package error appeared above, MCP is installable and configured."
