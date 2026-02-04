# Execute Next Command

Execute the next plan in `.claude/plan/active/` using the **executing-plans** skill.

## Process

1. List plans in `.claude/plan/active/`
2. Select highest priority (or oldest if no priority set)
3. Use executing-plans skill on that plan
4. Follow plan step-by-step:
   - Execute step
   - Run tests
   - Commit if successful
   - Update progress.txt
   - Continue to next step
5. When complete:
   - Move plan to `.claude/plan/complete/`
   - Update features.txt
   - Append summary to progress.txt

## Autonomous Execution Rules

- Run tests after each step
- Commit after successful steps only
- Stop and flag if step fails 3 times
- Update progress.txt after each step
- Ask human if stop condition encountered

## Stop Conditions

Execution stops and asks for human guidance when:

- Test coverage drops below 75%
- Breaking changes needed
- Security implications discovered
- 3 consecutive test failures on same step
- Architectural decisions required
- Ambiguous requirements encountered
- External dependencies unavailable
- Scope significantly larger than expected

## Usage

```bash
/execute-next
# Executes the next plan from .claude/plan/active/
```

## Success Criteria

Before marking a plan complete:

- [ ] All tests pass
- [ ] No linting errors
- [ ] Code formatted properly
- [ ] Feature works end-to-end
- [ ] Committed to git with conventional message
- [ ] Progress logged to progress.txt
- [ ] Plan moved to `.claude/plan/complete/`
- [ ] features.txt updated

## Notes

- Uses **executing-plans** skill from `.claude/skills/obra/`
- Fully autonomous execution with validation gates
- Human review only needed at stop conditions
- All changes committed incrementally with clear messages
