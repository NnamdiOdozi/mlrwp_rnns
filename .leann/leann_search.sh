#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

# Load environment variables
if [ -f .env ]; then
  set -a
  source <(grep -v '^#' .env | tr -d '\r')
  set +a
fi

# Kill any stuck embedding servers
pkill -f "hnsw_embedding_server" 2>/dev/null || true
sleep 0.5

# Run the search
leann search "$@"
