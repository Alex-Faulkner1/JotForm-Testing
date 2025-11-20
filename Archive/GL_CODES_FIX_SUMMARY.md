# GL Codes Issue - Root Cause and Fix

## Problem Identified

The Expense Payment tests (TEST_007, TEST_008, TEST_009) were failing with:
```
⚠️  Could not fill value field: Timeout 30000ms exceeded.
```

## Root Cause

The test runner was trying to fill a **"value" field (#input_844)** for Expense Payment forms, but **this field doesn't exist** for Expense Payment.

### How Different Payment Types Handle Values:

1. **Sponsorship/Charitable Donation**: Has a direct "Value" field (#input_844) ✓
2. **Goods for Resale**: Uses "Goods (£)" field (#input_855) in Total Values section ✓
3. **Expense Payment**: Value is **AUTO-CALCULATED** from the Payable Documents section ✗

For Expense Payment:
- You fill: Goods, Carriage, VAT, Subtotal, Less Settlement Discount
- The system calculates: Total Payable (readonly field)
- There is NO manual "Value" field to fill

## The Bug

In `test_runner_WITH_GL_CODES.py` lines 806-826, the code was:

```python
# Value (different field structure for Goods for Resale)
try:
    if test_data.get("payment_type") == "Goods for Resale":
        # Fill Goods field
        await self.page.fill("#input_855", test_data["value"])
    else:
        # Standard value field for other payment types
        await self.page.fill("#input_844", test_data["value"])  # ← FAILS for Expense Payment!
except Exception as e:
    print(f"⚠️  Could not fill value field: {e}")
```

When payment_type was "Expense Payment", it would try to fill #input_844, which **doesn't exist**, causing a 30-second timeout and test failure.

## The Fix

Updated logic to handle all three payment types correctly:

```python
# Value (different field structure for Goods for Resale and Expense Payment)
try:
    payment_type = test_data.get("payment_type")
    
    if payment_type == "Goods for Resale":
        # For Goods for Resale, fill the "Goods (£)" field
        await self.page.fill("#input_855", test_data["value"])
        print(f"✓ Goods Value: £{test_data['value']}")
    elif payment_type == "Expense Payment":
        # For Expense Payment, value is calculated from payable documents section
        # No separate value field to fill - skip this step
        print(f"ℹ️  Expense Payment value calculated from payable documents")
    else:
        # Standard value field for other payment types (Sponsorship, etc.)
        await self.page.fill("#input_844", test_data["value"])
        print(f"✓ Value: £{test_data['value']}")
except Exception as e:
    print(f"⚠️  Could not fill value field: {e}")
```

## Impact

After this fix:
- Expense Payment tests will no longer timeout at the "value field" step
- GL Codes section will now execute properly (it comes AFTER the value section)
- All three Expense Payment tests (TEST_007, TEST_008, TEST_009) should pass

## GL Codes Status

The GL Codes implementation in the test runner (lines 530-660) was **already correct** - it just wasn't being reached because the tests were timing out earlier at the value field.

## Testing Recommendation

Run the test suite again with the fixed test_runner_FIXED.py:
```bash
python test_runner_FIXED.py
```

Expected results:
- TEST_007 (Expense Payment Happy Path): PASS
- TEST_008 (Expense Payment App 1 Rejection): PASS
- TEST_009 (Expense Payment App 2 Rejects): PASS

## Files Changed

- `test_runner_FIXED.py` - Fixed version of the test runner
- Original file: `test_runner_WITH_GL_CODES.py`
- Change location: Lines 806-826
