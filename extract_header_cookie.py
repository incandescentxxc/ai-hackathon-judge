#!/usr/bin/env python3
"""
Script to extract headers and cookies from a curl command.

Instructions:
1. Log in to your Devpost account in a browser
2. Open developer tools (F12 or right-click > Inspect)
3. Go to the Network tab and refresh the page
4. Right-click on any document request and select "Copy as cURL"
5. Paste the curl command into a file named curl.txt
6. Run this script: python extract_header_cookie.py
7. The script will create/update config.py with the extracted headers and cookies
"""

import re
import os
import sys
import json
import shlex

def extract_from_curl(curl_command):
    """Extract headers and cookies from a curl command."""
    # Split the curl command into tokens
    try:
        tokens = shlex.split(curl_command)
    except ValueError as e:
        print(f"Error parsing curl command: {e}")
        return None, None, None
    
    headers = {}
    cookies = {}
    url = None
    
    i = 1  # Skip 'curl'
    while i < len(tokens):
        token = tokens[i]
        
        # Extract URL (usually the first non-option argument)
        if not token.startswith('-') and not url:
            url = token.strip("'\"")
        
        # Extract headers
        elif token in ['-H', '--header'] and i + 1 < len(tokens):
            header = tokens[i + 1].strip("'\"")
            if ': ' in header:
                key, value = header.split(': ', 1)
                if key.lower() == 'cookie':
                    # Parse cookie string
                    cookie_parts = value.split('; ')
                    for part in cookie_parts:
                        if '=' in part:
                            cookie_key, cookie_value = part.split('=', 1)
                            cookies[cookie_key] = cookie_value
                else:
                    headers[key] = value
            i += 1  # Skip the next token as it's the header value
        
        # Extract cookies from -b or --cookie flag
        elif token in ['-b', '--cookie'] and i + 1 < len(tokens):
            cookie_string = tokens[i + 1].strip("'\"")
            # Parse cookie string
            cookie_parts = cookie_string.split('; ')
            for part in cookie_parts:
                if '=' in part:
                    cookie_key, cookie_value = part.split('=', 1)
                    cookies[cookie_key] = cookie_value
            i += 1  # Skip the next token as it's the cookie value
        
        # Skip other options
        elif token.startswith('-'):
            # If the option takes an argument, skip it too
            if token in ['-d', '--data', '--data-binary', '--data-raw', '-u', '--user']:
                i += 1
        
        i += 1
    
    return headers, cookies, url

def generate_config(headers, cookies, url):
    """Generate a config.py file with the extracted headers and cookies."""
    if not headers and not cookies:
        print("Error: No headers or cookies extracted.")
        return False
    
    base_url = None
    if url:
        # Extract base URL (scheme + host)
        match = re.match(r'(https?://[^/]+)', url)
        if match:
            base_url = match.group(1)
    
    # Create the config file content
    lines = ['"""', 'Configuration for AI-Judge', '"""', '']
    
    # Add headers
    lines.append('# Headers for HTTP requests')
    lines.append('HEADERS = {')
    for key, value in headers.items():
        lines.append(f"    '{key}': '{value}',")
    lines.append('}')
    lines.append('')
    
    # Add cookies
    lines.append('# Cookies for authentication')
    lines.append('COOKIES = {')
    for key, value in cookies.items():
        lines.append(f"    '{key}': '{value}',")
    lines.append('}')
    lines.append('')
    
    # Add base URL if available
    if base_url:
        lines.append('# Base URL for the Devpost hackathon')
        lines.append(f"BASE_URL = '{base_url}'")
    
    # Write to config.py
    with open('config.py', 'w') as f:
        f.write('\n'.join(lines))
    
    return True

def main():
    print("Header and Cookie Extractor for AI-Judge")
    print("=======================================")
    
    # Check if curl.txt exists
    if not os.path.exists('curl.txt'):
        print("Error: curl.txt file not found.")
        print("Please create a curl.txt file with your curl command.")
        print("Instructions:")
        print("1. Log in to your Devpost account")
        print("2. Open developer tools (F12)")
        print("3. Right-click on a request and select 'Copy as cURL'")
        print("4. Paste the command into a file named curl.txt")
        return
    
    # Read the curl command from curl.txt
    with open('curl.txt', 'r') as f:
        curl_command = f.read().strip()
    
    if not curl_command:
        print("Error: curl.txt is empty.")
        return
    
    # Extract headers and cookies
    headers, cookies, url = extract_from_curl(curl_command)
    
    if headers or cookies:
        # Generate config.py
        if generate_config(headers, cookies, url):
            print("\nSuccessfully created config.py with:")
            print(f"- {len(headers)} headers")
            print(f"- {len(cookies)} cookies")
            
            # Check for important cookies
            important_cookies = ['jwt', 'remember_user_token', '_devpost']
            missing = [cookie for cookie in important_cookies if cookie not in cookies]
            
            if missing:
                print("\nWarning: Some important cookies are missing:")
                for cookie in missing:
                    print(f" - {cookie}")
                print("Authentication may not work correctly without these cookies.")
            else:
                print("\nAll important cookies are present!")
            
            print("\nYou're all set! You can now use the judge.py and batch_submit.py scripts.")
    else:
        print("Error: Failed to extract headers or cookies from the curl command.")
        print("Please make sure the curl command is valid and contains cookies.")
        print("Look for either a '-H 'cookie:...' or a '-b '...' parameter in the curl command.")

if __name__ == "__main__":
    main() 