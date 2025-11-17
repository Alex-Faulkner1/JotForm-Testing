"""
Utility functions for JotForm automation
"""
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


def extract_efs_ref(page_content):
    """
    Extract EFS Reference from thank you page content.
    
    Args:
        page_content: HTML content of the page
    
    Returns:
        str: EFS Reference or None if not found
    """
    efs_ref_match = re.search(r'EFS Ref:\s*(\S+)', page_content)
    return efs_ref_match.group(1) if efs_ref_match else None


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
