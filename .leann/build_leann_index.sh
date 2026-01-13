#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# Load environment variables
if [ -f .env ]; then
  set -a
  source <(grep -v '^#' .env | tr -d '\r')
  set +a
fi

mkdir -p data

# Rebuild from scratch
leann remove my-data --force || true

leann build my-data \
  --docs ./data/test.txt ./data/2401.16985v1.pdf \
  --embedding-mode openai \
  --embedding-model text-embedding-3-small \
  --embedding-api-base https://api.openai.com/v1 \
  --embedding-api-key "$OPENAI_API_KEY" \
  --doc-chunk-size 512 \
  --doc-chunk-overlap 128 \
  --force

# Show index health
leann list

# Smoke-test retrieval
echo ""
echo "=== Search Test ==="
leann search my-data "What is this data about?" --top-k 5 2>&1 | grep -v "^\[read_" | grep -v "^INFO:" | grep -v "^ZmqDistance"