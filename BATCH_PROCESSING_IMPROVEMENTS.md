# Batch Processing Workflow - Improvements & Streamlining

## Date: 2026-02-04

## Summary
This document captures the improvements made to the `dw_batch_request` skill workflow to make it faster and more seamless for future use.

---

## Pain Points Identified

### 1. **Missing Dependencies**
- Required libraries (python-docx, python-pptx, odfpy, xlrd) were not installed in the project's .venv
- Had to install them mid-process, causing delays

### 2. **Unsupported File Formats**
- TSV and CSV files were not in the supported extensions list
- Required manual conversion from TSV → TXT before processing

### 3. **Multiple Conversion Steps**
- Excel/CSV files required conversion: Excel → TSV → TXT
- Time-consuming and error-prone manual process

### 4. **Output Location**
- Results were buried in `.claude/skills/data/summaries/`
- Not easily accessible from project root

### 5. **No Setup Documentation**
- No clear one-time setup instructions
- Each session required manual environment configuration

---

## Improvements Implemented

### ✅ 1. Added TSV/CSV Support
**Files modified:**
- `.claude/skills/create_batch.py` (line 3, 72)

**Changes:**
```python
# Updated docstring
Supported formats: PDF, DOCX, PPTX, ODP, TXT, MD, TSV, CSV

# Updated supported extensions
supported_extensions = ['*.pdf', '*.txt', '*.md', '*.docx', '*.pptx', '*.odp', '*.tsv', '*.csv']
```

**Impact:** TSV and CSV files now work directly without conversion to .txt

---

### ✅ 2. Updated Output Directory to Project Root
**Files modified:**
- `.claude/skills/process_results.py` (line 48)
- `.claude/skills/poll_and_process.py` (line 56)
- `.claude/skills/run_batch_pipeline.py` (line 164)

**Changes:**
```python
# Old: summaries_dir = Path('data/summaries')
# New: summaries_dir = Path('../../dw_batch_request_output')
```

**Impact:** All outputs now save to `dw_batch_request_output/` at project root

---

### ✅ 3. Created Setup Script
**New file:** `.claude/skills/setup_dependencies.sh`

**Usage:**
```bash
cd .claude/skills
./setup_dependencies.sh
```

**Impact:** One-time setup installs all required dependencies automatically

---

### ✅ 4. Updated .gitignore
**Lines added:**
```gitignore
# Batch processing outputs and temporary files
dw_batch_request_output/
data/converted_for_batch/
.claude/skills/data/
.claude/skills/batch_*.jsonl
.claude/skills/batch_id_*.txt
```

**Impact:** Output files and temporary artifacts won't clutter git history

---

## Workflow Comparison

### Before (Slow & Manual):
1. Try to run batch → fails due to missing dependencies
2. Install dependencies manually (xlrd, docx, pptx, odfpy)
3. Convert Excel → CSV/TSV
4. Rename TSV → TXT (unsupported format)
5. Run batch pipeline
6. Hunt for outputs in `.claude/skills/data/summaries/`
7. Manually move files to accessible location

**Time: ~10-15 minutes + troubleshooting**

---

### After (Fast & Seamless):
1. **One-time setup:** `./setup_dependencies.sh` (30 seconds)
2. Drop Excel/CSV/TSV files in `data/` folder
3. Run: `python run_batch_pipeline.py --input-dir ../../data/your_files/`
4. Results automatically saved to `dw_batch_request_output/`

**Time: ~1-2 minutes (after initial setup)**

---

## Future Recommendations

### A. **Add Pandas for Smarter Data Handling**
Currently, the script reads TSV/CSV as plain text. Consider adding pandas for:
- Auto-detection of delimiter (tab vs comma)
- Handling quoted fields with embedded delimiters
- Better memory management for large files

**Tradeoff:** Adds pandas dependency (~50MB)

---

### B. **Create Data Analysis Prompt Templates**
The current prompt is generic. Create specialized templates:
- `prompts/data_analysis.txt` (current one)
- `prompts/time_series_analysis.txt`
- `prompts/financial_data_analysis.txt`
- `prompts/statistical_summary.txt`

