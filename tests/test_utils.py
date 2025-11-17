"""
Unit tests for JotForm automation utilities
"""
import pytest
from utils import extract_efs_ref, extract_edit_link, make_test_pdf
import os


class TestEFSRefExtraction:
    """Test EFS reference extraction from page content."""
    
    def test_extract_valid_efs_ref(self):
        """Test extraction of valid EFS reference."""
        content = "Thank you! EFS Ref: EFS123456 has been submitted."
        result = extract_efs_ref(content)
        assert result == "EFS123456"
    
    def test_extract_efs_ref_not_found(self):
        """Test when EFS reference is not in content."""
        content = "Thank you for your submission!"
        result = extract_efs_ref(content)
        assert result is None
    
    def test_extract_efs_ref_with_special_chars(self):
        """Test EFS reference with alphanumeric characters."""
        content = "EFS Ref: EFS-2024-001A submitted successfully"
        result = extract_efs_ref(content)
        assert result == "EFS-2024-001A"


class TestEditLinkExtraction:
    """Test edit link extraction from page content."""
    
    def test_extract_valid_edit_link(self):
        """Test extraction of valid edit link."""
        content = '''
        <a href="https://eel.jotform.com/edit/241234567890123">Edit</a>
        '''
        result = extract_edit_link(content)
        assert result == "https://eel.jotform.com/edit/241234567890123"
    
    def test_extract_edit_link_not_found(self):
        """Test when edit link is not in content."""
        content = "<p>Thank you for your submission</p>"
        result = extract_edit_link(content)
        assert result is None
    
    def test_extract_edit_link_multiple_links(self):
        """Test extraction when multiple links exist (returns first)."""
        content = '''
        <a href="https://eel.jotform.com/edit/111111111111111">First</a>
        <a href="https://eel.jotform.com/edit/222222222222222">Second</a>
        '''
        result = extract_edit_link(content)
        assert result == "https://eel.jotform.com/edit/111111111111111"


class TestPDFGeneration:
    """Test PDF generation functionality."""
    
    def test_make_test_pdf_default(self):
        """Test PDF creation with default filename."""
        filename = "test_invoice.pdf"
        result = make_test_pdf(filename)
        
        assert os.path.exists(result)
        assert result == filename
        
        # Cleanup
        if os.path.exists(filename):
            os.remove(filename)
    
    def test_make_test_pdf_with_directory(self):
        """Test PDF creation with output directory."""
        output_dir = "test_output"
        filename = "invoice.pdf"
        
        result = make_test_pdf(filename, output_dir)
        
        assert os.path.exists(result)
        assert result == os.path.join(output_dir, filename)
        
        # Cleanup
        if os.path.exists(result):
            os.remove(result)
        if os.path.exists(output_dir):
            os.rmdir(output_dir)


# To run these tests:
# pip install pytest
# pytest tests/test_utils.py -v
