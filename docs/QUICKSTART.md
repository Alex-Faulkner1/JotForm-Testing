# Quick Start Guide

Get up and running with JotForm automation in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.8 or higher installed
- [ ] Git installed
- [ ] GitHub SSH key configured (for cloning)

## Installation (5 Steps)

### 1. Clone the Repository

```bash
git clone git@github.com:Alex-Faulkner1/JotForm-Testing.git
cd JotForm-Testing
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Run Setup Script

```bash
python setup.py
```

This will:
- ✅ Check Python version
- ✅ Create necessary directories
- ✅ Install dependencies
- ✅ Install Playwright browsers
- ✅ Verify installation

### 4. Configure (Optional)

Edit `config.py` to customize:

```python
# Update email addresses
EMAILS = {
    "pcm_email": "your.pcm@example.com",  # ← Change this
    "rd_email": "your.rd@example.com",     # ← Change this
}

# Update test data if needed
TEST_DATA = {
    "location_number": "331",  # ← Your location
    # ... other fields
}
```

### 5. Run!

```bash
python main.py
```

## What Happens?

1. **PDF Generated**: Creates `invoice.pdf`
2. **Stage 1**: Fills and submits inputter form
3. **Stage 2**: Approves at PCM level
4. **Stage 3**: Approves at RD level
5. **Output**: Screenshots saved in `output/EFS[number]/`

## Expected Output

```
===== STAGE 1: INPUTTER STAGE =====
Navigated to form
Completed: Company / Division
Completed: Location Number
...
Found EFS Ref: EFS123456
Created output folder: output/EFS123456

===== PCM STAGE =====
Navigated to PCM Stage form
...

===== RD STAGE =====
Navigated to RD Stage form
...

===== ALL STAGES COMPLETED SUCCESSFULLY =====
All screenshots saved in folder: output/EFS123456
```

## Verify Success

Check the `output/` folder:

```
output/
└── EFS123456/
    ├── stage1_submitted.png
    ├── pcm_stage_submitted.png
    └── rd_stage_submitted.png
```

## Troubleshooting

### "Command not found: python"

Try `python3` instead:
```bash
python3 main.py
```

### "playwright: command not found"

Run manually:
```bash
pip install playwright
playwright install chromium
```

### "Permission denied"

On Unix systems:
```bash
chmod +x setup.py
./setup.py
```

### Want to See the Browser?

Edit `config.py`:
```python
HEADLESS_MODE = False  # Change from True
```

## Next Steps

- [ ] Read the full [README.md](../README.md)
- [ ] Check out [TECHNICAL.md](TECHNICAL.md) for advanced usage
- [ ] Customize test data in `config.py`
- [ ] Add your own test scenarios
- [ ] Run tests: `pytest tests/`

## Common Commands

```bash
# Activate virtual environment
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# Run automation
python main.py

# Run tests
pytest tests/ -v

# Deactivate virtual environment
deactivate
```

## Getting Help

- Check [README.md](../README.md) for detailed documentation
- Review [TECHNICAL.md](TECHNICAL.md) for architecture details
- Contact: Test Automation Team

## Test Multiple Scenarios

Edit `config.py` between runs to test different scenarios:

```python
# Scenario 1: Different payment type
TEST_DATA = {
    "payment_type": "Customer Rebate",
    # ...
}

# Scenario 2: Different location
TEST_DATA = {
    "location_number": "999",
    # ...
}
```

---

**You're all set! Happy testing! 🚀**
