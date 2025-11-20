# JotForm Test Automation with Automated Email Link Retrieval

## 🎯 Overview

This integration combines your JotForm test automation with automatic approval link retrieval from YOPmail. Instead of manually copying approval links from emails, the system now automatically:

1. Submits a payment request form
2. Extracts the EFS Reference number
3. Polls the YOPmail inbox for the approval email
4. Extracts the JotForm approval link
5. Processes the approval automatically

## 📁 Files

### Core Files

- **`yopmail_link_retriever.py`** - Email link retrieval module
  - Connects to YOPmail via Selenium
  - Searches for emails by EFS Reference
  - Extracts JotForm edit links from email HTML
  
- **`test_runner_with_email.py`** - Updated test runner
  - Uses Playwright for form automation
  - Integrates with YOPmail retriever
  - Generates Excel reports

- **`test_suite.json`** - Test case definitions
  - Contains test data and approval workflows

### Supporting Files (Required)

You'll need these supporting modules (from your existing setup):
- `config.py` - Configuration settings
- `utils.py` - Utility functions (make_test_pdf, extract_efs_ref, etc.)

## 🔧 Configuration

### Approver Email Addresses

Edit `yopmail_link_retriever.py` to configure approver emails:

```python
APPROVER_EMAILS = {
    "PCM": "5497b0691aac47498821b0a603017505@yopmail.com",
    "RD": "your_rd_approver@yopmail.com",  # Add when ready
    "RCM": "your_rcm_approver@yopmail.com",  # Add when ready
}
```

Currently configured:
- **PCM Approver**: `5497b0691aac47498821b0a603017505@yopmail.com`

### Auto-Retrieval Toggle

In `test_runner_with_email.py`, you can enable/disable automatic link retrieval:

```python
runner = TestRunner(
    test_suite_file="test_suite.json",
    output_folder="test_results",
    auto_retrieve_links=True  # Set to False for manual input
)
```

## 🚀 Usage

### Running the Test Suite

```bash
python test_runner_with_email.py
```

The script will:
1. Load test cases from `test_suite.json`
2. Ask for your approval email (default: alex.faulkner@digiblu.com)
3. Execute each test:
   - Fill and submit the JotForm
   - Extract EFS Reference
   - **Automatically retrieve approval links from YOPmail**
   - Process approvals
   - Verify outcomes
4. Generate an Excel report

### Testing the Email Retriever Standalone

You can test the email retriever independently:

```bash
python yopmail_link_retriever.py
```

This will prompt you for:
- EFS Reference (e.g., EFS-123456)
- Approver stage (PCM/RD/RCM)

## 🔍 How It Works

### Email Link Retrieval Process

1. **Form Submission**
   - Test runner submits a JotForm payment request
   - Extracts EFS Reference from success page (e.g., "EFS-123456")

2. **Email Polling**
   - Opens the YOPmail inbox for the designated approver
   - Polls inbox every 5 seconds (max 24 attempts = 2 minutes)
   - Checks each email for the matching EFS Reference

3. **Link Extraction**
   - When matching email is found:
     - Extracts the JotForm edit link
     - Pattern: `https://eel.jotform.com/edit/[DIGITS]?eapeo1e` (PCM)
     - Pattern: `https://eel.jotform.com/edit/[DIGITS]?eapet2e` (RD)
   
4. **Approval Processing**
   - Uses the extracted link to open the approval form
   - Submits approval/rejection
   - Continues to next approval stage if needed

### Fallback Behavior

If automatic retrieval fails:
- System falls back to manual input
- User can paste the link manually
- Or type 'skip' to skip that stage

## 📊 Test Suite Structure

Your test suite includes these scenarios:

### Sponsorship/Charitable Donation
- TEST_001: Happy Path (single approver)
- TEST_002: App 1 Rejection
- TEST_003: App 2 Rejects (returns to App 1)

### Goods for Resale
- TEST_004: Happy Path
- TEST_005: App 1 Rejection
- TEST_006: App 2 Rejects

### Expense Payments
- TEST_007: Happy Path
- TEST_008: App 1 Rejection
- TEST_009: App 2 Rejects

## 🎯 POC Scope (Current Implementation)

