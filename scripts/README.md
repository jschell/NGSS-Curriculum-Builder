# Scripts Directory

Organized collection of tools for working with the NGSS Curriculum Builder data.

---

## Directory Structure

```
scripts/
├── parsing/          # Document parsing and extraction tools
├── validation/       # Data validation and URL checking
├── research/         # Research and investigation utilities
└── README.md         # This file
```

---

## Parsing Tools

### `parsing/parse_standards.py`

**Purpose:** Core automated parser for extracting grade-level page ranges from state standards PDFs.

**Usage:**
```bash
cd scripts/parsing
uv run parse_standards.py parse --states WA,OR,CA
uv run parse_standards.py parse --all
uv run parse_standards.py report patches/grade_sections.json
```

**Features:**
- Automated PDF text extraction with pypdf
- Pattern matching for grade level markers
- Generates JSON patches for states.json
- Creates human-readable analysis reports

**Success Rate:** ~60-70% for standard document structures

**See Also:** `docs/LESSONS_LEARNED.md` for parsing patterns and approaches

---

## Validation Tools

### `validation/validate_urls.py`

**Purpose:** Check accessibility of all document URLs in states.json

**Usage:**
```bash
cd scripts/validation
uv run validate_urls.py
```

**Output:**
- Lists broken URLs (404, 403, connection errors)
- Identifies states needing URL updates
- Validates SSL certificates

**Use Case:** Run before major data updates or after state agencies update their websites

---

### `validation/apply_page_ranges.py`

**Purpose:** Apply extracted page range patches to states.json

**Usage:**
```bash
cd scripts/validation
uv run apply_page_ranges.py [patch_file.json]
```

**Default:** Reads from `patches/grade_sections.json` if no file specified

**Function:**
- Merges grade section data from patch files into states.json
- Validates data structure before writing
- Creates backup of states.json
- Reports statistics on updated states

**Safety:** Always test on a copy of states.json first

---

## Research Tools

### `research/batch3_research.py`

**Purpose:** Example script for batch URL research using MCP browser tools

**Features:**
- Demonstrates brave_web_search integration
- Shows browser navigation patterns
- URL verification workflows

**Use Case:** Reference implementation for finding alternative URLs when state websites change

---

### `research/research_state_urls_browser.py`

**Purpose:** Interactive browser-based research for finding state standards URLs

**Features:**
- MCP browser tool integration examples
- Handles bot-protected websites
- Visual verification patterns

**Use Case:** Template for investigating hard-to-access state documents

---

## Usage Patterns

### Standard Workflow

1. **Validate URLs** (before starting)
   ```bash
   cd scripts/validation
   uv run validate_urls.py
   ```

2. **Parse Documents**
   ```bash
   cd scripts/parsing
   uv run parse_standards.py parse --states TX,FL,NY
   ```

3. **Review Generated Patch**
   ```bash
   cat patches/grade_sections.json
   cat reports/grade_sections_analysis.md
   ```

4. **Apply Patch** (if satisfied)
   ```bash
   cd scripts/validation
   uv run apply_page_ranges.py
   ```

---

## Dependencies

All scripts use **UV inline dependencies** for easy execution without global installations:

```python
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pypdf>=4.0.0",
#     "httpx>=0.24.0",
# ]
# ///
```

**Run with:** `uv run script_name.py`

**UV Installation:** https://docs.astral.sh/uv/

---

## Adding New Scripts

When adding new tools to this directory:

1. **Choose appropriate subdirectory:**
   - `parsing/` - Extract data from documents
   - `validation/` - Check data integrity
   - `research/` - Investigation and discovery tools

2. **Use UV inline dependencies:**
   ```python
   #!/usr/bin/env -S uv run
   # /// script
   # requires-python = ">=3.10"
   # dependencies = ["package>=1.0.0"]
   # ///
   ```

3. **Add documentation:**
   - Update this README with script description
   - Include usage examples
   - Document expected inputs/outputs

4. **Follow conventions:**
   - Use argparse for CLI arguments
   - Output to stdout or files in `patches/`, `reports/`
   - Return non-zero exit codes on errors

---

## See Also

- **Main CLI:** `state_science_standards_system.py` (project root)
- **Parsing Guide:** `docs/LESSONS_LEARNED.md`
- **Project Context:** `.claude/CLAUDE.md`
