#!/usr/bin/env python3
"""
File Verification Script
Run this to verify all project files are present
"""
import os
import sys

def check_file(filepath, description):
    """Check if a file exists and print result."""
    exists = os.path.exists(filepath)
    size = os.path.getsize(filepath) if exists else 0
    status = "✅" if exists else "❌"
    
    print(f"{status} {description}")
    if exists:
        print(f"   └─ {filepath} ({size:,} bytes)")
    else:
        print(f"   └─ MISSING: {filepath}")
    
    return exists

def main():
    """Check all project files."""
    print("\n" + "="*60)
    print("JotForm Testing - File Verification")
    print("="*60 + "\n")
    
    files_to_check = [
        # Python files
        ("main.py", "Main automation script"),
        ("config.py", "Configuration settings"),
        ("utils.py", "Helper functions"),
        ("setup.py", "Setup script"),
        ("__init__.py", "Package initialization"),
        ("tests/__init__.py", "Tests package init"),
        ("tests/test_utils.py", "Unit tests"),
        
        # Documentation
        ("README.md", "Main documentation"),
        ("CHANGELOG.md", "Version history"),
        ("docs/QUICKSTART.md", "Quick start guide"),
        ("docs/TECHNICAL.md", "Technical documentation"),
        
        # Configuration
        ("requirements.txt", "Python dependencies"),
        (".gitignore", "Git ignore rules"),
        (".env.example", "Environment template"),
    ]
    
    print("📋 Checking Files...\n")
    
    all_present = True
    for filepath, description in files_to_check:
        if not check_file(filepath, description):
            all_present = False
    
    print("\n" + "="*60)
    
    if all_present:
        print("✅ ALL FILES PRESENT - Project is complete!")
        print("\nYou can now run:")
        print("  python setup.py")
        print("  python main.py")
    else:
        print("❌ SOME FILES MISSING - Please re-download the project")
        sys.exit(1)
    
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
