# Technical Documentation

## Architecture Overview

The JotForm automation is built using a modular architecture that separates concerns:

```
┌─────────────┐
│   main.py   │  ← Orchestrates the workflow
└──────┬──────┘
       │
       ├──→ ┌──────────────┐
       │    │  config.py   │  ← Configuration and settings
       │    └──────────────┘
       │
       └──→ ┌──────────────┐
            │  utils.py    │  ← Helper functions
            └──────────────┘
```

## Workflow Stages

### Stage 1: Inputter (Form Submission)

**Purpose**: Initial form submission by the requester

**Key Functions**:
- `fill_inputter_stage()` - Fills all form fields
- `select_approver()` - Selects approver from iframe dropdown
- `submit_inputter_stage()` - Submits form and extracts EFS ref

**Selectors Used**:
```python
"#input_123"    # Company/Division dropdown
"#input_124"    # Location Number
"#input_131"    # Raised By
"#lite_mode_130" # Payment Request Date
"#input_543"    # Payment Request Type
"#input_701"    # Description
"#input_547"    # Payee
"#label_input_604_0" # Has Invoice (Yes)
"#input_558"    # File Upload
"#input_562"    # Invoice Number
"#lite_mode_566" # Invoice Date
"#label_input_607_0" # Bank Details (Yes)
"#input_844"    # Value
"#input_195"    # PCM Email
"#input_98"     # Submit Button
```

**Iframe Handling**:
The approver dropdown is embedded in an iframe. The script:
1. Iterates through all frames
2. Finds the frame containing "ADDropdown"
3. Selects the second option (first is usually blank)

**Output**:
- EFS Reference number (e.g., "EFS123456")
- Edit link for next stage
- Screenshot: `stage1_submitted.png`

### Stage 2: PCM (Profit Centre Manager Approval)

**Purpose**: Manager reviews and approves/rejects the request

**Key Functions**:
- `process_pcm_stage()` - Handles entire PCM stage

**Selectors Used**:
```python
"#label_input_203_0" # Approve radio button
"#input_244"         # RD Email
"#input_98"          # Submit Button
```

**Output**:
- Edit link for RD stage
- Screenshot: `pcm_stage_submitted.png`

### Stage 3: RD (Regional Director Approval)

**Purpose**: Final approval by Regional Director

**Key Functions**:
- `process_rd_stage()` - Handles entire RD stage

**Selectors Used**:
```python
"#label_input_249_0" # Approve radio button
"#input_98"          # Submit Button
```

**Output**:
- Final confirmation
- Screenshot: `rd_stage_submitted.png`

## Data Flow

```
┌──────────────┐
│ Generate PDF │
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│  Fill Form       │
│  (Stage 1)       │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Extract EFS Ref │
│  & Edit Link     │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Create Output   │
│  Folder          │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Wait for        │
│  Workflows       │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  PCM Approval    │
│  (Stage 2)       │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Wait for        │
│  Workflows       │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  RD Approval     │
│  (Stage 3)       │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│  Complete        │
└──────────────────┘
```

## Error Handling

### Redirect Detection

The script includes retry logic for form submissions:

```python
async def wait_for_redirect(page, initial_url, timeout):
    # Wait for redirect
    await page.wait_for_timeout(timeout)
    
    # Check if URL changed
    if page.url == initial_url:
        # Retry once
        await page.click("#input_98")
        await page.wait_for_timeout(timeout)
        
        # Final check
        if page.url == initial_url:
            return False  # Failed
    
    return True  # Success
```

### Common Failure Points

1. **Approver dropdown not found**
   - Cause: Iframe not loaded or selector changed
   - Mitigation: Wait logic, error messages

2. **No redirect after submit**
   - Cause: Network issues, form validation errors
   - Mitigation: Retry logic, timeout adjustments

3. **EFS Ref not found**
   - Cause: Page structure changed
   - Mitigation: Regex pattern matching, error messages

## Configuration

### Test Data Structure

```python
TEST_DATA = {
    "company_division": str,      # Dropdown label
    "location_number": str,        # Text input
    "raised_by": str,              # Text input
    "payment_type": str,           # Dropdown label
    "description": str,            # Text input
    "payee": str,                  # Text input
    "has_invoice": bool,           # Radio button
    "invoice_filename": str,       # File path
    "invoice_number": str,         # Text input
    "invoice_date": str,           # Date (DDMMYYYY)
    "bank_details_on_invoice": bool, # Radio button
    "value": str,                  # Number input
}
```

### Timing Configuration

- **WORKFLOW_WAIT_TIME**: Time to wait between stages for background processes (default: 10s)
- **REDIRECT_TIMEOUT**: Time to wait for page redirect (default: 3s)
- **BROWSER_TIMEOUT**: General browser timeout (default: 30s)

## Extending the Automation

### Adding a New Payment Type

1. Update `TEST_DATA` in `config.py`:
   ```python
   "payment_type": "New Payment Type",
   ```

