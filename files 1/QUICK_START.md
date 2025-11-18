# Quick Start Guide - YOPmail Email Automation

## 🚀 Get Started in 3 Steps

### Step 1: Review the Files

You now have:
- ✅ `yopmail_link_retriever.py` - Email automation module
- ✅ `test_runner_with_email.py` - Updated test runner with email integration
- ✅ `README.md` - Full documentation

### Step 2: Test Email Retrieval Standalone

Before running the full test suite, verify email retrieval works:

```bash
python yopmail_link_retriever.py
```

When prompted:
- Enter an EFS Reference you know exists (e.g., from a recent test)
- Enter "PCM" as the approver stage
- Watch it automatically find and extract the link!

### Step 3: Run Your First Automated Test

```bash
python test_runner_with_email.py
```

The system will now:
1. ✅ Fill out the payment request form
2. ✅ Extract the EFS Reference (e.g., EFS-123456)
3. ✅ **Automatically poll YOPmail for the approval email**
4. ✅ **Extract the JotForm link automatically**
5. ✅ Process the approval
6. ✅ Generate Excel report

## 🎯 What's Different?

### Before (Your Original Script)
```python
def get_approval_link(self, stage_name: str, efs_ref: str) -> str:
    print(f"📧 {stage_name} Approval Link Required")
    print(f"EFS Ref: {efs_ref}")
    
    # Manual input required
    link = input(f"Paste {stage_name} link (or 'skip'): ").strip()
    return link
```

### After (New Integrated Version)
```python
def get_approval_link(self, stage_name: str, efs_ref: str) -> str:
    if self.auto_retrieve_links:
        # Automatic retrieval from YOPmail!
        link = get_approval_link_for_test(stage_name, efs_ref)
        
        if link:
            print(f"✅ Link retrieved automatically!")
            return link
    
    # Fallback to manual if needed
    link = input(f"Paste {stage_name} link: ").strip()
    return link
```

## 🔧 Configuration

### Current Setup (PCM Only - POC)

In `yopmail_link_retriever.py`:
```python
APPROVER_EMAILS = {
    "PCM": "5497b0691aac47498821b0a603017505@yopmail.com",
    # Add more approvers when ready:
    # "RD": "your_rd_email@yopmail.com",
    # "RCM": "your_rcm_email@yopmail.com",
}
```

### How to Add More Approvers

1. Get the YOPmail addresses for RD and RCM approvers
2. Add them to the `APPROVER_EMAILS` dictionary
3. That's it! The system will automatically handle them.

## 📊 What to Expect

### Console Output During Test

```
====================================================================
TEST 1 of 9
====================================================================
Test ID: TEST_001
Description: TEST_001: Happy Path - Single Approver
====================================================================

============================================================
Filling Form
============================================================
✓ Company/Division: Edmundson Electrical
✓ Location Number: 331
✓ Raised By: Test Automation
✓ Payment Type: Sponsorship/Charitable Donation
...

============================================================
Submitting Form
============================================================
✓ Submit clicked
✅ Redirected to: https://eel.jotform.com/...
✅ EFS Reference: EFS-849362
============================================================

============================================================
Processing PCM Approval
============================================================

    🔍 Searching for approval link...
    📧 Approver: PCM
    🔖 EFS Ref: EFS-849362
    ⏱️  Max wait: 120 seconds

    [Attempt 1/24]
    📬 Loading YOPmail inbox: 5497b0691aac47498821b0a603017505
    📧 Found 2 message(s)
    🔎 Scanning 2 email(s)...
    ✅ Found email with EFS-849362
    🎯 Approval link found!

✅ Link retrieved automatically!
🔗 https://eel.jotform.com/edit/6392716199412043114?eapeo1e
============================================================

✓ Opened PCM approval form
✓ Selected: Approve
✓ Submitted approval
✅ Redirected to: https://eel.jotform.com/...
✅ Outcome: Form fully approved
============================================================

✅ Test TEST_001 completed: PASS
```

