# Plan Feature Command

Read the next incomplete feature from features.txt and use the **writing-plans** skill to create a detailed implementation plan.

## Process

1. Read features.txt
2. Identify next incomplete feature under "Todo"
3. Use writing-plans skill with that feature
4. Save plan to `.claude/plan/active/[feature-slug].md`
5. Link plan to feature in features.txt
6. Summarize plan for human review

## Output Example

```
Created plan: .claude/plan/active/url-validation.md

Plan Summary:
- 5 implementation steps
- Estimated time: 1-2 hours
- Dependencies: None (uses stdlib)
- Tests required: URL validation checks
- Commits planned: 5 incremental commits

Review the plan at .claude/plan/active/url-validation.md
Run /execute-next when ready to proceed.
```

## Usage

```bash
/plan-feature
# Automatically selects next feature from features.txt

# Or specify a feature:
/plan-feature "Add page_range data for all documents"
```

## Notes

- Creates plans in `.claude/plan/active/` directory
- Plan follows standard structure (see guide.md Plan Structure section)
- Human should review plan before execution
- Use /execute-next to start execution after review