2. Check if new fields are required for this type

3. Add conditional logic if field visibility changes:
   ```python
   if TEST_DATA["payment_type"] == "New Payment Type":
       # Handle type-specific fields
       await page.fill("#special_field", "value")
   ```

### Adding a New Approval Stage

1. Create a new function in `main.py`:
   ```python
   async def process_new_stage(page, stage_url, output_folder):
       print("\n===== NEW STAGE =====")
       await page.goto(stage_url)
       
       # Fill fields
       # ...
       
       # Submit
       await page.click("#input_98")
       
       # Save screenshot
       await page.screenshot(path=f"{output_folder}/new_stage.png")
       
       # Extract next stage URL
       content = await page.content()
       return extract_edit_link(content)
   ```

2. Add to workflow in `run_automation()`:
   ```python
   new_stage_url = await process_new_stage(page, current_url, output_folder)
   ```

## Performance Considerations

### Browser Headless Mode

- **Headless=True**: Faster, no visual overhead
- **Headless=False**: Slower but useful for debugging

### Wait Strategies

The script uses explicit waits:
- `page.wait_for_timeout()`: Fixed wait times
- Consider using `page.wait_for_selector()` for dynamic loading

### Screenshot Optimization

Screenshots are PNG format. Consider:
- Using JPEG for smaller file sizes
- Reducing quality if size is an issue
- Taking screenshots only on errors

## Security Considerations

### Credentials

- Never commit actual email addresses to version control
- Use environment variables for sensitive data
- Consider using `.env` file (already in `.gitignore`)

### File Handling

- Generated PDFs are not committed (in `.gitignore`)
- Output folders are excluded from version control

## Debugging Tips

### Enable Visual Mode

Set in `config.py`:
```python
HEADLESS_MODE = False
```

### Add Debug Screenshots

```python
await page.screenshot(path=f"{output_folder}/debug_{step_name}.png")
```

### Console Logging

Playwright captures console logs:
```python
page.on("console", lambda msg: print(f"Browser: {msg.text}"))
```

### Network Monitoring

Monitor network requests:
```python
page.on("request", lambda req: print(f"→ {req.method} {req.url}"))
page.on("response", lambda res: print(f"← {res.status} {res.url}"))
```

## Future Enhancements

1. **Parallel Execution**: Run multiple test cases simultaneously
2. **Report Generation**: Create HTML/PDF test reports
3. **Email Integration**: Parse approval emails instead of using edit links
4. **Database Integration**: Store test results in database
5. **CI/CD Integration**: Run tests on commit/schedule
6. **Dynamic Selectors**: Handle selector changes automatically
7. **Test Data from Files**: Load test data from CSV/Excel

## Troubleshooting Common Issues

### Issue: Selectors Not Found

**Symptoms**: Element not found errors

**Solutions**:
1. Check if form structure changed
2. Use browser dev tools to find new selectors
3. Update selectors in code
4. Add wait conditions before interacting

### Issue: Iframe Content Not Accessible

**Symptoms**: Cannot find approver dropdown

**Solutions**:
1. Verify iframe is loaded: `await page.wait_for_selector("iframe")`
2. Check iframe name/URL patterns
3. Use `page.frame_locator()` for modern Playwright

### Issue: Form Validation Errors

**Symptoms**: Form doesn't submit, no redirect

**Solutions**:
1. Check console for validation messages
2. Verify all required fields are filled
3. Check date format matches expected format
4. Ensure file uploads complete before submit

## API Reference

### Main Functions

#### `run_automation()`
Main entry point. Orchestrates entire workflow.

**Returns**: None

**Raises**: Exception on critical errors

#### `fill_inputter_stage(page)`
Fills all fields in Stage 1 form.

**Args**:
- `page` (Page): Playwright page object

**Returns**: None

#### `process_pcm_stage(page, pcm_url, output_folder)`
Handles PCM approval stage.

**Args**:
- `page` (Page): Playwright page object
- `pcm_url` (str): URL for PCM stage
- `output_folder` (str): Path for screenshots

**Returns**: str - URL for next stage or None

#### `process_rd_stage(page, rd_url, output_folder)`
Handles RD approval stage.

**Args**:
- `page` (Page): Playwright page object
- `rd_url` (str): URL for RD stage  
- `output_folder` (str): Path for screenshots

**Returns**: bool - Success status

### Utility Functions

#### `make_test_pdf(filename, output_dir)`
Generates a test PDF invoice.

**Args**:
- `filename` (str): PDF filename
- `output_dir` (str, optional): Output directory

**Returns**: str - Path to created PDF

#### `extract_efs_ref(page_content)`
Extracts EFS reference from HTML content.

**Args**:
- `page_content` (str): HTML content

**Returns**: str - EFS reference or None

#### `extract_edit_link(page_content)`
Extracts edit URL from HTML content.

**Args**:
- `page_content` (str): HTML content

**Returns**: str - Edit URL or None
