# Obra Skill: Executing Plans

## Skill Objective

Execute detailed implementation plans autonomously with rigorous validation, testing, and progress tracking at each step. Ensure code quality, maintain project integrity, and stop appropriately when human intervention is needed.

## When to Invoke This Skill

- User requests `/execute-next` command
- User requests `/work` command (executes plans in sequence)
- A plan in `.claude/plan/active/` is ready for implementation
- Prerequisites verified and plan reviewed by human

## Input Requirements

**Required:**
- Plan file from `.claude/plan/active/[feature].md`
- Project context from `.claude/CLAUDE.md`
- Clean working directory (or understood dirty state)
- Baseline tests passing

**Verify Before Starting:**
1. Read plan file completely
2. Check all prerequisites are met
3. Verify baseline tests pass
4. Understand stop conditions
5. Confirm git status is acceptable

## Execution Algorithm

### Phase 1: Pre-Execution Validation

```
1. Read plan file from .claude/plan/active/
2. Parse plan structure:
   - Context and objectives
   - Prerequisites list
   - Implementation steps
   - Validation strategy
   - Success criteria
   - Rollback plan
3. Verify prerequisites:
   - Run prerequisite verification commands
   - Check all dependencies available
   - Confirm configurations in place
4. Check baseline state:
   - Run test suite (must pass)
   - Verify no linting errors
   - Confirm clean git state (or understood state)
5. Update progress.txt:
   "YYYY-MM-DD HH:MM - Starting plan: [feature-name]"
6. If any prerequisite fails:
   - Log failure to progress.txt
   - Alert human with specific missing item
   - STOP (do not proceed)
```

### Phase 2: Step-by-Step Execution

For each step in the plan:

```
Step N Execution Loop:

1. Read step details:
   - Action description
   - Files to create/modify
   - Tests required
   - Validation commands
   - Commit message template

2. Execute the action:
   - Create files if specified
   - Modify files if specified
   - Follow project patterns and conventions
   - Use appropriate tools (Read, Edit, Write, Bash)
   - Maintain code quality and style

3. Validate the change:
   - Run validation commands from plan
   - Run relevant tests (unit, integration)
   - Check for regressions
   - Verify expected behavior

4. Decision Point:

   IF validation passes:
     a. Commit changes:
        - Use commit message from plan
        - Include session URL in commit body
     b. Update progress.txt:
        "YYYY-MM-DD HH:MM - Completed step N: [description]"
     c. Continue to next step

   ELSE IF validation fails (first time):
     a. Analyze failure
     b. Attempt fix
     c. Retry validation
     d. If fix succeeds: commit and continue
     e. If fix fails: proceed to retry logic below

   ELSE IF validation fails (2nd time):
     a. Deep analysis of failure
     b. Check for environmental issues
     c. Attempt alternative approach
     d. Retry validation
     e. If succeeds: commit and continue
     f. If fails: proceed to stop condition below

   ELSE IF validation fails (3rd time):
     a. Log failure to progress.txt
     b. Document what was attempted
     c. Alert human with specifics:
        - What step failed
        - What validation failed
        - What was attempted (3 tries)
        - Current state of code
        - Suggested next steps
     d. STOP (do not proceed)

5. Between steps:
   - Brief pause to ensure no race conditions
   - Verify working directory state
   - Confirm ready for next step
```

### Phase 3: Post-Execution Completion

```
After all steps complete:

1. Run final validation:
   - Full test suite
   - Linting
   - Build (if applicable)
   - End-to-end feature test

2. Verify success criteria:
   - Check all success criteria from plan
   - Confirm test coverage goals met
   - Verify documentation updated
   - Ensure all commits made

3. If final validation passes:
   a. Update features.txt:
      - Move feature from Todo to Done
      - Add completion date
   b. Archive plan:
      - Move from .claude/plan/active/
      - To .claude/plan/complete/
      - Rename with date: YYYY-MM-DD-[feature-slug].md
   c. Update progress.txt with summary:
      "YYYY-MM-DD HH:MM - Completed plan: [feature-name]
       - Steps completed: N/N
       - Commits made: N
       - Tests: All passing (X/X)
       - Duration: Y minutes"
   d. Provide completion summary to user
   e. SUCCESS

4. If final validation fails:
   a. Do NOT mark as complete
   b. Do NOT move plan to complete/
   c. Log issue to progress.txt
   d. Alert human with details
   e. Suggest next steps
   f. STOP
```

