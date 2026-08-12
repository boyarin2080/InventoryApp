# Implementation Tasks

- [x] 1. Write bug condition exploration property test
- [x] 2. Implement bug fix - Replace `$` with `₽` in dashboard.html and add `floatformat:2` filter for consistent decimal places

## Bug Condition Exploration

The bug exists if:
- Dashboard displays prices with `$` prefix (e.g., `$100`)
- Other pages correctly display prices with `₽` suffix (e.g., `100.00₽`)

## Fix Verification

After implementing the fix:
- Dashboard should display prices as `₽XX.XX` (suffix format with 2 decimal places)
- No美元 symbols should appear in any template