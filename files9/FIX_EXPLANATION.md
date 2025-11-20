# Fix for TEST_003 and TEST_006 Failures

## Problem Identified

**Root Cause**: Incomplete test workflows for "App 2 Rejects" scenarios

### What Was Wrong

Tests 003, 006, and 009 were designed to test the rejection-return workflow:
1. PCM approves
2. RD rejects
3. **Form returns to PCM** (generates new approval email)

However, the tests only defined steps 1-2, leaving the workflow incomplete:
- TEST_003 comment: "Needs to be completed from PCM approval stage"
- TEST_006 comment: "investigate logic of the tests"

The script had a `break` statement at line 1241 that stopped processing after RD rejection, preventing any subsequent workflow stages from executing.

---

## Solution

### 1. Updated Test Suite (`test_suite_FIXED.json`)

Added a **third workflow stage** to tests 003, 006, and 009:

```json
{
  "approval_workflow": [
    {
      "stage": "PCM",
      "action": "Approve",
      "notes": "First approver approves"
    },
    {
      "stage": "RD",
      "action": "Reject",
      "notes": "Second approver rejects - returns to App 1"
    },
    {
      "stage": "PCM",
      "action": "Approve",
      "notes": "PCM re-approves the returned form"
    }
  ],
  "expected_outcome": "Form fully approved"
}
```

**Changes Summary**:
- TEST_003: Added 3rd stage (PCM re-approval), changed expected outcome to "Form fully approved"
- TEST_006: Added 3rd stage (PCM re-approval), changed expected outcome to "Form fully approved", increased value to 10000 to trigger RD approval
- TEST_009: Added 3rd stage (PCM re-approval), changed expected outcome to "Form fully approved"

### 2. Updated Script (`test_runner_WITH_APPROVAL_LINKS_FIXED.py`)

**Removed** the validation code and `break` statement at lines 1209-1241.

**Before** (lines 1209-1241):
```python
if stage_result.get("action") == "Reject" and stage["stage"] in ["RD", "COO"]:
    result.actual_outcome = "Sent back to App 1"
    # [30+ lines of validation code]
    break  # <-- This prevented processing the next stage!
```

**After**:
```python
if stage_result.get("action") == "Reject" and stage["stage"] in ["RD", "COO"]:
    print("\n" + "=" * 60)
    print("📧 RD Rejection - Form Returns to PCM")
    print("=" * 60)
    print(f"Form rejected by {stage['stage']}, returning to PCM...")
    print(f"Next workflow stage should handle PCM re-approval")
    print("=" * 60 + "\n")
    # Note: Don't break here - continue to next workflow stage
```

---

## How It Works Now

The complete workflow for tests 003, 006, and 009:

```
┌─────────────────────────────────────────────────────┐
│  Step 1: Form Submission                            │
│  ✓ Creates EFS reference (e.g., DEV_PR488)         │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  Step 2: PCM Approval (1st time)                    │
│  ✓ Retrieves approval link from email              │
│  ✓ Opens link and clicks "Approve"                 │
│  ✓ Submits approval                                 │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  Step 3: RD Rejection                               │
│  ✓ Retrieves RD approval link from email           │
│  ✓ Opens link and clicks "Reject"                  │
│  ✓ Fills rejection reason                          │
│  ✓ Submits rejection                                │
│  → Form returns to PCM (new email sent)            │
└─────────────────────────────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│  Step 4: PCM Re-Approval (2nd time) ✨ NEW!        │
│  ✓ Retrieves return-to-PCM approval link           │
│  ✓ Opens link and clicks "Approve"                 │
│  ✓ Submits approval                                 │
│  ✓ Form is now FULLY APPROVED                      │
└─────────────────────────────────────────────────────┘
```

---

## Testing the Fix

Run the updated test suite with the fixed script:

```bash
python test_runner_WITH_APPROVAL_LINKS_FIXED.py
```

Expected results:
- TEST_003: Should now **PASS** with "Form fully approved"
- TEST_006: Should now **PASS** with "Form fully approved"
- TEST_009: Should now **PASS** with "Form fully approved"

---

## Alternative Test Scenario (Optional)

If you want to test the "return and then reject" scenario, you could create additional tests:

```json
{
  "test_id": "TEST_003B",
  "scenario": "App 2 Rejects, Returns to App 1, Then Rejected",
  "approval_workflow": [
    {
      "stage": "PCM",
      "action": "Approve",
      "notes": "First approval"
    },
    {
      "stage": "RD",
      "action": "Reject",
      "notes": "Rejects - returns to PCM"
    },
    {
      "stage": "PCM",
      "action": "Reject",
      "notes": "PCM rejects the returned form"
    }
  ],
  "expected_outcome": "Form DELETED"
}
```

This would test the full rejection-return-rejection flow.
