# Batch Document Summarization with Doubleword API

A simple Python CLI Pipeline for batch processing documents (PDF, DOCX, PPTX, TXT, MD, ODP) into structured summaries using the ultra low-cost Doubleword API and open-weight models. Just load your docs, a prompt, and then the Doubleword API key and you're good to go.

## Overview

This tool extracts text from multiple document formats and generates comprehensive ~2000-word structured summaries using Doubleword's batch inference API. Originally built for literature reviews in actuarial machine learning research, it can be adapted for any bulk document summarization task.

## Use Cases

- **Literature reviews** - Summarize academic papers systematically
- **Regulatory analysis** - Convert 200-page consultation papers into actionable digests
- **Compliance** - Extract structured data from policy documents at scale
- **Sentiment analysis** - Process customer feedback documents in bulk
- **Research synthesis** - Analyze collections of technical reports
- **LLM/Agent Evaluations** - Use LLM as a Judge to evaluate LLM and Agent outputs

## Performance

**Real-world results:**
- **Initial test:** 2 papers processed in ~1 minute
- **Production run:** 33 papers processed in ~30 minutes
- **Total cost:** ~15 pence for 35 papers
- **SLA:** Selected 24-hour window, actual delivery < 30 minutes

## Supported File Formats

- **PDF** (`.pdf`) - Research papers, reports, articles
- **Microsoft Word** (`.docx`) - Documents, proposals
- **Microsoft PowerPoint** (`.pptx`) - Presentations, slide decks
- **OpenDocument Presentation** (`.odp`) - Open format presentations
- **Plain Text** (`.txt`) - Text documents
- **Markdown** (`.md`) - Technical documentation, notes

All formats are processed through the same pipeline with automatic file type detection.

## How It Works

The pipeline consists of three stages:

### Stage 1: Document Extraction & Batch Request Creation
**Script:** `create_batch.py`

- Scans `data/papers/` folder (or custom location via `--input-dir`)
- Extracts text from multiple formats:
  - **PDF:** pypdf (fast) with pdfplumber fallback (robust)
  - **DOCX:** python-docx
  - **PPTX:** python-pptx
  - **ODP:** odfpy
  - **TXT/MD:** Direct text read
- Creates structured JSONL batch requests with custom summarization prompt
- Outputs: `batch_requests_{timestamp}.jsonl`

### Stage 2: Batch Submission
**Script:** `submit_batch.py`

- Uploads `batch_requests.jsonl` to Doubleword API
- Creates batch job with 1-hour completion window
- Saves batch ID to `batch_id.txt` for tracking
- Outputs: Batch ID for monitoring

### Stage 3: Polling & Processing
**Script:** `poll_and_process.py`

- Polls batch job status at configurable intervals (default: 60 seconds)
- Automatically downloads results when completed
- Calls `process_results.py` to extract and save individual summaries
- Outputs: Individual markdown summaries in `data/summaries/`

### Processing Results
**Script:** `process_results.py`

- Downloads batch output file from Doubleword API
- Parses JSONL responses
- Saves each summary as timestamped markdown file
- Format: `{filename}_summary_{timestamp}.md`

## Setup

### 1. Install Dependencies
git clone https://github.com/NnamdiOdozi/batch_summary_doubleword.git

Using uv (recommended):
```bash
uv sync
source .venv/bin/activate  # Linux/macOS
# OR on Windows: .venv\Scripts\activate
```

Or using pip:
```bash
python3 -m venv .venv
source .venv/bin/activate  # Linux/macOS  
# OR on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Requirements** ([requirements.txt](requirements.txt)):
- `pypdf>=6.6.0` - Fast PDF text extraction
- `pdfplumber>=0.11.9` - Robust fallback for complex PDFs
- `python-docx>=1.1.0` - Microsoft Word document extraction
- `python-pptx>=1.0.0` - PowerPoint presentation extraction
- `odfpy>=1.4.1` - OpenDocument format extraction
- `openai>=2.14.0` - API client (compatible with Doubleword API)
- `python-dotenv>=1.1.0` - Environment variable management

### 2. Configure Environment Variables

Copy the sample environment file:
```bash
cp .env.sample .env
```

Edit `.env` and fill in your credentials:
```bash
# Your Doubleword API token
DOUBLEWORD_AUTH_TOKEN=your_api_token_here

