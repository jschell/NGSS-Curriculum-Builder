# NGSS Curriculum Builder - Project Context

## Project Overview

**Name**: NGSS Curriculum Builder
**Purpose**: Grade-agnostic K-12 science standards tracking system for all 51 US states/jurisdictions
**Status**: Production-ready metadata system; document parsing in development

**Core Functionality**:
- Query state science standards by grade level across all 51 jurisdictions
- Track NGSS direct adoption (21 states) vs. framework-based standards (30 states)
- Catalog 101 standards documents and 67 state assessments
- Fast metadata queries (<20ms) with future document parsing capability

---

## Technology Stack

### Core Technologies
- **Language**: Python 3.10+
- **Package Manager**: UV (for inline script dependencies)
- **Dependencies**: Stdlib only for CLI; UV inline deps for parsing scripts
- **Data Format**: JSON (external data storage)
- **Architecture**: Two-tier (fast metadata + lazy content loading)

### Project Structure
```
NGSS-Curriculum-Builder/
├── state_science_standards_system.py  # Main CLI (609 lines)
├── parse_standards.py                 # Document parser (639 lines)
├── validate_urls.py                   # URL validation (434 lines)
├── data/
│   └── states.json                    # 51 states data (111 KB)
├── .claude/
│   ├── guide.md                       # Obra workflow guide (824 lines)
│   ├── CLAUDE.md                      # This file (project context)
│   ├── plan/
│   │   ├── active/                    # Current implementation plans
│   │   └── complete/                  # Completed plans archive
│   ├── commands/                      # Slash commands
│   └── skills/obra/                   # Obra autonomous skills
├── docs/                              # Technical documentation
├── features.txt                       # Feature backlog
└── progress.txt                       # Session execution log
```

---

## Core Development Rules

### 1. Test-Driven Development
- **Always test before adding features**: Run CLI commands to verify current behavior
- **Test after changes**: Validate that new code works before committing
- **No breaking changes**: Maintain backward compatibility with existing queries

### 2. Commit Discipline
- **Format**: Conventional commits (feat:, fix:, docs:, refactor:, test:)
- **Frequency**: Commit after each logical unit of work completes
- **Message structure**:
  ```
  <type>(<scope>): <short description>

  <optional longer description>
  <optional breaking changes>

  https://claude.ai/code/session_<ID>
  ```
- **Examples**:
  - `feat(parser): add PDF page range extraction`
  - `fix(validation): handle 404 errors gracefully`
  - `docs(readme): add installation instructions`

### 3. Data Integrity
- **Never modify data/states.json directly**: Use validation/update scripts
- **Always validate**: Run validation before updating JSON
- **Preserve structure**: Maintain consistent field naming and types
- **No data loss**: Keep all existing fields when adding new ones

### 4. Code Quality
- **Type hints**: Use dataclasses and type annotations
- **No external deps for CLI**: Keep core tool dependency-free
- **Modular design**: Clear separation of concerns
- **Error handling**: Graceful failures with helpful messages

---

## Test Commands

### CLI Functionality Tests
```bash
# Test: List all states
python state_science_standards_system.py list

# Test: Search by grade
python state_science_standards_system.py search 5

# Test: State info
python state_science_standards_system.py state WA

# Test: State info with grade filter
python state_science_standards_system.py state CA 8

# Test: K-12 coverage
python state_science_standards_system.py range TX

# Test: Compare states for grade
python state_science_standards_system.py compare 3

# Test: Research queries
python state_science_standards_system.py queries NY 6
```

### Parser Tests
```bash
# Test: Parse standards document
uv run parse_standards.py

# Expected: Auto-generate grade section mappings from PDFs/HTML
```

### Validation Tests
```bash
# Test: Validate all URLs
uv run validate_urls.py

# Expected: Check all 80 document URLs, report 404/403 errors
```

### Data Integrity Tests
```bash
# Verify JSON structure
python -c "import json; json.load(open('data/states.json'))"

# Count states
python -c "import json; print(len(json.load(open('data/states.json'))))"
# Expected: 51

# Count documents
python -c "import json; data=json.load(open('data/states.json')); print(sum(len(s['documents']) for s in data.values()))"
# Expected: 80
```

---

## Autonomous Workflow Modes

### Mode 1: Planning (Human-in-Loop)
**When to use**: New features, architectural decisions, ambiguous requirements

**Process**:
1. Read feature from `features.txt`
2. Create detailed plan in `.claude/plan/active/<feature-name>.md`
3. Review plan with human
4. Wait for approval before execution

**Plan Structure**:
- Feature description
- Prerequisites
- Step-by-step implementation
- Test strategy
- Success criteria
- Rollback plan

### Mode 2: Execution (Fully Autonomous)
**When to use**: Approved plans, repetitive tasks, well-defined work

**Process**:
1. Load plan from `.claude/plan/active/`
2. Execute steps sequentially
3. Run tests after each step
4. Auto-commit successful changes
5. Update progress.txt continuously
6. Move completed plan to `.claude/plan/complete/`

**Execution Loop**:
```
FOR each step in plan:
  1. Execute step
  2. Run relevant tests
  3. IF tests pass:
       - Commit changes
       - Log progress
       - Continue to next step
     ELSE:
       - STOP and alert human
       - Document failure
       - Wait for intervention
```

---

## Stop Conditions (When to Ask for Help)

**STOP and alert human if**:

