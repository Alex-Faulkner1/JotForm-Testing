# JotForm Payment Request Automation

Automated testing suite for JotForm payment request workflows with multi-stage approval processes.

## Overview

This project automates the end-to-end testing of JotForm payment request forms, covering:
- **Stage 1**: Inputter submission (form filling and initial submission)
- **Stage 2**: Profit Centre Manager (PCM) approval
- **Stage 3**: Regional Director (RD) approval

The automation uses Playwright to interact with JotForm, captures screenshots at each stage, and organizes outputs by EFS reference number.

## Features

- ✅ Automated form filling with configurable test data
- ✅ Multi-stage approval workflow automation
- ✅ Screenshot capture at each stage
- ✅ PDF invoice generation for testing
- ✅ Organized output folders by EFS reference
- ✅ Error handling and retry logic
- ✅ Configurable settings via `config.py`
- ✅ Modular code structure for easy maintenance

## Project Structure

```
jotform-testing/
├── main.py              # Main automation script
├── config.py            # Configuration settings
├── utils.py             # Helper functions
├── requirements.txt     # Python dependencies
├── README.md            # This file
├── .gitignore          # Git ignore rules
├── output/             # Generated test outputs (auto-created)
│   └── [EFS_REF]/      # Folders created per test run
│       ├── stage1_submitted.png
│       ├── pcm_stage_submitted.png
│       └── rd_stage_submitted.png
├── tests/              # Unit tests (future)
└── docs/               # Additional documentation (future)
```

## Prerequisites

- Python 3.8 or higher
- Git

## Installation

### 1. Clone the Repository

```bash
git clone git@github.com:Alex-Faulkner1/JotForm-Testing.git
cd JotForm-Testing
```

### 2. Create a Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers

```bash
playwright install chromium
```

## Configuration

Edit `config.py` to customize:

### Test Data
```python
TEST_DATA = {
    "company_division": "Edmundson Electrical",
    "location_number": "331",
    "payment_type": "Sponsorship/Charitable Donation",
    # ... other fields
}
```

### Email Addresses
```python
EMAILS = {
    "pcm_email": "your.email@example.com",
    "rd_email": "your.email@example.com",
}
```

### Browser Settings
```python
HEADLESS_MODE = True  # Set to False to see browser actions
BROWSER_TIMEOUT = 30000  # Timeout in milliseconds
```

## Usage

### Basic Usage

Run the automation with default settings:

```bash
python main.py
```

### What Happens

1. **PDF Generation**: Creates a test invoice PDF
2. **Stage 1 - Inputter**: 
   - Fills out all form fields
   - Uploads the test PDF
   - Submits the form
   - Captures EFS reference
3. **Stage 2 - PCM**: 
   - Navigates to PCM approval form
   - Approves the request
   - Submits and captures screenshot
4. **Stage 3 - RD**: 
   - Navigates to RD approval form
   - Approves the request
   - Completes workflow

### Output

All screenshots and artifacts are saved in:
```
output/[EFS_REF_NUMBER]/
```

Example:
```
output/EFS123456/
├── stage1_submitted.png
├── pcm_stage_submitted.png
└── rd_stage_submitted.png
```

## Development

### Running in Non-Headless Mode

For debugging, set headless mode to False in `config.py`:

```python
HEADLESS_MODE = False
```

### Adding New Test Scenarios

1. Modify `TEST_DATA` in `config.py` with your test case
2. Run `main.py` to execute
3. Review output in the generated folder

### Extending Functionality

- **New Stages**: Add new functions in `main.py` following the pattern of `process_pcm_stage()`
- **New Fields**: Update `fill_inputter_stage()` to include additional form fields
- **Utilities**: Add helper functions to `utils.py`

## Troubleshooting

### Common Issues

**Issue**: Browser fails to launch
- **Solution**: Run `playwright install chromium` to ensure browsers are installed

**Issue**: Form fields not found
- **Solution**: Check if JotForm selectors have changed; update selectors in `main.py`

**Issue**: No redirect after submit
- **Solution**: Check network conditions; the script includes retry logic but may need adjustment

**Issue**: PDF generation fails
- **Solution**: Ensure `reportlab` is installed: `pip install reportlab`

### Debug Mode

To see the browser in action and debug issues:
1. Set `HEADLESS_MODE = False` in `config.py`
2. Run the script
3. Watch the browser automation in real-time

## Testing

### Manual Testing

Run the script and verify:
- All form fields are filled correctly
- Screenshots are captured
- Output folders are created with correct EFS reference
- All stages complete successfully

### Future: Unit Tests

```bash
# When tests are added
pytest tests/
```

## Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Test thoroughly
4. Commit: `git commit -m "Add your feature"`
5. Push: `git push origin feature/your-feature`
6. Create a Pull Request

## Payment Types Supported

Currently configured for:
- Sponsorship/Charitable Donation

Can be extended to support:
- Goods for Resale
- Expense Payments
- Customer Rebate
- Sales Ledger Refund
- Employee Expense Advance

## Roadmap

- [ ] Add unit tests
- [ ] Support for all 6 payment types
- [ ] Email approval workflow integration
- [ ] Batch processing capabilities
- [ ] Test report generation
- [ ] CI/CD integration
- [ ] Configuration via environment variables
- [ ] Rejection flow testing

## Dependencies

- `playwright` - Browser automation
- `reportlab` - PDF generation
- `python-dotenv` - Environment variable management (future use)

## License

Internal use for DigiBlun/Experience Travel Group

## Contact

For questions or issues, contact the Test Automation team.

---

**Note**: This automation is for testing purposes only. Ensure you have proper authorization before running automated tests against production forms.
