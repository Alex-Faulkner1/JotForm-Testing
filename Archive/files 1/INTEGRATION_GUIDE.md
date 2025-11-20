# Integration Overview - What Changed

## 🎯 Core Integration Points

### 1. Import the Email Retriever

**Added to test_runner_with_email.py:**
```python
from yopmail_link_retriever import get_approval_link_for_test
```

### 2. Updated get_approval_link() Method

**BEFORE (Manual):**
```python
def get_approval_link(self, stage_name: str, efs_ref: str) -> str:
    """Prompt user for approval link."""
    print(f"\n📧 {stage_name} Approval Link Required")
    print(f"EFS Ref: {efs_ref}")
    print(f"\nCheck your email for the {stage_name} approval email.")
    
    link = input(f"Paste {stage_name} link (or 'skip'): ").strip()
    return link if link.lower() != 'skip' else None
```

**AFTER (Automatic with Fallback):**
```python
def get_approval_link(self, stage_name: str, efs_ref: str) -> str:
    """Get approval link - automatically from YOPmail or manual input."""
    print(f"\n📧 {stage_name} Approval Link Required")
    print(f"EFS Ref: {efs_ref}")
    
    if self.auto_retrieve_links:
        print(f"🤖 Attempting automatic retrieval from YOPmail...")
        
        try:
            # AUTOMATIC RETRIEVAL HERE
            link = get_approval_link_for_test(stage_name, efs_ref)
            
            if link:
                print(f"\n✅ Link retrieved automatically!")
                print(f"🔗 {link}")
                return link
            else:
                print(f"\n⚠️  Automatic retrieval failed")
                print(f"Falling back to manual input...")
        
        except Exception as e:
            print(f"\n⚠️  Error: {e}")
            print(f"Falling back to manual input...")
    
    # Manual fallback (same as before)
    link = input(f"Paste {stage_name} link (or 'skip'): ").strip()
    return link if link.lower() != 'skip' else None
```

### 3. Added Auto-Retrieval Toggle

**BEFORE:**
```python
def __init__(self, test_suite_file: str, output_folder: str = "test_results"):
    self.test_suite_file = test_suite_file
    self.output_folder = output_folder
    # ...
```

**AFTER:**
```python
def __init__(self, test_suite_file: str, output_folder: str = "test_results",
             auto_retrieve_links: bool = True):  # NEW PARAMETER
    self.test_suite_file = test_suite_file
    self.output_folder = output_folder
    self.auto_retrieve_links = auto_retrieve_links  # NEW FLAG
    # ...
```

### 4. Updated Main Entry Point

**BEFORE:**
```python
async def main():
    runner = TestRunner(
        test_suite_file="test_suite.json",
        output_folder="test_results"
    )
    await runner.run_all_tests()
```

**AFTER:**
```python
async def main():
    runner = TestRunner(
        test_suite_file="test_suite.json",
        output_folder="test_results",
        auto_retrieve_links=True  # NEW: Enable automatic retrieval
    )
    await runner.run_all_tests()
```

## 📦 New Module: yopmail_link_retriever.py

### Key Components

#### 1. YOPmailLinkRetriever Class
```python
class YOPmailLinkRetriever:
    """Retrieve JotForm approval links from YOPmail inbox by EFS Reference."""
    
    def get_approval_link(self, approver_stage: str, efs_ref: str) -> str | None:
        """
        Main method: Searches YOPmail inbox for email with matching EFS Ref
        and extracts the JotForm edit link.
        """
```

#### 2. Email Pattern Matching
```python
def _extract_efs_ref(self, html: str) -> str | None:
    """
    Finds EFS Reference in email HTML:
    - EFS-123456
    - EFS 123456
    - EFS Ref: 123456
    """

def _extract_jotform_link(self, html: str) -> str | None:
    """
    Finds JotForm edit link:
    - https://eel.jotform.com/edit/[DIGITS]?eapeo1e (PCM)
    - https://eel.jotform.com/edit/[DIGITS]?eapet2e (RD)
    """
```

#### 3. Convenience Function
```python
def get_approval_link_for_test(approver_stage: str, efs_ref: str) -> str | None:
    """
    Simple function for test runner to call.
    
    Usage:
        link = get_approval_link_for_test("PCM", "EFS-123456")
    """
    retriever = YOPmailLinkRetriever(headless=True)
    return retriever.get_approval_link(approver_stage, efs_ref)
```

## 🔄 Execution Flow Comparison

### OLD FLOW (Manual)
```
1. Test Runner: Submit form → Get EFS Ref
2. Test Runner: Print "Check your email"
3. USER: Manually opens email
4. USER: Copies approval link
5. USER: Pastes link into terminal
6. Test Runner: Continues with approval
```
**Total time:** ~5-10 minutes per test (with manual steps)