## Stop Conditions (Human Intervention Required)

Immediately STOP execution and alert human when:

### 1. Test Failures
- 3 consecutive test failures on same step
- Test coverage drops below 75%
- Critical tests fail that weren't failing before
- Cannot determine how to fix failing tests

### 2. Data Integrity Issues
- Risk of data loss or corruption
- Conflicting data states
- Invalid data structures
- Cannot validate data integrity

### 3. Security Concerns
- Credentials or secrets needed
- Authentication required
- Security implications discovered
- Potential vulnerability introduced

### 4. Architectural Decisions
- Major refactoring needed beyond plan scope
- Design pattern choice required
- Technology stack changes needed
- Multiple valid approaches (need human preference)

### 5. Scope Issues
- Step much more complex than expected
- New requirements discovered
- Dependencies not in plan
- Feature scope significantly larger than planned

### 6. External Dependencies
- API or service unavailable
- Rate limiting encountered
- External resource missing (URLs, documents)
- Network or permission issues

### 7. Ambiguous Requirements
- Unclear what correct behavior should be
- Contradictory requirements
- Missing specifications
- Need product/design decisions

### 8. Code Quality Issues
- Cannot maintain code quality standards
- Introducing technical debt unavoidably
- Violating project conventions necessarily
- Breaking changes required

## Commit Strategy

### Commit Message Format
```
<type>(<scope>): <short description>

<optional detailed description>
<optional breaking changes note>

https://claude.ai/code/session_<SESSION_ID>
```

### Types (from project conventions)
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `test`: Adding or updating tests
- `refactor`: Code change that neither fixes bug nor adds feature
- `chore`: Changes to build process or auxiliary tools

### When to Commit
- After each successful step validation
- Keep commits atomic and focused
- One step = one commit (usually)
- Combine tiny steps if appropriate (< 5 lines each)
- Never commit failing code
- Never commit without testing

## Progress Tracking

### progress.txt Format

```
YYYY-MM-DD HH:MM - Starting plan: [feature-name]
YYYY-MM-DD HH:MM - Verified prerequisites: all passing
YYYY-MM-DD HH:MM - Baseline tests: 42/42 passing

YYYY-MM-DD HH:MM - Step 1/N: [description]
YYYY-MM-DD HH:MM - Created: [files]
YYYY-MM-DD HH:MM - Tests passing: 42/42
YYYY-MM-DD HH:MM - Committed: feat(scope): description (abc123)

YYYY-MM-DD HH:MM - Step 2/N: [description]
YYYY-MM-DD HH:MM - Modified: [files]
YYYY-MM-DD HH:MM - Tests passing: 45/45 (+3 new)
YYYY-MM-DD HH:MM - Committed: feat(scope): description (def456)

[... continue for all steps ...]

YYYY-MM-DD HH:MM - Final validation: all tests passing (48/48)
YYYY-MM-DD HH:MM - Completed plan: [feature-name]
YYYY-MM-DD HH:MM - Moved to complete/
YYYY-MM-DD HH:MM - Duration: 45 minutes
```

### Continuous Updates
- Update after each step completion
- Log errors and retries
- Document decisions made
- Track time and progress
- Note any deviations from plan

## Error Handling

### Validation Failure
1. Attempt 1: Fix obvious issues
2. Attempt 2: Try alternative approach
3. Attempt 3: Deep investigation
4. After 3 attempts: Stop and alert human

### Missing Prerequisites
1. Check if can be installed/configured automatically
2. If yes: Add step to install, then continue
3. If no: Stop and alert human with specific need

### Scope Expansion
1. Assess if within reasonable bounds
2. If minor (< 20% more work): Adapt and continue
3. If major: Stop and alert human with scope details

### External Failures
1. Retry with exponential backoff (2s, 4s, 8s)
2. Check if alternative available
3. If persistent: Stop and alert human