### ✅ Working Now
- PCM approver email configured
- Automatic link retrieval from YOPmail
- EFS Reference matching
- Single and multi-stage approval workflows
- All 9 test cases (3 payment types)

### 🔜 Next Steps
1. Add RD approver email address
2. Add RCM approver email address
3. Test with remaining payment types:
   - Customer Rebate
   - Sales Ledger Refund
   - Employee Expense Advance
4. Add timeout configuration options
5. Add retry logic for transient failures

## ⚙️ Technical Details

### Dependencies

```bash
# Selenium (for YOPmail)
pip install selenium

# Playwright (for JotForm automation)
pip install playwright
playwright install firefox

# Excel reporting
pip install openpyxl

# HTML parsing (optional, for future enhancements)
pip install beautifulsoup4
```

### Browser Requirements

- **Firefox** - Required for both Selenium and Playwright
- Geckodriver will be managed automatically

### Performance

- **Email polling**: 5-second intervals, max 2 minutes
- **Form operations**: ~3-5 seconds per action
- **Full test**: ~30-60 seconds per test case (depending on workflow)

## 🐛 Troubleshooting

### Email Not Found
```
❌ No approval link found after 24 attempts
💡 Check manually at: https://yopmail.com/?login=5497b0691aac47498821b0a603017505
```

**Possible causes:**
- Email hasn't arrived yet (JotForm processing delay)
- Wrong EFS Reference
- Email went to different approver
- Email format changed

**Solutions:**
- Check the YOPmail inbox manually
- Verify EFS Reference is correct
- Increase `max_attempts` in code
- Use manual fallback mode

### Selenium/Firefox Issues
```
Error: geckodriver not found
```

**Solution:**
```bash
# Install geckodriver
# On Ubuntu/Debian:
sudo apt-get install firefox-geckodriver

# On MacOS:
brew install geckodriver
```

### EFS Reference Not Extracted
```
⚠️  Could not extract EFS Reference
```

**Solution:**
- Check the thank-you page HTML structure
- Update regex pattern in `extract_efs_ref()` function
- Verify form submission was successful

## 📝 Example Output

```
====================================================================
📧 PCM Approval Link Required
====================================================================
EFS Ref: EFS-123456
🤖 Attempting automatic retrieval from YOPmail...

    🔍 Searching for approval link...
    📧 Approver: PCM
    🔖 EFS Ref: EFS-123456
    ⏱️  Max wait: 120 seconds

    [Attempt 1/24]
    📬 Loading YOPmail inbox: 5497b0691aac47498821b0a603017505
    📧 Found 3 message(s)
    🔎 Scanning 3 email(s)...
    ✅ Found email with EFS-123456
    🎯 Approval link found!

✅ Link retrieved automatically!
🔗 https://eel.jotform.com/edit/6392716199412043114?eapeo1e
====================================================================
```

## 🎓 Key Improvements Over Manual Process

### Before (Manual)
1. Submit form → Get EFS Ref
2. Wait for email notification
3. Check inbox manually
4. Find correct email
5. Copy approval link
6. Paste into test runner
7. Process approval
8. Repeat for each test

**Time per test:** ~5-10 minutes

### After (Automated)
1. Submit form → System handles everything
2. Automatic email retrieval
3. Automatic link extraction
4. Automatic approval processing

**Time per test:** ~30-60 seconds

**Time saved:** ~80-90% reduction in manual effort!

## 🔒 Security Notes

- YOPmail is a temporary email service - suitable for testing only
- Never use real sensitive data in test scenarios
- Email addresses are stored in code - consider using environment variables for production

## 📧 Support

For issues or questions:
- Check the troubleshooting section above
- Review the inline code comments
- Test the email retriever standalone first
- Verify YOPmail is accessible

## 🚀 Future Enhancements

Potential improvements:
- [ ] Add support for attachments/PDFs in emails
- [ ] Implement parallel test execution
- [ ] Add email notification on test completion
- [ ] Create dashboard for test results
- [ ] Add CI/CD integration
- [ ] Support for other email providers
- [ ] Add screenshot capture on failures
- [ ] Implement test data generation

---

**Current Status:** ✅ POC Ready for Testing (PCM Approver)

**Next Milestone:** Add RD and RCM approver support
