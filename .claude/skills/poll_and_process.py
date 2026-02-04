#!/usr/bin/env python3
"""Poll batch job status and automatically download results when complete."""

import os
import sys
import time
import subprocess
import argparse
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

# Parse command line arguments
parser = argparse.ArgumentParser(
    description='Poll batch job and download results when complete'
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

# Initialize client
client = OpenAI(
    api_key=os.environ['DOUBLEWORD_AUTH_TOKEN'],
    base_url=os.environ['DOUBLEWORD_BASE_URL']
)

# Get polling interval from environment variable (default: 60 seconds)
POLLING_INTERVAL = int(os.environ.get('POLLING_INTERVAL', '60'))

# Determine output and logs directories
output_dir = Path(args.output_dir)
logs_dir = Path(args.logs_dir) if args.logs_dir else (output_dir / 'logs')

if not logs_dir.exists():
    print(f"Error: {logs_dir} directory not found.")
    print("Run submit_batch.py first to create a batch job.")
    exit(1)

batch_id_files = list(logs_dir.glob('batch_id_*.txt'))
if not batch_id_files:
    print("Error: No batch_id_*.txt files found in ../../dw_batch_output/logs/.")
    print("Run submit_batch.py first to create a batch job.")
    exit(1)

# Get most recent batch ID file
latest_batch_id_file = max(batch_id_files, key=lambda p: p.stat().st_mtime)
with open(latest_batch_id_file, 'r') as f:
    batch_id = f.read().strip()

print("="*60)
print("BATCH MONITORING")
print("="*60)
print(f"Output directory: {output_dir.resolve()}")
print(f"Logs directory: {logs_dir.resolve()}")
print(f"Batch ID file: {latest_batch_id_file}")
print(f"Batch ID: {batch_id}")
print(f"Polling interval: {POLLING_INTERVAL}s")
print("="*60)
print("\nPress Ctrl+C to stop polling\n")

try:
    while True:
        batch = client.batches.retrieve(batch_id)
        status = batch.status
        completed = batch.request_counts.completed
        total = batch.request_counts.total

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        print(f"[{timestamp}] Status: {status} | Progress: {completed}/{total}")

        if status == 'completed':
            print("\n✓ Batch completed successfully!")
            print("Downloading and processing results...\n")

            # Run process_results.py with the same output/logs directories
            cmd = [sys.executable, 'process_results.py', '--output-dir', str(output_dir)]
            if args.logs_dir:
                cmd.extend(['--logs-dir', str(logs_dir)])
            result = subprocess.run(cmd)

            if result.returncode == 0:
                print(f"\n✓ All results saved to {output_dir.resolve()}")
            else:
                print("\n✗ Error processing results")
            break

        elif status == 'failed':
            print(f"\n✗ Batch failed!")
            if hasattr(batch, 'errors') and batch.errors:
                print(f"Errors: {batch.errors}")
            break

        elif status == 'expired':
            print(f"\n✗ Batch expired!")
            break

        elif status == 'cancelled':
            print(f"\n✗ Batch was cancelled!")
            break

        # Wait before next check
        time.sleep(POLLING_INTERVAL)

except KeyboardInterrupt:
    print("\n\nPolling stopped by user")
    print(f"Current status: {status}")
    print("Run this script again to resume polling")
