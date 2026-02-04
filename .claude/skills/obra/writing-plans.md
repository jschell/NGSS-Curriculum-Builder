# Obra Skill: Writing Plans

## Skill Objective

Transform high-level feature descriptions into detailed, executable implementation plans that can be executed autonomously with clear validation gates and rollback strategies.

## When to Invoke This Skill

- User requests `/plan-feature` command
- User requests `/batch-plan` command
- A feature from features.txt needs detailed planning
- Complex multi-step implementation required
- Before starting autonomous execution with `/work`

## Input Requirements

**Required:**
- Feature description (from features.txt or user input)
- Project context (from `.claude/CLAUDE.md`)
- Current codebase state (git status, file structure)

**Optional:**
- Existing code to modify
- Related features or dependencies
- Constraints or requirements
- Template to base plan on

## Execution Steps

### Step 1: Understand Context

1. Read `.claude/CLAUDE.md` for:
   - Technology stack
   - Core development rules
   - Test commands
   - Commit message format
   - Stop conditions
2. Read features.txt to understand:
   - Feature position in backlog
   - Related features
   - Dependencies
3. Review current codebase:
   - Relevant files that will be modified
   - Existing patterns to follow
   - Test structure
4. Check for existing plans:
   - Active plans that might conflict
   - Completed plans with similar patterns
   - Templates that might apply

### Step 2: Analyze Feature Scope

1. Break down the feature into logical components
2. Identify:
   - Prerequisites (dependencies, configs, installs)
   - Files to create
   - Files to modify
   - Tests required
   - Documentation updates
3. Estimate complexity:
   - Simple: 1-3 steps, < 1 hour
   - Medium: 4-7 steps, 1-3 hours
   - Complex: 8+ steps, > 3 hours
4. Flag if scope seems too large:
   - Suggest breaking into multiple features
   - Identify natural split points

### Step 3: Design Implementation Steps

For each logical component, create a step with:

**Step Structure:**
```markdown
### Step N: [Clear, actionable description]

**Action:** What to do
**Files to create:** List new files (if any)
**Files to modify:** List existing files to change
**Tests required:** Specific test files/cases
**Validation:** How to verify success (commands to run)
**Commit message:** Conventional commit format
**Expected duration:** Estimate (optional)
```

**Step Ordering:**
1. Prerequisites first (installs, configs)
2. Core functionality before polish
3. Tests alongside or after each major change
4. Documentation last
5. Each step should be committable

**Step Granularity:**
- Each step should take 5-30 minutes
- Each step should be testable independently
- Each step should result in a clean commit
- Avoid steps that are too small (1 line changes)
- Avoid steps that are too large (> 200 lines)

### Step 4: Define Validation Strategy

For the plan overall:

**Prerequisites Checklist:**
- [ ] List all dependencies that must exist
- [ ] List all configurations needed
- [ ] List all access/permissions required

**Test Strategy:**
- Identify which tests to run after each step
- Define new test cases needed
- Specify test coverage goals (> 80%)
- Include integration test requirements

**Success Criteria:**
- [ ] All tests pass
- [ ] No linting errors
- [ ] Code formatted properly
- [ ] Feature works end-to-end
- [ ] Documentation complete
- [ ] Committed with proper messages

### Step 5: Plan for Failure

**Rollback Plan:**
```bash
# Commands to undo changes if needed
git revert HEAD~N..HEAD  # N = number of commits
# File deletions if needed
# Config restoration if needed
```

**Potential Blockers:**
- List known risks or uncertainties
- Identify external dependencies
- Flag areas needing human decision
- Note stop conditions that might trigger

### Step 6: Format and Save Plan

