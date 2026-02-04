#!/usr/bin/env python3
"""Download batch results and save summaries to data/summaries/."""

import os
import glob
import json
import argparse
from pathlib import Path
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Parse command line arguments
parser = argparse.ArgumentParser(
    description='Download batch results and save to output directory'
)
parser.add_argument(
    '--output-dir',
    metavar='DIR',
    default='../../dw_batch_output',
    help='Output directory (default: ../../dw_batch_output)'
)
parser.add_argument(
    '--logs-dir',
    metavar='DIR',
    help='Logs directory (default: {output-dir}/logs)'
)

args = parser.parse_args()

# Load environment variables
load_dotenv()

# Security preflight check - verify required environment variables
required_vars = ['DOUBLEWORD_AUTH_TOKEN', 'DOUBLEWORD_BASE_URL']
missing_vars = [var for var in required_vars if not os.getenv(var)]

if missing_vars:
    print("="*60)
    print("ERROR: Missing required environment variables")
    print("="*60)
    for var in missing_vars:
        print(f"  ❌ {var}")
    print()
    print("Setup instructions:")
    print("  1. Copy .env.sample to .env")
    print("  2. Edit .env and add your DOUBLEWORD_AUTH_TOKEN")
    print("  3. Ensure .env is in the same directory as this script")
    print()
    print("SECURITY: Never commit .env to git - it's in .gitignore")
    print("="*60)
    exit(1)

# Initialize client
client = OpenAI(
    api_key=os.environ['DOUBLEWORD_AUTH_TOKEN'],
    base_url=os.environ['DOUBLEWORD_BASE_URL']
)

# Determine output and logs directories
output_dir = Path(args.output_dir)
logs_dir = Path(args.logs_dir) if args.logs_dir else (output_dir / 'logs')

# Find most recent batch_id file in logs/
if not logs_dir.exists():
    print(f"Error: {logs_dir} directory not found.")
    exit(1)

batch_id_files = list(logs_dir.glob('batch_id_*.txt'))
if not batch_id_files:
    print("Error: No batch_id_*.txt files found in logs/.")
    exit(1)

latest_batch_id_file = max(batch_id_files, key=lambda p: p.stat().st_mtime)
with open(latest_batch_id_file, 'r') as f:
    batch_id = f.read().strip()

print(f"Retrieving batch results: {batch_id}\n")

# Get batch status
batch = client.batches.retrieve(batch_id)

if batch.status != 'completed':
    print(f"✗ Batch not completed yet. Status: {batch.status}")
    exit(1)

print(f"✓ Batch completed successfully")
print(f"Output file ID: {batch.output_file_id}\n")

# Download results file
print("Downloading results...")
file_response = client.files.content(batch.output_file_id)

# Create output directory
output_dir.mkdir(parents=True, exist_ok=True)
print(f"Output directory: {output_dir.resolve()}")
print(f"Summaries will be saved to: {output_dir}/\n")

# Process each result
results_count = 0
for line in file_response.text.split('\n'):
    if not line.strip():
        continue

    result = json.loads(line)
    custom_id = result['custom_id']

    # Extract summary from response
    summary = result['response']['body']['choices'][0]['message']['content']

    # Extract filename from custom_id (e.g., "summary-DGM" -> "DGM")
    filename = custom_id.replace('summary-', '')

    # Generate timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Save summary with timestamp as markdown
    output_path = output_dir / f'{filename}_summary_{timestamp}.md'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(summary)

    print(f"✓ Saved: {output_path}")
    results_count += 1

print(f"\n✓ Successfully processed {results_count} summaries")
