# Work Command (Obra-Enhanced)

Start autonomous work session with plan-based execution.

## Process

1. Check git status - ensure clean working directory
2. Read progress.txt to understand previous work
3. Run test suite to verify baseline state
4. If tests fail:
   - Fix failures before proceeding
   - Update progress.txt with fixes
5. Check for existing plans in `.claude/plan/active/`
6. If plans exist:
   - Use /execute-next
   - Continue until all plans complete or blocker encountered
7. If no plans exist:
   - Read next feature from features.txt
   - Use /plan-feature to create plan
   - Ask: "Plan created. Execute now? (yes/no)"
   - If yes: Use /execute-next
8. Repeat until:
   - All features completed, OR
   - Blocker encountered (stop condition met), OR
   - All plans executed

## Fully Autonomous Mode

To skip confirmations between plans, add to `.claude/CLAUDE.md`:

```markdown
AUTO_EXECUTE=true
```

When enabled, `/work` will:
- Execute all active plans without asking
- Create new plans from features.txt as needed
- Only stop at blockers or when all work complete

## Session Management

- Continuously update progress.txt
- Commit after each successful step
- Leave codebase in working state
- Provide summary when stopping

## Usage

```bash
/work
# Start autonomous work session

# Typical session flow:
# 1. Checks baseline (tests pass)
# 2. Finds active plan or creates new plan
# 3. Executes plan step-by-step
# 4. Moves to next plan when complete
# 5. Continues until blocker or all work done
```

## Pre-Work Checklist

Before starting `/work`, verify:

- [ ] Git working directory is clean (or intentionally dirty)
- [ ] Baseline tests pass
- [ ] features.txt has work items
- [ ] Plans reviewed if they exist in active/
- [ ] Stop conditions understood

## Example Session

```
$ /work

[Checking baseline state...]
✓ Git working directory clean
✓ Tests passing (42/42)
✓ Found 2 active plans

[Executing: url-validation.md]
Step 1/5: Create validation script
✓ Created validate_urls.py
✓ Tests pass (42/42)
✓ Committed: feat(validation): add URL validation script

Step 2/5: Run validation on all documents
✓ Validated 80 URLs
✓ Found 4 broken URLs (WA, CA, HI, TX)
✓ Committed: test(validation): validate all document URLs

[... steps 3-5 continue ...]

✓ Plan complete: url-validation.md
✓ Moved to .claude/plan/complete/
✓ Updated features.txt

[Executing: page-range-data.md]
Step 1/4: Research page ranges for K-12 documents
⚠ STOP: Need to manually download and inspect PDFs
⚠ Cannot proceed without human research

[Session paused: Blocker encountered]

Summary:
- Completed: url-validation (5/5 steps)
- Blocked: page-range-data (1/4 steps)
- Commits: 5
- Tests: All passing (45/45)
- Duration: 8 minutes

Next: Complete page range research for 64 K-12 documents
```

## Stop Conditions

The /work command will stop and alert human when:

- Test coverage drops below 75%
- Breaking API changes needed
- Security implications discovered
- 3 consecutive test failures on same step
- Architectural decisions required
- Ambiguous requirements encountered
- External dependencies unavailable
- Scope significantly larger than expected

## Workflow Comparison

### Manual Mode (No /work)
```
You: /plan-feature
Claude: [Creates plan]
You: Review plan, then /execute-next
Claude: [Executes one plan, stops]
You: /execute-next
Claude: [Executes next plan, stops]
[Repeat for each plan]
```

### Autonomous Mode (Using /work)
```
You: /work
Claude: [Creates plans, executes all sequentially]
       [Stops only at blockers or completion]
       [Hours of work done autonomously]
```

## Notes

- **Most powerful command** for autonomous development
- Best used after batch planning with plan review
- Can run for hours autonomously if no blockers
- Always leaves codebase in working state
- Comprehensive progress logging
- Safe to interrupt - progress is saved continuously