### NEW FLOW (Automatic)
```
1. Test Runner: Submit form → Get EFS Ref
2. Test Runner: Calls get_approval_link_for_test(stage, efs_ref)
3. Email Retriever: Opens YOPmail inbox (Selenium)
4. Email Retriever: Polls for email with matching EFS Ref
5. Email Retriever: Extracts JotForm link
6. Email Retriever: Returns link to Test Runner
7. Test Runner: Continues with approval
```
**Total time:** ~30-60 seconds per test (fully automated)

## 🎨 Visual Process Flow

### Email Retrieval Process

```
┌─────────────────────┐
│  Test Runner        │
│  (Playwright)       │
└──────────┬──────────┘
           │
           │ 1. Submit Form
           ↓
┌─────────────────────┐
│  JotForm Server     │
└──────────┬──────────┘
           │
           │ 2. Send Email to Approver
           ↓
┌─────────────────────┐
│  YOPmail Inbox      │
│  (PCM: 5497b0...)   │
└──────────┬──────────┘
           │
           │ 3. get_approval_link_for_test("PCM", "EFS-123456")
           ↓
┌─────────────────────┐
│  YOPmail Retriever  │
│  (Selenium)         │
└──────────┬──────────┘
           │
           │ 4. Poll inbox (every 5s)
           │ 5. Find email with EFS-123456
           │ 6. Extract JotForm link
           ↓
┌─────────────────────┐
│  Return Link        │
│  to Test Runner     │
└─────────────────────┘
```

## 📝 Configuration Required

### yopmail_link_retriever.py

```python
APPROVER_EMAILS = {
    "PCM": "5497b0691aac47498821b0a603017505@yopmail.com",
    
    # TODO: Add these when ready
    # "RD": "your_rd_email@yopmail.com",
    # "RCM": "your_rcm_email@yopmail.com",
}
```

### No changes needed to:
- `test_suite.json` - Works as-is
- `config.py` - Works as-is
- `utils.py` - Works as-is

## 🚀 Usage Examples

### Example 1: Run with Auto-Retrieval (Default)
```python
runner = TestRunner(
    test_suite_file="test_suite.json",
    output_folder="test_results",
    auto_retrieve_links=True  # Enabled
)
await runner.run_all_tests()
```

### Example 2: Disable Auto-Retrieval
```python
runner = TestRunner(
    test_suite_file="test_suite.json",
    output_folder="test_results",
    auto_retrieve_links=False  # Manual input only
)
await runner.run_all_tests()
```

### Example 3: Standalone Email Retrieval
```python
from yopmail_link_retriever import get_approval_link_for_test

# Get link for specific EFS Ref
link = get_approval_link_for_test("PCM", "EFS-123456")

if link:
    print(f"Found link: {link}")
else:
    print("Link not found")
```

## 🎯 Benefits Summary

### Time Savings
- **Before:** 5-10 minutes per test (manual)
- **After:** 30-60 seconds per test (automatic)
- **Reduction:** ~80-90% time saved

### Reliability
- **Before:** Prone to copy/paste errors
- **After:** Automated extraction, no human error

### Scalability
- **Before:** Can't run unattended
- **After:** Can run overnight/unattended

### Maintainability
- **Before:** Manual process documentation needed
- **After:** Self-documenting code

## 🔧 Customization Points

### Adjust Polling Behavior
```python
# In yopmail_link_retriever.py
def get_approval_link(self, approver_stage: str, efs_ref: str, 
                     max_attempts: int = 24,    # Change this
                     poll_interval: int = 5):   # Or this
```

### Add New Approver Stages
```python
# In yopmail_link_retriever.py
APPROVER_EMAILS = {
    "PCM": "email1@yopmail.com",
    "RD": "email2@yopmail.com",
    "RCM": "email3@yopmail.com",
    "NEW_STAGE": "email4@yopmail.com",  # Just add here
}
```

### Modify Link Patterns
```python
# In yopmail_link_retriever.py
def _extract_jotform_link(self, html: str) -> str | None:
    # Current pattern
    pattern = r"(https://eel\.jotform\.com/edit/\d+\?(?:eapeo1e|eapet2e))"
    
    # Add new patterns if link format changes
    pattern = r"(https://eel\.jotform\.com/edit/\d+\?(?:eapeo1e|eapet2e|newtype))"
```

## ✨ That's It!

The integration is minimal and clean:
- ✅ One new module (`yopmail_link_retriever.py`)
- ✅ One import statement
- ✅ One method updated (`get_approval_link`)
- ✅ One parameter added (`auto_retrieve_links`)

Everything else stays the same! 🎉
