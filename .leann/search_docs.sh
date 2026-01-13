#!/usr/bin/env bash
# On-the-fly document search
# Usage: ./search_docs.sh "your query" file1.pdf file2.pdf ...
# Example: ./search_docs.sh "What is machine learning?" "actuary-gpt*.pdf" "Practical*.pdf"

set -euo pipefail
cd "$(dirname "$0")"

# Load environment
if [ -f .env ]; then
  set -a
  source <(grep -v '^#' .env | tr -d '\r')
  set +a
fi

if [ $# -lt 2 ]; then
  echo "Usage: $0 \"search query\" file1 [file2 ...]"
  echo "Example: $0 \"machine learning\" data/actuary*.pdf"
  exit 1
fi

QUERY="$1"
shift  # Remove query from args, leaving only files

# Build file list
DOC_ARGS=()
for pattern in "$@"; do
  # Handle glob patterns
  for file in $pattern; do
    if [ -f "$file" ]; then
      DOC_ARGS+=("$file")
    else
      echo "Warning: File not found: $file"
    fi
  done
done

if [ ${#DOC_ARGS[@]} -eq 0 ]; then
  echo "Error: No valid documents found"
  exit 1
fi

echo "Indexing ${#DOC_ARGS[@]} document(s)..."
for doc in "${DOC_ARGS[@]}"; do
  echo "  - $(basename "$doc")"
done
echo ""

# Create temporary index
INDEX_NAME="temp-search-$$"

# Clean up on exit
trap "leann remove $INDEX_NAME --force 2>/dev/null || true" EXIT

# Build index
leann build "$INDEX_NAME" \
  --docs "${DOC_ARGS[@]}" \
  --embedding-mode openai \
  --embedding-model text-embedding-3-small \
  --embedding-api-base https://api.openai.com/v1 \
  --embedding-api-key "$OPENAI_API_KEY" \
  --doc-chunk-size 512 \
  --doc-chunk-overlap 128 \
  2>&1 | grep -v "^\[read_" | grep -v "^INFO:" || true

echo ""
echo "=== Search Results ==="
echo "Query: $QUERY"
echo ""

# Search
leann search "$INDEX_NAME" "$QUERY" --top-k 5 2>&1 | grep -v "^\[read_" | grep -v "^INFO:" | grep -v "^ZmqDistance"

# Cleanup handled by trap