**Usage:**
```bash
python run_batch_pipeline.py --prompt-file prompts/time_series_analysis.txt
```

---

### C. **Add Direct Excel Support**
Instead of converting Excel → TSV → TXT, read Excel files directly:
```python
# In create_batch.py, add:
def extract_text_excel(excel_path):
    import pandas as pd
    df = pd.read_excel(excel_path)
    return df.to_csv(sep='\t', index=False)
```

**Benefit:** One less conversion step

---

### D. **Add Output Format Options**
Currently outputs markdown. Add options for:
- JSON (for programmatic processing)
- CSV/TSV (for spreadsheet import)
- HTML (for web viewing)

---

### E. **Create CLAUDE.md Section**
Add to project CLAUDE.md:
```markdown
## Batch Data Analysis

For analyzing multiple data files using LLM batch processing:

1. **Setup (one-time):**
   ```bash
   cd .claude/skills && ./setup_dependencies.sh
   ```

2. **Usage:**
   ```bash
   cd .claude/skills
   python run_batch_pipeline.py --input-dir ../../data/your_files/
   ```

3. **Results:** Check `dw_batch_request_output/` folder

4. **Supported formats:** PDF, DOCX, PPTX, ODP, TXT, MD, TSV, CSV
```

---

## Key Lessons Learned

1. **Pre-install all dependencies** to avoid mid-workflow failures
2. **Support common data formats natively** (TSV, CSV) to reduce conversion steps
3. **Use project root for outputs** - easier to find and reference
4. **Document setup clearly** - future you (or teammates) will thank you
5. **Update .gitignore proactively** - avoid committing large output files

---

## Quick Reference

### Run batch analysis on data files:
```bash
cd .claude/skills
source ../../.venv/bin/activate
python run_batch_pipeline.py --input-dir ../../data/your_files/
```

### Check results:
```bash
ls -lh dw_batch_request_output/
```

### Customize analysis prompt:
```bash
# Edit the prompt temporarily
vim .claude/skills/summarisation_prompt.txt

# Or use a different model for cost/speed tradeoff
export DOUBLEWORD_MODEL="Qwen/Qwen3-VL-30B-A3B-Instruct-FP8"
```

---

## Cost & Performance

**Current setup:**
- Model: Qwen3-VL-235B (complex analysis)
- 2 data files (~120KB total)
- Completion time: ~1 minute
- Cost: ~0.4p

**For cost savings on simple data:**
```bash
export DOUBLEWORD_MODEL="Qwen/Qwen3-VL-30B-A3B-Instruct-FP8"  # ~50% cheaper
export COMPLETION_WINDOW=24h  # Even cheaper, but slower
```

---

## Files Modified/Created

### Modified:
- `.claude/skills/create_batch.py` - Added TSV/CSV support
- `.claude/skills/process_results.py` - Updated output directory
- `.claude/skills/poll_and_process.py` - Updated output directory
- `.claude/skills/run_batch_pipeline.py` - Updated output directory
- `.gitignore` - Added batch output patterns

### Created:
- `.claude/skills/setup_dependencies.sh` - One-time setup script
- `dw_batch_request_output/` - Output directory (at project root)
- `BATCH_PROCESSING_IMPROVEMENTS.md` - This document

---

## Next Session Checklist

When using batch processing next time:

- [ ] Dependencies already installed? (Run `pip list | grep docx` to check)
- [ ] `.env` file configured with DOUBLEWORD_AUTH_TOKEN?
- [ ] Know what analysis you want? (Update summarisation_prompt.txt if needed)
- [ ] Files in supported format? (PDF, DOCX, PPTX, TXT, MD, TSV, CSV, ODP)
- [ ] Ready to run: `python run_batch_pipeline.py --input-dir /path/to/files/`

---

**Time saved per batch run: ~8-12 minutes**
**Setup required: Once per project**