## ⚡ Key Features

### 1. Smart Email Matching
- Searches for emails containing the exact EFS Reference
- Handles multiple emails in inbox
- Ignores irrelevant emails

### 2. Automatic Polling
- Checks inbox every 5 seconds
- Waits up to 2 minutes for email to arrive
- Handles email delays gracefully

### 3. Robust Link Extraction
- Extracts JotForm edit links from HTML
- Supports both PCM (eapeo1e) and RD (eapet2e) patterns
- Validates link format

### 4. Intelligent Fallback
- If automatic retrieval fails → asks for manual input
- Never blocks the test from continuing
- Clear error messages and guidance

## 🎓 Pro Tips

### Tip 1: Run a Single Test First
Edit `test_runner_with_email.py` temporarily:
```python
# Near the bottom of run_all_tests()
for i, test_case in enumerate(self.test_cases[:1], 1):  # Only run first test
    ...
```

### Tip 2: Increase Wait Time if Needed
In `yopmail_link_retriever.py`:
```python
def get_approval_link(self, approver_stage: str, efs_ref: str, 
                     max_attempts: int = 48,  # Changed from 24 = 4 min wait
                     poll_interval: int = 5):
```

### Tip 3: Disable Auto-Retrieval for Debugging
In `test_runner_with_email.py`:
```python
runner = TestRunner(
    test_suite_file="test_suite.json",
    output_folder="test_results",
    auto_retrieve_links=False  # Disable for manual testing
)
```

### Tip 4: Check YOPmail Manually If Stuck
If the script can't find the email:
```
https://yopmail.com/?login=5497b0691aac47498821b0a603017505
```

## ✅ Checklist Before Running

- [ ] Firefox installed
- [ ] Selenium installed (`pip install selenium`)
- [ ] Playwright installed (`pip install playwright`)
- [ ] `config.py` and `utils.py` present
- [ ] `test_suite.json` in same folder
- [ ] Internet connection active
- [ ] YOPmail accessible (test in browser first)

## 🐛 Common Issues & Fixes

### Issue: "No email found after 24 attempts"
**Cause:** Email hasn't arrived or went to wrong inbox
**Fix:** Check YOPmail manually, increase wait time, or verify EFS Ref

### Issue: "Could not extract EFS Reference"
**Cause:** Thank you page format changed
**Fix:** Update `extract_efs_ref()` in `utils.py`

### Issue: "Selenium can't find Firefox"
**Cause:** Geckodriver not installed
**Fix:** `sudo apt-get install firefox-geckodriver` (Linux) or `brew install geckodriver` (Mac)

### Issue: "Link extracted but approval fails"
**Cause:** Link might have expired
**Fix:** Check link validity, ensure timely processing

## 📈 Next Steps

After POC success:

1. **Add More Approvers**
   - Get YOPmail addresses for RD and RCM
   - Add to `APPROVER_EMAILS` dictionary
   
2. **Test All Payment Types**
   - Customer Rebate
   - Sales Ledger Refund
   - Employee Expense Advance

3. **Optimize Performance**
   - Reduce polling intervals
   - Add parallel test execution
   - Implement caching

4. **Production Readiness**
   - Add error handling
   - Implement logging
   - Create deployment scripts

## 🎉 Expected Results

After running the test suite:
- ✅ 9 test cases executed automatically
- ✅ Excel report generated with results
- ✅ All approval links retrieved without manual intervention
- ✅ ~80% time savings compared to manual process

## 💪 You're Ready!

You now have a fully automated test system that:
- Fills forms automatically
- Retrieves approval emails automatically
- Processes approvals automatically
- Generates reports automatically

Just run `python test_runner_with_email.py` and watch the magic happen! 🚀

---

**Questions or issues?** Refer to the full README.md for detailed troubleshooting.
