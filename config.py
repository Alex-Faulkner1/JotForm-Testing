"""
Configuration file for JotForm Payment Request automation
"""
import os
from datetime import date, timedelta

# JotForm URL
JOTFORM_URL = "https://eel.jotform.com/252244495892972"

# Browser Settings
HEADLESS_MODE = True
BROWSER_TIMEOUT = 30000  # milliseconds

# Test Data - Inputter Stage
TEST_DATA = {
    "company_division": "Edmundson Electrical",
    "location_number": "331",
    "raised_by": "Automated Test",
    "payment_type": "Sponsorship/Charitable Donation",
    "description": "Test Description",
    "payee": "Test Auto",
    "has_invoice": True,
    "invoice_filename": "invoice.pdf",
    "invoice_number": "Invoice123",
    "invoice_date": (date.today() - timedelta(days=1)).strftime("%d%m%Y"),
    "bank_details_on_invoice": True,
    "value": "10000",
}

# Email addresses for testing
EMAILS = {
    "pcm_email": "mustapha.jobe@digiblu.com",
    "rd_email": "mustapha.jobe@digiblu.com",
}

# Output Settings
OUTPUT_DIR = "output"
CREATE_TIMESTAMPED_FOLDERS = True

# Workflow Settings
WORKFLOW_WAIT_TIME = 10000  # milliseconds between stages
REDIRECT_TIMEOUT = 3000  # milliseconds to wait for redirect