**Plan Format:**
```markdown
# Plan: [Feature Name]

**Status:** Not Started
**Created:** YYYY-MM-DD
**Estimated Duration:** X hours
**Priority:** High/Medium/Low

---

## Context

[2-3 sentences: What is this feature and why are we building it?]

[Reference to features.txt if applicable]

---

## Prerequisites

- [ ] Dependency X installed
- [ ] Config Y updated
- [ ] Access to Z available
- [ ] Tests currently passing

**Verification:**
```bash
[Commands to verify prerequisites]
```

---

## Implementation Steps

### Step 1: [Description]
**Action:** [What to do]
**Files to create:** [List or "None"]
**Files to modify:** [List or "None"]
**Tests required:** [Specific test files]
**Validation:** [How to verify]
```bash
[Test commands]
```
**Commit message:** `[type]([scope]): [description]`

### Step 2: [Description]
[Same structure...]

[... more steps ...]

---

## Validation Strategy

**After Each Step:**
- Run relevant tests
- Verify no regressions
- Check code quality

**Final Validation:**
```bash
[Full test suite command]
[Linting command]
[Build command if applicable]
```

---

## Success Criteria

- [ ] All tests pass
- [ ] Test coverage > 80%
- [ ] No linting errors
- [ ] Feature works end-to-end
- [ ] Documentation updated
- [ ] All commits follow convention

---

## Rollback Plan

**If execution fails:**
```bash
git revert HEAD~N..HEAD  # Revert N commits
[Other restoration commands]
```

**Files to restore:**
- [List files that might need manual restoration]

---

## Potential Blockers

- [ ] [Known risk or uncertainty #1]
- [ ] [External dependency #2]
- [ ] [Decision point #3]

**Stop Conditions:**
- If [condition], stop and ask human
- If [condition], stop and ask human

---

## Notes

[Any additional context, links, or references]
```

**Save Location:**
- File: `.claude/plan/active/[feature-slug].md`
- Slug format: lowercase, hyphens, descriptive
- Examples: `user-authentication.md`, `pdf-parser.md`, `url-validation.md`

### Step 7: Link Plan to Feature

Update features.txt:
```markdown
## Todo
- [ ] User authentication → .claude/plan/active/user-authentication.md
```

## Output Format

After creating the plan, provide a summary:

```
✓ Created plan: .claude/plan/active/[feature-slug].md

Plan Summary:
- Steps: N implementation steps
- Duration: Estimated X hours
- Dependencies: [List or "None"]
- Tests: N new test cases required
- Commits: N planned commits
- Complexity: Simple/Medium/Complex

Key Steps:
1. [Brief description of step 1]
2. [Brief description of step 2]
...

Prerequisites:
- [List prerequisites to verify]

Potential Blockers:
- [List any identified risks]

Review the plan at .claude/plan/active/[feature-slug].md
Run /execute-next when ready to proceed.
```

## Validation Criteria

A good plan has:

- [ ] Clear, actionable steps (not vague)
- [ ] Each step is independently testable
- [ ] Each step has validation command
- [ ] Commit messages follow convention
- [ ] Prerequisites clearly listed
- [ ] Rollback strategy defined
- [ ] Success criteria measurable
- [ ] Potential blockers identified
- [ ] Test strategy comprehensive
- [ ] File paths are specific

## Error Handling

**If feature is too vague:**
- Ask clarifying questions
- Suggest breaking into smaller features
- Request more context from user

**If dependencies are missing:**
- Add to prerequisites
- Flag for human to resolve first
- Suggest prerequisite features

**If scope is too large:**
- Suggest splitting into multiple features
- Propose logical break points
- Estimate time honestly (don't underestimate)

## Notes

- **Planning is thoughtful, execution is mechanical** - Invest time in good plans
- **Plans are living documents** - Can be adjusted during execution
- **Better to over-specify than under-specify** - Autonomous execution needs detail
- **Include examples** - If pattern is not obvious, show code examples in plan
- **Consider the autonomous executor** - Write plans for a careful but literal interpreter

## Integration with Project

**For NGSS Curriculum Builder specifically:**

- Technology stack: Python 3.10+, stdlib, UV for scripts
- Test pattern: Run CLI commands to verify
- Data integrity: Always validate data/states.json
- Performance: Keep metadata queries < 100ms
- Commit format: `feat(scope): description`
- Stop conditions: Security, data integrity, external dependencies

**Common plan types:**
1. URL validation and fixing
2. Data addition/correction
3. Parser enhancements
4. New CLI commands
5. Export functionality
6. Search features

**Project-specific validation:**
```bash
# Verify state data integrity
python -c "import json; json.load(open('data/states.json'))"

# Test CLI commands
python state_science_standards_system.py list
python state_science_standards_system.py search 5

# Run parser tests
uv run parse_standards.py

# Validate URLs
uv run validate_urls.py
```