# Doubleword API endpoint
DOUBLEWORD_BASE_URL=https://api.doubleword.ai/v1

# API endpoint for chat completions (relative to base URL)
CHAT_COMPLETIONS_ENDPOINT=/v1/chat/completions

# Model to use
DOUBLEWORD_MODEL=Qwen/Qwen3-VL-235B-A22B-Instruct-FP8
or any other model you would like eg the smaller and cheaper Qwen/Qwen3-VL-30B-A3B-Instruct-FP8

# Polling frequency (seconds)
POLLING_INTERVAL=60

# Batch completion window or SLA (how long the API has to complete the job)
# Options: "1h" or "24h"
COMPLETION_WINDOW=1h

# Summary word count (target length for generated summaries)
SUMMARY_WORD_COUNT=2000

# Maximum tokens for model response (includes reasoning + summary)
MAX_TOKENS=5000
```

**Get your API key:**
1. Visit [Doubleword Portal](https://doubleword.ai)
2. Click to join Private Preview
3. Create account or log in
4. Generate API key in settings

### 3. Add Your Documents 
      
Place documents in:
- `data/papers/` folder

Supported formats: PDF, DOCX, PPTX, ODP, TXT, MD     

The pipeline will automatically detect and process all supported files in this directory.

### 4. Customize Summarization (Optional)

**Adjust word count:**
Edit `SUMMARY_WORD_COUNT` in `.env` to change summary length (default: 2000 words)

**Customize prompt template:**
Edit [summarisation_prompt.txt](summarisation_prompt.txt) to adjust:
- Output structure and fields
- Technical complexity level
- Markdown formatting
- Required fields

## Usage

### Quick Start - Run Full Pipeline

```bash
python run_batch_pipeline.py
```

This orchestrator script runs all three stages automatically:
1. Extracts documents and creates batch requests
2. Submits to Doubleword API
3. Polls until complete and downloads summaries

### Command Line Options

**Process all files in default directory:**
```bash
python run_batch_pipeline.py
```

**Process specific files:**
```bash
python run_batch_pipeline.py --files paper1.pdf report.docx slides.pptx
```

**Process files from custom directory:**
```bash
python run_batch_pipeline.py --input-dir /path/to/documents/
```

**View all options:**
```bash
python run_batch_pipeline.py --help
python create_batch.py --help
```

### Manual Step-by-Step

If you prefer to run stages individually:

**Stage 1: Create batch requests (all files in data/papers/)**
```bash
python create_batch.py
```

Or process specific files:
```bash
python create_batch.py --files doc1.pdf doc2.docx
```

Or process custom directory:
```bash
python create_batch.py --input-dir /custom/path/
```

Output: `batch_requests_{timestamp}.jsonl`

**Stage 2: Submit batch**
```bash
python submit_batch.py
```
Output: `batch_id.txt` with job ID

**Stage 3: Poll and process**
```bash
python poll_and_process.py
```
Output: Individual summaries in `data/summaries/`

### Monitoring Progress

The polling script shows real-time status:
```
[2026-01-25 14:32:15] Status: in_progress | Progress: 12/35
[2026-01-25 14:32:45] Status: in_progress | Progress: 24/35
[2026-01-25 14:33:15] Status: completed | Progress: 35/35

✓ Batch completed successfully!
```

Press `Ctrl+C` to stop polling. Run the script again to resume.

## Project Structure

```
batch_summary_doubleword/
├── README.md                           # This file
├── pyproject.toml                      # Python dependencies (uv)
├── requirements.txt                    # Python dependencies (pip)
├── .env.sample                         # Environment variable template
├── .gitignore                          # Git ignore rules
├── run_batch_pipeline.py               # Orchestrator script (Python)
├── summarisation_prompt.txt            # Prompt template for summaries
├── create_batch.py     # Stage 1: PDF extraction
├── submit_batch.py                     # Stage 2: Batch submission
├── poll_and_process.py                 # Stage 3: Polling and processing
├── process_results.py                  # Result processing
└── data/
    ├── papers/                         # Input PDFs
    └── summaries/                      # Output summaries (auto-created)
