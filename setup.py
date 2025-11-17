#!/usr/bin/env python3
"""
Setup script for JotForm Testing automation
Initializes the project and checks dependencies
"""
import subprocess
import sys
import os


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def check_python_version():
    """Check if Python version is 3.8 or higher."""
    print_header("Checking Python Version")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True


def create_directories():
    """Create necessary directories."""
    print_header("Creating Directories")
    dirs = ['output', 'tests', 'docs']
    for dir_name in dirs:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"✅ Created: {dir_name}/")
        else:
            print(f"⏭️  Already exists: {dir_name}/")


def install_dependencies():
    """Install Python dependencies."""
    print_header("Installing Dependencies")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], 
                      check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        return False


def install_playwright_browsers():
    """Install Playwright browsers."""
    print_header("Installing Playwright Browsers")
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
        print("✅ Chromium browser installed successfully")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install Playwright browsers")
        return False
    except FileNotFoundError:
        print("❌ Playwright not found. Please install dependencies first.")
        return False


def verify_setup():
    """Verify that all components are properly installed."""
    print_header("Verifying Setup")
    
    # Check if main files exist
    required_files = ['main.py', 'config.py', 'utils.py', 'requirements.txt']
    all_exist = True
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} not found")
            all_exist = False
    
    return all_exist


def main():
    """Main setup function."""
    print("\n" + "🚀" * 30)
    print("  JotForm Testing - Setup Script")
    print("🚀" * 30)
    
    steps = [
        ("Python Version", check_python_version),
        ("Directories", create_directories),
        ("Dependencies", install_dependencies),
        ("Playwright Browsers", install_playwright_browsers),
        ("Verification", verify_setup)
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        if not step_func():
            failed_steps.append(step_name)
    
    print_header("Setup Complete")
    
    if not failed_steps:
        print("✅ All setup steps completed successfully!")
        print("\nYou can now run the automation:")
        print("  python main.py")
    else:
        print("⚠️  Setup completed with some issues:")
        for step in failed_steps:
            print(f"  - {step}")
        print("\nPlease resolve the issues above before running.")
    
    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()
