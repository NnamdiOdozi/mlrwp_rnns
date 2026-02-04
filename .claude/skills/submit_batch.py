#!/usr/bin/env python3
"""Upload batch requests and submit batch job to Doubleword API."""

import os
import sys
import glob
import argparse
from pathlib import Path
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Parse command line arguments
parser = argparse.ArgumentParser(
    description='Upload and submit batch requests to Doubleword API'
)
parser.add_argument(
    'batch_file',
    nargs='?',
    help='Path to batch_requests_*.jsonl file (default: most recent in logs/)'
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
    sys.exit(1)

# Initialize client with Doubleword credentials
client = OpenAI(
    api_key=os.environ['DOUBLEWORD_AUTH_TOKEN'],
    base_url=os.environ['DOUBLEWORD_BASE_URL']
)

# Print environment variables being used
print("="*60)
print("BATCH SUBMISSION")
print("="*60)
print(f"Doubleword API: {os.environ['DOUBLEWORD_BASE_URL']}")
print(f"Auth Token: {'*' * 20}...{os.environ['DOUBLEWORD_AUTH_TOKEN'][-4:]}")
print(f"Completion Window: {os.getenv('COMPLETION_WINDOW', '1h')}")
print(f"Endpoint: {os.getenv('CHAT_COMPLETIONS_ENDPOINT', '/v1/chat/completions')}")
print("="*60)
print()

# Determine output and logs directories
output_dir = Path(args.output_dir)
logs_dir = Path(args.logs_dir) if args.logs_dir else (output_dir / 'logs')

# Print absolute paths for clarity
print(f"Output directory: {output_dir.resolve()}")
print(f"Logs directory: {logs_dir.resolve()}")
print()

# Determine which batch file to upload
if args.batch_file:
    # User specified a file path
    batch_file_path = args.batch_file
    if not os.path.exists(batch_file_path):
        print(f"Error: File '{batch_file_path}' not found.")
        exit(1)
else:
    # Look for most recent batch file in logs/ folder
    if not logs_dir.exists():
        print(f"Error: {logs_dir} directory not found. Run create_batch.py first.")
        exit(1)

    batch_files = list(logs_dir.glob('batch_requests_*.jsonl'))
    if not batch_files:
        print(f"Error: No batch_requests_*.jsonl files found in {logs_dir}.")
        print("Run create_batch.py first to create a batch file.")
        exit(1)

    # Get most recent batch file
    batch_file_path = max(batch_files, key=lambda p: p.stat().st_mtime)

print(f"Uploading: {batch_file_path}")
print()

# Upload batch file
with open(batch_file_path, "rb") as file:
    batch_file = client.files.create(
        file=file,
        purpose="batch"
    )

print(f"✓ File uploaded successfully!")
print(f"  File ID: {batch_file.id}")

# Create batch job
completion_window = os.getenv('COMPLETION_WINDOW', '1h')
print(f"\nCreating batch job (completion window: {completion_window})...")
batch = client.batches.create(
    input_file_id=batch_file.id,
    endpoint=os.getenv('CHAT_COMPLETIONS_ENDPOINT', '/v1/chat/completions'),
    completion_window=completion_window
)

print(f"✓ Batch job created successfully!")
print(f"  Batch ID: {batch.id}")
print(f"  Status: {batch.status}")

# Save batch ID to logs/ folder with timestamp
logs_dir.mkdir(parents=True, exist_ok=True)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
batch_id_file = logs_dir / f'batch_id_{timestamp}.txt'
with open(batch_id_file, 'w') as f:
    f.write(batch.id)

print(f"\n✓ Batch ID saved to {batch_id_file}")
print()
print("="*60)
print("NEXT STEP:")
print("  python poll_and_process.py")
print("="*60)
