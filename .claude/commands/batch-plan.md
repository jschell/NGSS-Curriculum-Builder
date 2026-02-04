# Batch Plan Command

Create plans for all incomplete features in features.txt.

## Process

1. Read all "Todo" features from features.txt
2. For each feature:
   - Use writing-plans skill
   - Save to `.claude/plan/active/[feature-slug].md`
   - Add plan reference to features.txt
3. Analyze dependencies between plans
4. Sort plans by dependency order
5. Provide execution roadmap

## Output Example

```
Created 5 plans:

1. ✓ .claude/plan/active/url-validation.md (no dependencies)
2. ✓ .claude/plan/active/page-range-data.md (no dependencies)
3. ✓ .claude/plan/active/document-caching.md (depends on parser)
4. ✓ .claude/plan/active/full-text-search.md (depends on #3)
5. ✓ .claude/plan/active/export-functionality.md (no dependencies)

Suggested execution order follows dependency chain.
Review all plans, then run /work to begin autonomous execution.
```

## Usage

```bash
/batch-plan
# Creates plans for all Todo features in features.txt
```

## When to Use

- **Morning Planning Session**: Create plans for day's work, review over coffee
- **Sprint Planning**: Plan out multiple features at once
- **After Feature Discussion**: Convert discussed features into executable plans
- **New Project Phase**: Plan major functionality batch

## After Batch Planning

1. **Review all plans** - Check for completeness and accuracy
2. **Adjust priorities** - Reorder features.txt if needed
3. **Start execution**:
   - Manual: `/execute-next` for one-by-one review
   - Autonomous: `/work` for continuous execution

## Notes

- Creates multiple plans efficiently
- Identifies dependencies between features
- Allows review before committing to execution order
- Human reviews plans, then autonomous execution proceeds
- More efficient than planning features one at a time
