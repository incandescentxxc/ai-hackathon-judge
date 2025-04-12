#!/usr/bin/env python3
"""
Setup script for the AI Judge system.
Handles installation of dependencies and configuration setup.
"""

import os
import sys
import subprocess
import re
import json
from src.extractor import extract_from_file

def check_python_version():
    """Check that Python version is 3.6+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 6):
        print("Error: Python 3.6 or higher is required.")
        print(f"Current version: {version.major}.{version.minor}.{version.micro}")
        return False
    print(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def install_dependencies():
    """Install required dependencies"""
    print("\nInstalling dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully.")
        return True
    except Exception as e:
        print(f"Error installing dependencies: {e}")
        print("You may need to manually install the dependencies listed in requirements.txt")
        return False

def setup_config():
    """Set up the configuration"""
    print("\nSetting up configuration...")
    
    # Check if config.py already exists
    if os.path.exists('config.py'):
        overwrite = input("config.py already exists. Overwrite? (y/n): ")
        if overwrite.lower() != 'y':
            print("✓ Using existing configuration.")
            return True
    
    # Ask if user has a curl command
    has_curl = input("Do you have a curl command from your browser? (y/n): ")
    if has_curl.lower() == 'y':
        # Setup using curl command
        curl_file = input("Enter path to curl command file (default: curl.txt): ") or 'curl.txt'
        if not os.path.exists(curl_file):
            print(f"File {curl_file} not found. Let's create it.")
            print("Please paste your curl command below (press Ctrl+D or Ctrl+Z on a new line when done):")
            curl_content = sys.stdin.read().strip()
            with open(curl_file, 'w') as f:
                f.write(curl_content)
        
        # Extract from curl command
        success = extract_from_file(curl_file=curl_file)
        if success:
            print("✓ Configuration set up successfully using curl command.")
            return True
        else:
            print("Failed to extract configuration from curl command.")
            print("Falling back to manual setup.")
    
    # Manual setup
    print("\nManual setup:")
    headers = {
        'User-Agent': input("User-Agent (press Enter for default): ") or 
                     'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
    }
    
    cookies = {}
    print("\nEnter cookies (required for authentication):")
    print("Leave blank and press Enter when done.")
    while True:
        cookie_name = input("Cookie name (e.g., jwt): ")
        if not cookie_name:
            break
        cookie_value = input(f"Value for {cookie_name}: ")
        cookies[cookie_name] = cookie_value
    
    base_url = input("\nBase URL (default: https://hackatopia.devpost.com): ") or 'https://hackatopia.devpost.com'
    
    # Write config file
    try:
        with open('config.py', 'w') as f:
            f.write('"""\nConfiguration for AI-Judge\n"""\n\n')
            f.write('# Headers for HTTP requests\n')
            f.write('HEADERS = {\n')
            for key, value in headers.items():
                f.write(f"    '{key}': '{value}',\n")
            f.write('}\n\n')
            
            f.write('# Cookies for authentication\n')
            f.write('COOKIES = {\n')
            for key, value in cookies.items():
                f.write(f"    '{key}': '{value}',\n")
            f.write('}\n\n')
            
            f.write('# Base URL for the Devpost hackathon\n')
            f.write(f"BASE_URL = '{base_url}'\n\n")
            
            f.write('# OpenAI API configuration\n')
            openai_key = input("\nOpenAI API key (for AI judging, leave blank if not using): ")
            f.write(f"OPENAI_API_KEY = '{openai_key}'\n")
            f.write("OPENAI_MODEL = 'gpt-3.5-turbo'  # Model to use for AI judging\n")
        
        print("✓ Configuration set up successfully with manual entry.")
        return True
    except Exception as e:
        print(f"Error creating config file: {e}")
        return False

def check_uri_file():
    """Check if uri.txt exists and has valid URIs"""
    print("\nChecking for URI file...")
    
    if not os.path.exists('uri.txt'):
        create = input("uri.txt not found. Create a sample? (y/n): ")
        if create.lower() == 'y':
            with open('uri.txt', 'w') as f:
                f.write("/submissions/123456-example-project/judging\n")
            print("✓ Created sample uri.txt file.")
            print("  Note: You should replace the sample URI with real project URIs.")
        else:
            print("You'll need to create uri.txt manually before using batch processing.")
        return True
    
    # Count URIs in the file
    with open('uri.txt', 'r') as f:
        uris = [line.strip() for line in f if line.strip()]
        valid_count = sum(1 for uri in uris if re.match(r"^/submissions/\w+-[^/]+/judging", uri))
        
    print(f"✓ Found uri.txt with {valid_count} valid URIs.")
    return True

def main():
    """Main setup function"""
    print("==================================")
    print("   AI Judge System Setup")
    print("==================================\n")
    
    # Steps for setup
    steps = [
        ("Checking Python version", check_python_version),
        ("Installing dependencies", install_dependencies),
        ("Setting up configuration", setup_config),
        ("Checking URI file", check_uri_file)
    ]
    
    results = []
    for step_name, step_func in steps:
        print(f"\n{step_name}...")
        success = step_func()
        results.append((step_name, success))
    
    # Print summary
    print("\n==================================")
    print("   Setup Summary")
    print("==================================")
    for step_name, success in results:
        status = "✓ Success" if success else "✗ Failed"
        print(f"{step_name}: {status}")
    
    if all(success for _, success in results):
        print("\nSetup completed successfully! You can now use the AI Judge system.")
        print("\nTry running some commands:")
        print("  python cli.py fetch /submissions/123456-example-project/judging")
        print("  python cli.py test random")
        print("  python cli.py test ai")
    else:
        print("\nSetup completed with some issues. Please fix the failed steps before using the system.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 