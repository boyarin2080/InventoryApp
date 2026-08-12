# Bugfix Design Document

## Overview
Fix currency symbol display on dashboard to use Russian Ruble (₽) instead of US Dollar ($) and ensure proper suffix position.

## Files to Modify

### templates/dashboard.html
**Line 115** - Change price display format

**Current:**
```html
<td>${{ item.purchase_price }}</td>
```

**Fixed:**
```html
<td>₽{{ item.purchase_price|floatformat:2 }}</td>
```

## Validation Steps

After fix, verify:
1. Dashboard displays prices with `₽` suffix (e.g., `100.00₽`)
2. All other templates continue to use correct format
3. No美元 symbols remain anywhere in templates

## Test Cases

| Scenario | Expected Result |
|----------|----------------|
| Dashboard loads | Prices show as `₽XX.XX` |
| Inventory list page | Prices remain `₽XX.XX` |
| Sales list page | Prices remain `₽XX.XX` |
| Detail pages | Prices remain `₽XX.XX` |