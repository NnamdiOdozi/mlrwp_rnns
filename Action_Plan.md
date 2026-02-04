## Improvement points to hand to an assistant (ordered by impact)

### 1) Clarify the “contract” and audience

* Rewrite the top of `SKILL.md` so it is unambiguous whether this is a **Claude Code skill**, a **general repo utility**, or both.
* Add a crisp **Contract** section: inputs (files), required configuration (environment variables), outputs (folder + naming), failure behaviour (skip versus stop), and what “success” means.
* Add a one-paragraph “Who this is for” and “What you need installed”.

### 2) Add a one-page Quick Start that works for 80 percent of users

* Put a “Quick Start (5 minutes)” at the very top: install dependencies, set `.env`, edit `prompt.txt`, run create → submit → poll, find outputs.
* Keep it platform-friendly (Linux, macOS, and Windows PowerShell examples if possible).
* Remove repo-specific relative paths (`../../data`) from the Quick Start; use explicit `--input-dir` and `--output-dir` examples.

### 3) Make portability real: remove path assumptions and parameterise directories

* Ensure scripts support `--input-dir`, `--output-dir`, `--logs-dir` with safe defaults that stay inside the project.
* Ensure outputs are deterministic and consistent regardless of where the user runs from (working directory).
* Print absolute paths at runtime so users can find results quickly.

### 4) Tighten claims and clearly separate “supported now” from “planned”

* Audit the “Supported File Formats” and “OCR/handwritten/scanned PDF” statements.
* Explicitly distinguish:

  * Text-based PDFs (pypdf/pdfplumber).
  * Image-based PDFs (requires rasterisation + vision, if not implemented mark as “planned”).
* Remove or soften any “tested successfully” claims that are not reproducible by a stranger running the repo.

### 5) Security and secrets hardening (public sharing readiness)

* Add “Security” section:

  * `.env` and `logs/` must be in `.gitignore`.
  * Never log or write tokens into JSONL or debug output.
  * Document safe key handling patterns and what users should never commit.
* Add a preflight check that errors if `DOUBLEWORD_AUTH_TOKEN` is missing, but never prints it.

### 6) Add cost guardrails that are actionable, not just educational

* Add a `--dry-run` mode (or a separate script) that estimates:

  * How many files will be processed.
  * Approximate token counts per file (even a rough heuristic is better than nothing).
  * Expected maximum output tokens (from `MAX_TOKENS`) and a “worst-case” cost band.
* Add a “human approval” step for large jobs:

  * For example, require confirmation if file count > N or if estimated cost > £X.

### 7) Improve idempotency and rerun safety

* Ensure reruns do not silently duplicate costs by default.
* Add an optional `--resume` or `--skip-existing` mode that checks if an output file already exists for an input file.
* Define a stable mapping: input file name + prompt hash + model + settings → output file name (or metadata file), so reruns are predictable.

### 8) Add lightweight quality checks on outputs

* For JSON extraction tasks, validate JSON and flag failures.
* For OCR/extraction, flag “empty / too short” outputs.
* Produce a summary report at the end: counts of success, skipped, failed, and where to find details.

### 9) Split `SKILL.md` from the long guide and move examples into `/examples`

* Keep `SKILL.md` short and “portal friendly”.
* Move the long receipt/invoice prompt, multimodal multi-doc example, and the deep cost math into:

  * `GUIDE.md` and/or `examples/receipt_json/`, `examples/multimodal/`.
* Keep a small “Examples index” in `SKILL.md` linking to those.

### 10) Make “Tier 1 vs Tier 2” decision rules more concrete

* Add a small decision table:

  * Same prompt/model/schema for all files → Tier 1.
  * Different prompts or schemas by type → Tier 2.
  * Human approval / high spend → Tier 2 + dry run.
* Provide a Tier 2 starter template script that is intentionally minimal and documented.

### 11) Provider and orchestrator friendliness

* Document the minimal assumptions needed for other orchestrators:

  * “This is a command-line pipeline. Any orchestrator can call these scripts.”
* If you intend portability beyond Doubleword later, add an internal concept of a “provider adapter” but do not implement fully yet.

### 12) Dependency management: prefer `uv run` for repeatable environments in Claude Code shells

* Add a recommended workflow using `uv` so users do not fight Python environments between multiple Claude Code shells:

  * Keep a `pyproject.toml` (or requirements) and a short section: “Run everything via `uv run …` so the environment is consistent.”
* Example commands to include in docs:

  * `uv sync` (or `uv pip install -r requirements.txt` if you stay requirements-based).
  * `uv run python create_batch.py --input-dir …`
  * `uv run python submit_batch.py`
  * `uv run python poll_and_process.py`
* Rationale to mention in one sentence: Claude Code often uses multiple shells, and `uv run` ensures the same resolved environment is used each time.


### 13) Safer approval workflow for expensive jobs

* A clear approval threshold (file count or estimated spend).
* A “review plan” output that shows what will be run before it is submitted.

### 14) Better multimodal support for image-based PDFs

* Add PDF page rasterisation (Poppler or PyMuPDF - which is more suitable) and a vision-first pipeline for scanned PDFs.
---

## Future improvements (later release, do not implement now)

### A) Sleeper agent / background processing

* Add an optional background mode that periodically checks for queued work.
* Strongly gate it with explicit user intent: only process jobs placed in a dedicated folder.

### B) Job manifest and queue semantics

* Introduce a `queue/` directory with one subfolder per job.
* Each job includes a `job.json` manifest specifying:

  * input paths, prompt, model, `MAX_TOKENS`, completion window, and expected outputs.
* Implement robust state transitions: `queued/ → in_progress/ → done/` and lock files to prevent double-processing.

