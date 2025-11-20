# JotForm Payment Request Test Automation Suite

Comprehensive test automation for JotForm Payment Request workflows with automated Excel reporting.

## 📋 Overview

This test automation suite executes predefined test scenarios for JotForm Payment Request forms, covering:
- **3 Form Types**: Sponsorship/Charitable Donation, Goods for Resale, Expense Payments
- **3 Scenarios per Form**: Happy Path, App 1 Rejection, App 2 Rejection
- **Total**: 9 automated test cases

## 📁 Project Structure

```
JotForm-Testing/
├── test_suite.json           # Test case definitions
├── test_runner.py             # Main test execution engine
├── main_manual_links.py       # Manual single-test runner
├── config.py                  # Configuration settings
├── utils.py                   # Helper functions
├── test_results/              # Test execution results
│   ├── TEST_001_DEV_PR###/   # Individual test folders
│   │   ├── stage1_submitted.png
│   │   ├── pcm_approve.png
│   │   └── ...
│   └── test_results_TIMESTAMP.xlsx  # Excel reports
└── output/                    # General output folder
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+** installed
2. **Virtual environment** activated
3. **Dependencies** installed

```bash
cd ~/Documents/GitHub/JotForm-Testing
source venv/bin/activate
pip install -r requirements.txt
```

### Running the Full Test Suite

```bash
python test_runner.py
```

The test runner will:
1. Load all 9 test cases from `test_suite.json`
2. Prompt for your email address
3. Execute each test sequentially
4. Prompt for approval links from emails
5. Take screenshots at each stage
6. Generate Excel report with results

### Running a Single Test (Manual Mode)

For debugging or running individual tests:

```bash
python main_manual_links.py
```

## 📊 Test Suite Structure

### Test Cases Included

| Test ID | Form Type | Scenario | Expected Outcome |
|---------|-----------|----------|------------------|
| TEST_001 | Sponsorship/Charitable Donation | Happy Path | Form fully approved |
| TEST_002 | Sponsorship/Charitable Donation | App 1 Rejection | Form DELETED |
| TEST_003 | Sponsorship/Charitable Donation | App 2 Rejects | Sent back to App 1 |
| TEST_004 | Goods for Resale | Happy Path | Form fully approved |
| TEST_005 | Goods for Resale | App 1 Rejection | Form DELETED |
| TEST_006 | Goods for Resale | App 2 Rejects | Sent back to App 1 |
| TEST_007 | Expense Payments | Happy Path | Form fully approved |
| TEST_008 | Expense Payments | App 1 Rejection | Form DELETED |
| TEST_009 | Expense Payments | App 2 Rejects | Sent back to App 1 |

### Test Data Structure (JSON)

Each test case contains:

```json
{
  "test_id": "TEST_001",
  "form_type": "Sponsorship/Charitable Donation",
  "scenario": "Happy Path",
  "description": "All approvers approve - single approver",
  "test_data": {
    "company_division": "Edmundson Electrical",
    "location_number": "331",
    "raised_by": "Test Automation",
    "payment_type": "Sponsorship/Charitable Donation",
    "description": "TEST_001: Happy Path - Single Approver",
    "payee": "Test Charity",
    "value": "5000",
    ...
  },
  "approval_workflow": [
    {
      "stage": "RCM",
      "approver_email": "alex.faulkner@digiblu.com",
      "action": "Approve",
      "notes": "First and only approver"
    }
  ],
  "expected_outcome": "Form fully approved",
  "expected_status": "APPROVED"
}
```

## 📧 Email Approval Links

During test execution, you'll be prompted to provide approval links:

### PCM Approval Link
```
Expected format: https://eel.jotform.com/edit/############?eapeo1e
```

### RD Approval Link
```
Expected format: https://eel.jotform.com/edit/############?eapet2e
```

**How to get these links:**
1. Check your email after Stage 1 submission
2. Look for email with subject containing the EFS Ref (e.g., DEV_PR370)
3. Copy the link from the "Click here" button
4. Paste into the terminal when prompted

## 📈 Excel Report

After test execution, an Excel report is generated with two sheets:

### Sheet 1: Test Results

Contains detailed results for each test:
- Test ID
- Test Name
- Form Type
- Scenario
- Status (PASS/FAIL/ERROR) - color coded
- EFS Reference
- Start/End Time
- Duration
- Expected vs Actual Outcome
- Error Messages
- Screenshots paths

### Sheet 2: Summary

High-level statistics:
- Total Tests
- Passed
- Failed
- Errors
- Pass Rate
- Execution Date/Time

**Color Coding:**
- 🟢 Green = PASS
- 🔴 Red = FAIL
- 🟡 Yellow = ERROR

## 🔧 Configuration

### config.py

Key settings:

```python
# JotForm URL
JOTFORM_URL = "https://eel.jotform.com/form/252244495892972"

