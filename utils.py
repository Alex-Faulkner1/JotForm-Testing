"""
Utility functions for JotForm automation
"""
import html
import os
import re
from reportlab.pdfgen import canvas


def make_test_pdf(filename="invoice.pdf", output_dir=None):
    """
    Generate a simple test PDF invoice.
    
    Args:
        filename: Name of the PDF file to create
        output_dir: Directory to save the PDF in (optional)
    
    Returns:
        str: Full path to the created PDF
    """
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        filepath = os.path.join(output_dir, filename)
    else:
        filepath = filename
    
    c = canvas.Canvas(filepath)
    c.drawString(100, 750, "Test Invoice PDF – Automated Upload")
    c.save()
    
    return filepath


import re
from html import unescape


def extract_efs_ref(html_content: str) -> str | None:
    """
    Extract EFS Reference from HTML content.

    Handles:
    - HTML entities like &nbsp;
    - Various spacing patterns
    - Alphanumeric formats: DEV_PR395, TEST_001
    - Numeric formats: EFS-123456, 123456

    Args:
        html_content: HTML content containing EFS reference

    Returns:
        EFS reference string or None if not found
    """
    # IMPORTANT: Decode HTML entities (&nbsp; → space, etc.)
    decoded_html = unescape(html_content)

    # Try multiple patterns in order of specificity
    patterns = [
        # Pattern 1: "EFS Ref:" or "EFS Reference:" followed by alphanumeric
        # \s* means "zero or more spaces"
        r"EFS\s+Ref(?:erence)?:?\s*([A-Z]+_[A-Z0-9_]+)",

        # Pattern 2: Already formatted with EFS- prefix
        r"(?:EFS\s+)?Ref(?:erence)?:?\s*(EFS-\d+)",

        # Pattern 3: Just numbers after "Reference:"
        r"(?:EFS\s+)?Ref(?:erence)?:?\s*(\d{6})",

        # Pattern 4: Generic "Reference:" with alphanumeric
        r"Reference:?\s*([A-Z]+_[A-Z0-9_]+)",

        # Pattern 5: EFS followed by space and numbers
        r"\bEFS\s+(\d{6})\b",

        # Pattern 6: In URLs or standalone
        r"\bEFS-(\d{6})\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, decoded_html, re.IGNORECASE)
        if match:
            ref = match.group(1)

            # If it's already prefixed with EFS-, return as-is
            if ref.startswith("EFS-"):
                return ref

            # If it's purely numeric (6 digits), format as EFS-XXXXXX
            if ref.isdigit() and len(ref) == 6:
                return f"EFS-{ref}"

            # Otherwise return as-is (e.g., DEV_PR395, TEST_001)
            return ref

    return None


def extract_edit_link(page_content):
    """
    Extract the edit link from thank you page content.
    
    Args:
        page_content: HTML content of the page
    
    Returns:
        str: Edit URL or None if not found
    """
    edit_link_match = re.search(r'https://eel\.jotform\.com/edit/[^\s\'"<>]+', page_content)
    return edit_link_match.group(0) if edit_link_match else None


def create_output_folder(folder_name, base_dir="output"):
    """
    Create an output folder for storing screenshots and artifacts.
    
    Args:
        folder_name: Name of the folder to create
        base_dir: Base directory for output folders
    
    Returns:
        str: Path to the created folder
    """
    folder_path = os.path.join(base_dir, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    return folder_path