```

**Generated files (not in git):**
- `batch_requests_YYYYMMDD_HHMMSS.jsonl` - JSONL file with timestamped batch requests
- `batch_id_YYYYMMDD_HHMMSS.txt` - Timestamped batch job ID
- `data/summaries/*.md` - Individual paper summaries

## Configuration Options

### Polling Interval

Adjust how frequently the script checks batch status:

```bash
# In .env file
POLLING_INTERVAL=60  # Check every 60 seconds
```

Lower values = faster notification, more API calls
Higher values = fewer API calls, slower notification

**Recommended:** 30-60 seconds for most use cases

### Model Selection

The default model is `Qwen/Qwen3-VL-235B-A22B-Instruct-FP8`, which supports:
- Long context windows (128K+ tokens)
- Vision capabilities (for PDFs with charts/diagrams)
- Structured output generation

To use a different model, update `DOUBLEWORD_MODEL` in `.env`.

### Completion Window / SLA

The batch job completion window determines how long the API has to complete your job. Configure via `COMPLETION_WINDOW` in `.env`:

```bash
COMPLETION_WINDOW=1h  # Options: "1h" or "24h"
```

Doubleword typically completes jobs much faster than the window:
- 2 papers: ~1 minute
- 35 papers: ~30 minutes

Use `1h` for most cases. Use `24h` if you want even cheaper pricing and if task is not as time critical.

## Cost Estimation

Based on actual usage (Jan 2026):
- **35 papers** (mixed lengths, 45-200 pages each)
- **Model:** Qwen3-VL-235B-A22B-Instruct-FP8
- **Cost:** ~15 pence total (~0.43p per paper)

Cost varies by:
- Document length
- Requested summary length
- Model selected
- Number of requests

## Troubleshooting

### Authentication Errors

```
Error: Unauthorized
```
**Solution:** Check your `DOUBLEWORD_AUTH_TOKEN` in `.env`

### Batch Takes Too Long

**Solution:** Doubleword typically completes in ~1 minute. If waiting longer:
1. Check Doubleword portal for job status
2. Verify your completion window setting
3. Contact Doubleword support if job is stuck

### Process Results Error

```
✗ Error processing results
```
**Solution:** Check that `process_results.py` has correct permissions and paths

## Extending the Pipeline

### Adding New Data Sources

Use the `--input-dir` option to process files from any directory:

```bash
python run_batch_pipeline.py --input-dir /path/to/your/documents/
```

Or process specific files regardless of location:
```bash
python run_batch_pipeline.py --files /path/to/file1.pdf /other/path/file2.docx
```

### Customizing Output Format

Edit `summarisation_prompt.txt` to change:
- Summary structure
- Required fields
- Output length
- Technical depth

### Changing Output Directory

Edit `process_results.py` line 37:
```python
summaries_dir = Path('output/my_summaries')  # Custom location
```

## Technical Stack

- **Python 3.12+** - Core runtime
- **pypdf** - Primary PDF text extraction
- **pdfplumber** - Fallback extraction for complex PDFs
- **python-docx** - Microsoft Word document extraction
- **python-pptx** - PowerPoint presentation extraction
- **odfpy** - OpenDocument format extraction
- **OpenAI SDK** - API client (Doubleword API is OpenAI-compatible)
- **Doubleword API** - Batch inference backend
- **Qwen3-VL-235B** - Vision-language model for document understanding

## Acknowledgments

Built using:
- [Doubleword AI](https://app.doubleword.ai/models?page=1) - Batch inference platform
- [Qwen3-VL] - Open-weight vision-language model provided by Doubleword
- OpenAI-compatible API standard for seamless integration

## License

MIT License - see LICENSE file for details

## Next Steps
- Try out streaming feature
- Test the model's vision capabilities
- LLM as a Judge  - this is often token intensive and async and so a good candidate for batch inference
- Add temperature, top_p, top_k, frequency penalty, presence penalty etc to .env or config file 

## Related Concepts

- **Batch inference** - Processing multiple requests efficiently
- **Open-weight models** - Qwen3, DeepSeek, Llama alternatives to proprietary models
- **Structured output** - JSON/markdown formatted LLM responses
- **Document intelligence** - AI-powered document analysis at scale