# Browser settings
HEADLESS_MODE = False  # Set to True for headless execution
BROWSER_TIMEOUT = 60000

# Timing
WORKFLOW_WAIT_TIME = 10000  # Wait between stages (ms)
REDIRECT_TIMEOUT = 5000      # Wait for redirects (ms)

# Test Data
TEST_DATA = {
    "company_division": "Edmundson Electrical",
    "location_number": "331",
    ...
}
```

### Modifying Test Suite

To add/modify tests, edit `test_suite.json`:

```bash
# Open in your editor
code test_suite.json

# Or use any text editor
nano test_suite.json
```

## 🖼️ Screenshots

Screenshots are automatically captured:
- `stage1_submitted.png` - After initial form submission
- `pcm_approve.png` / `pcm_reject.png` - After PCM stage
- `rd_approve.png` / `rd_reject.png` - After RD stage
- `*_error.png` - If errors occur
- `*_already_reviewed.png` - If form already reviewed

## 🐛 Troubleshooting

### "No approval buttons found"

**Cause:** Banner detection is incorrectly identifying form as reviewed.

**Solution:**
1. Check the screenshot in test results folder
2. Verify the approval link is correct
3. Ensure sufficient wait time (increase WORKFLOW_WAIT_TIME in config.py)

### "Could not extract EFS Ref"

**Cause:** Form submission failed or redirect didn't work.

**Solution:**
1. Check if form has validation errors
2. Verify all required fields are filled
3. Check browser screenshot for errors

### "No redirect detected"

**Cause:** Form took longer to process than expected.

**Solution:**
1. Increase REDIRECT_TIMEOUT in config.py
2. Check network connection
3. Verify JotForm is responding

### Email Link Issues

**Problem:** Can't find approval email.

**Solution:**
1. Check spam/junk folder
2. Search for EFS Ref in email
3. Wait a few seconds - emails can be delayed
4. Verify email address is correct in config

## 📝 Test Execution Workflow

```
1. Load test_suite.json
   ↓
2. Get user email for approvals
   ↓
3. For each test case:
   ├─ Fill form with test data
   ├─ Submit Stage 1
   ├─ Extract EFS Ref
   ├─ Take screenshot
   ├─ For each approval stage:
   │  ├─ Prompt for approval link
   │  ├─ Navigate to approval form
   │  ├─ Check if already reviewed
   │  ├─ Click Approve/Reject
   │  ├─ Submit
   │  └─ Take screenshot
   └─ Record result (PASS/FAIL/ERROR)
   ↓
4. Generate Excel report
   ↓
5. Display summary
```

## 🔒 Best Practices

1. **Run one test at a time initially** - Use `main_manual_links.py` to verify each form type works
2. **Check emails promptly** - Approval emails may take a few seconds to arrive
3. **Review screenshots** - Always check screenshots if a test fails
4. **Keep test data unique** - Use different invoice numbers for each test
5. **Run during off-peak hours** - Avoid running during heavy system usage

## 🎯 Next Steps

### Extending the Test Suite

1. **Add more form types:**
   - Customer Rebate
   - Sales Ledger Refund
   - Employee Expense Advances

2. **Add more scenarios:**
   - App 2 Rejects → App 1 Re-approves → Success
   - App 2 Rejects → App 1 Rejects
   - Multi-level rejections

3. **Add email automation:**
   - Implement IMAP to automatically fetch approval links
   - Remove manual link entry requirement

### Email Integration (Future)

Once IMAP authentication is resolved:

```python
# In test_runner.py, replace get_approval_link() with:
from email_helper import get_approval_link_from_email

approval_link = get_approval_link_from_email(
    efs_ref, 
    stage_name, 
    EMAIL_CONFIG
)
```

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review screenshot in test_results folder
3. Check Excel report for error details
4. Review console output for debug messages

## 📚 Related Files

- `main_manual_links.py` - Single test manual runner
- `email_helper.py` - Email integration (future)
- `SCRIPT_VERSIONS.md` - Documentation on different script versions
- `Payment_Request_Rejection_Flows.xlsx` - Master test scenarios

## 🏆 Success Criteria

A test is considered **PASSED** when:
- ✅ Form submits successfully
- ✅ EFS Ref is extracted
- ✅ All approval stages execute without error
- ✅ Actual outcome matches expected outcome
- ✅ Screenshots captured successfully

## ⚠️ Known Limitations

1. **Manual link entry** - Requires user to paste approval links from email
2. **Sequential execution** - Tests run one at a time (not parallel)
3. **Fixed approver** - Uses same email for all approval stages
4. **No email auto-fetch** - Pending IMAP authentication resolution

---

**Version:** 1.0  
**Last Updated:** November 17, 2024  
**Author:** Test Automation Team