### 1. Security Issues
- Credentials or API keys needed
- Authentication changes required
- Data privacy concerns
- External API access needed

### 2. Test Failures
- 3 consecutive test failures
- Breaking existing functionality
- Test coverage drops below 75%
- Critical CLI commands fail

### 3. Architectural Decisions
- Major refactoring needed
- Technology stack changes
- New external dependencies
- Database schema changes

### 4. Data Issues
- Ambiguous state standards information
- Conflicting documentation
- Missing critical data (>5 states)
- URL validation failures (>10 broken links)

### 5. Ambiguous Requirements
- Feature scope unclear
- Multiple implementation approaches
- User preference needed
- Design decisions required

### 6. External Dependencies
- State education websites down
- PDF documents unavailable
- HTML structure changed significantly
- Rate limiting encountered

---

## Obra Skills Integration

### Writing Plans Skill
**File**: `.claude/skills/obra/writing-plans.md`

**When to invoke**:
- User requests new feature from backlog
- Complex multi-step implementation needed
- Slash command `/plan-feature <name>` called

**Expected output**: Detailed implementation plan in `.claude/plan/active/`

### Executing Plans Skill
**File**: `.claude/skills/obra/executing-plans.md`

**When to invoke**:
- Plan approved and ready for execution
- Slash command `/execute-next` called
- Slash command `/work` called (autonomous loop)

**Expected output**:
- Code changes committed
- Tests passing
- Progress logged
- Plan moved to complete/

---

## Project-Specific Context

### Current State (As of 2026-02-19)
- ✅ 51/51 states complete with metadata
- ✅ 100 documents cataloged
- ✅ 70 assessments tracked
- ✅ JSON data structure (111 KB)
- ✅ CLI tool fully functional
- ✅ PDF/HTML parser implemented
- ✅ URL validation utility created
- ✅ grade_sections data with confidence scoring (35/51 states)
- ✅ page_range_status on all 100 documents (zero missing)
- ✅ Texas K-12 complete (17 docs: K-8 individual + 8 HS courses, all extracted)
- ✅ Mississippi K-12 extracted (TOC parsing 2026-02-19)
- ✅ Virginia correctly classified as not_applicable_multi_document (13 per-grade docs)
- ❌ No document content caching
- ❌ No full-text search
- ❌ No export functionality (CSV/Excel)
- ❌ No web API or interface

### Known Issues
1. **Pending Extraction** (10 docs, all accessible):
   - CA: grades 2-5 individual PDFs (status=pending)
   - NY: grades 6-8 and HS PDFs (status=pending)
   - KY: HS course standards (status=pending)
   - NJ: grades 6-12 PDF (status=pending)
   - WA: 2 alternative arrangement docs (DCI, Topic — lower priority)

3. **Performance Considerations**:
   - Metadata queries: <20ms ✅ Fast
   - Document parsing: 1-5 seconds per PDF ⚠️ Slower
   - Full database parse: ~195 seconds ⚠️ Needs caching

### Next Priority Work
(See `features.txt` for full backlog)

**High Priority**:
1. Extract TX HS course page ranges (8 short PDFs, likely accessible)
2. VA extraction via manual browser download (see holding plan)

**Medium Priority**:
3. Implement document content caching
4. Add full-text search across standards
5. Create CSV/Excel export functionality

---

## Development Patterns

### Adding a New State
1. Research state education agency website
2. Find science standards page
3. Identify NGSS status (direct_adoption or framework_based)
4. Catalog all K-12 documents
5. Add assessment information
6. Update data/states.json
7. Run validation tests
8. Commit with message: `feat(data): add <State> science standards`

### Adding Document Parsing
1. Identify document format (PDF, HTML, Excel)
2. Choose appropriate parser (pypdf, BeautifulSoup4, openpyxl)
3. Extract text for specific grades/pages
4. Parse standards structure
5. Cache parsed content
6. Update data structure with cache references
7. Test parsing with sample documents
8. Commit with message: `feat(parser): add <format> document parsing`

### Fixing Broken URLs
1. Run `uv run validate_urls.py` to identify broken links
2. Research current state education website
3. Find replacement URLs
4. Update data/states.json
5. Re-run validation to confirm fixes
6. Commit with message: `fix(data): update broken URLs for <states>`

---

## Quick Reference

### File Locations
- **Main CLI**: `state_science_standards_system.py`
- **State data**: `data/states.json`
- **Feature backlog**: `features.txt`
- **Session log**: `progress.txt`
- **Active plans**: `.claude/plan/active/`
- **Completed plans**: `.claude/plan/complete/`

### Key Functions
- `load_states_data()` - Load JSON and convert to dataclasses
- `expand_grade_range()` - Expand "K-12" to array
- `get_documents_for_grade()` - Filter documents by grade
- `get_coverage_summary()` - K-12 coverage analysis

### Data Counts
- States: 51
- Documents: 101
- Assessments: 67
- NGSS states: 21
- Framework states: 30

---

## Notes for Claude

- This is a **production-ready metadata system** with document parsing in development
- Prioritize **data integrity** - never lose existing information
- Keep **CLI fast** - metadata queries must stay under 100ms
- Use **lazy loading** for document parsing - don't slow down metadata queries
- Follow **conventional commits** - clear, descriptive messages
- **Stop and ask** if security, architecture, or data issues arise
- **Test everything** - this is educational infrastructure, accuracy matters
- Reference the **Obra guide** (`.claude/guide.md`) for autonomous workflow details
