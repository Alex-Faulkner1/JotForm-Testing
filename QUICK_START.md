# 🚀 Quick Start Guide - Test Automation Suite

## ⚡ 5-Minute Setup

### 1. Navigate to Project
```bash
cd ~/Documents/GitHub/JotForm-Testing
```

### 2. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 3. Verify Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Test Suite
```bash
python test_runner.py
```

## 📧 During Test Execution

You'll be prompted for approval links from your email:

### Step 1: Form Submission
The script fills and submits the form automatically.

### Step 2: Check Email
After Stage 1 submission, you'll see:
```
============================================================
📧 PCM Approval Link Required
============================================================
EFS Ref: DEV_PR370

Please check your email for the PCM approval email.
Expected link format: https://eel.jotform.com/edit/############?eapeo1e
============================================================

Paste PCM link (or 'skip'):
```

**What to do:**
1. Open your email
2. Search for "DEV_PR370" (the EFS Ref shown)
3. Open the email
4. Copy the link from "Click here" button
5. Paste into terminal
6. Press ENTER

### Step 3: Review & Submit
The script will navigate to the approval form.
You'll see a pause:
```
⏸️  Review PCM form and press ENTER to submit...
```

**What to do:**
1. Look at the browser window
2. Verify the form looks correct
3. Press ENTER to submit

### Step 4: Repeat for Next Stage
If the test has multiple approval stages, repeat steps 2-3.

## 📊 After All Tests Complete

You'll see a summary:
```
============================================================
TEST EXECUTION COMPLETE
============================================================
Total Tests: 9
Passed: 7
Failed: 1
Errors: 1

📊 Report: test_results/test_results_20241117_143000.xlsx
📁 Screenshots: test_results/
============================================================
```

## 🎯 Test Results

### Excel Report Location
```
test_results/test_results_TIMESTAMP.xlsx
```

### Screenshots Location
```
test_results/
├── TEST_001_DEV_PR370/
│   ├── stage1_submitted.png
│   ├── pcm_approve.png
│   └── ...
├── TEST_002_DEV_PR371/
│   └── ...
└── test_results_20241117_143000.xlsx
```

## 🐛 Quick Troubleshooting

### Problem: "No approval buttons found"
**Solution:** Wait a few more seconds, then run again. The form might still be loading.

### Problem: Can't find approval email
**Solution:** 
1. Check spam/junk folder
2. Search for the EFS Ref (e.g., "DEV_PR370")
3. Wait 30 seconds - emails can be delayed

### Problem: Form validation errors
**Solution:** Check the browser window for red error messages. The script pauses so you can see them.

## 💡 Tips

1. **Keep email tab open** - You'll need to check it multiple times
2. **Copy full URL** - Include everything starting with `https://`
3. **Don't close browser** - The script needs it open
4. **Review before submitting** - You get a chance to check each form
5. **Check Excel report** - It has all the details including error messages

## 🎓 What Each Test Does

| Test | What It Tests | Expected Result |
|------|---------------|-----------------|
| TEST_001-003 | Sponsorship forms | Approve/Reject/Return flows |
| TEST_004-006 | Goods for Resale | Approve/Reject/Return flows |
| TEST_007-009 | Expense Payments | Approve/Reject/Return flows |

## 📞 Need Help?

1. Check `TEST_SUITE_README.md` for detailed documentation
2. Look at screenshots in `test_results/` folder
3. Open Excel report for error details
4. Check console output for debug messages

## ⏱️ How Long Does It Take?

- **Per test:** 2-5 minutes (depending on how quickly you provide links)
- **Full suite (9 tests):** ~30-45 minutes

## 🔄 Running Individual Tests

Want to test just one scenario?

```bash
python main_manual_links.py
```

This runs the manual mode for a single test case (currently configured for Sponsorship).

---

**That's it! You're ready to run automated tests.** 🎉

For more details, see `TEST_SUITE_README.md`