## Validation Strategy

### After Each Step
```bash
# Run step-specific tests
[test command from plan]

# Check for regressions
[full test suite if specified]

# Verify behavior
[validation command from plan]
```

### Before Commit
```bash
# Ensure tests pass
[test command]

# Check code quality (if specified)
[lint command]

# Verify git state
git status
git diff --check  # Check for whitespace errors
```

### Final Validation
```bash
# Full test suite
[project test command from CLAUDE.md]

# Linting
[project lint command from CLAUDE.md]

# End-to-end feature test
[feature-specific validation]
```

## Output Format

### During Execution (Continuous)
```
Executing plan: [feature-name]

Step 1/N: [description]
├─ Action: [what's being done]
├─ Creating: [files]
├─ Testing: [test results]
└─ ✓ Committed: [commit message] (abc123)

Step 2/N: [description]
├─ Action: [what's being done]
├─ Modifying: [files]
├─ Testing: [test results]
└─ ✓ Committed: [commit message] (def456)

[... continue ...]
```

### On Completion
```
✓ Plan completed: [feature-name]

Summary:
- Steps completed: N/N
- Commits made: N
- Files created: N
- Files modified: N
- Tests: All passing (X/X, +Y new)
- Coverage: Z% (↑ from W%)
- Duration: M minutes

Changes:
- [Commit 1: brief description]
- [Commit 2: brief description]
- [... all commits ...]

The plan has been moved to .claude/plan/complete/YYYY-MM-DD-[feature-slug].md
Updated features.txt to mark feature as done.

Next: [Next feature from backlog, or "All features complete!"]
```

### On Stop Condition
```
⚠ Execution stopped: [reason]

Plan: [feature-name]
Progress: Step N/M completed

Issue:
[Detailed description of why execution stopped]

What was attempted:
- [Attempt 1 description]
- [Attempt 2 description]
- [Attempt 3 description if applicable]

Current state:
- Working directory: [clean/has changes]
- Tests: [X passing, Y failing]
- Last successful step: N
- Commits made: N

Next steps:
[Suggested actions for human]

The plan remains in .claude/plan/active/ for continuation after resolution.
```

## Integration with Project

**For NGSS Curriculum Builder specifically:**

### Test Commands
```bash
# Verify data integrity
python -c "import json; json.load(open('data/states.json'))"

# Test CLI functionality
python state_science_standards_system.py list
python state_science_standards_system.py search 5
python state_science_standards_system.py state WA

# Run parser (if applicable)
uv run parse_standards.py

# Validate URLs (if applicable)
uv run validate_urls.py
```

### Common Validations
- JSON structure valid (no syntax errors)
- State count = 51
- Document count maintained
- No data loss
- URLs formatted correctly
- Grade levels valid (K, 1-12)

### Project-Specific Stop Conditions
- Data corruption risk in states.json
- URLs broken (> 10 broken links)
- External education websites unavailable
- Manual research required
- PDF documents need downloading

### Commit Patterns
- `feat(data): add [state] science standards`
- `fix(validation): correct broken URLs for [states]`
- `feat(parser): add [format] document parsing`
- `docs(readme): add [section] documentation`
- `test(cli): verify [command] functionality`

## Notes

- **Execution is mechanical, not creative** - Follow the plan precisely
- **Validation is critical** - Never skip tests or validation steps
- **Stop when uncertain** - Better to ask than to break
- **Commit frequently** - Incremental progress is safe progress
- **Document everything** - Future Claude (or humans) will read progress.txt
- **Maintain quality** - Autonomous doesn't mean careless
- **Respect stop conditions** - They exist for good reasons

## Quality Checklist

Before marking any plan as complete:

- [ ] All steps executed successfully
- [ ] All tests passing
- [ ] No linting errors
- [ ] All files properly formatted
- [ ] All commits have proper messages
- [ ] All commits pushed (if auto-push enabled)
- [ ] progress.txt updated completely
- [ ] features.txt updated
- [ ] Plan moved to complete/
- [ ] No TODO comments left (unless intentional)
- [ ] No debug code left
- [ ] Documentation updated if needed
