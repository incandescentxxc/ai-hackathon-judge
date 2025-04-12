#!/usr/bin/env python3
"""
Module for extracting headers and cookies from curl commands.
Used to simplify authentication setup.
"""

import re
import os
import shlex
import sys
import json

def extract_from_curl(curl_command):
    """
    Extract headers and cookies from a curl command.
    
    Args:
        curl_command (str): The curl command to parse
        
    Returns:
        tuple: (headers, cookies, url) extracted from the command
    """
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

def generate_config(headers, cookies, url, output_file='config.py'):
    """
    Generate a config.py file with the extracted headers and cookies.
    
    Args:
        headers (dict): HTTP headers
        cookies (dict): Cookies for authentication
        url (str): URL from which to extract the base URL
        output_file (str): Path to the output config file
        
    Returns:
        bool: True if successful, False otherwise
    """
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
        lines.append('')
    
    # Add placeholders for OpenAI configuration
    lines.append('# OpenAI API configuration (add your key here)')
    lines.append("OPENAI_API_KEY = ''  # Your OpenAI API key")
    lines.append("OPENAI_MODEL = 'gpt-3.5-turbo'  # Model to use for AI judging")
    
    # Write to config file
    with open(output_file, 'w') as f:
        f.write('\n'.join(lines))
    
    return True

def extract_from_file(curl_file='curl.txt', config_file='config.py'):
    """
    Extract headers and cookies from a file containing a curl command and generate a config file.
    
    Args:
        curl_file (str): Path to the file containing the curl command
        config_file (str): Path to the output config file
        
    Returns:
        bool: True if successful, False otherwise
    """
    # Check if curl file exists
    if not os.path.exists(curl_file):
        print(f"Error: {curl_file} file not found.")
        print(f"Please create a {curl_file} file with your curl command.")
        print("Instructions:")
        print("1. Log in to your Devpost account")
        print("2. Open developer tools (F12)")
        print("3. Right-click on a request and select 'Copy as cURL'")
        print(f"4. Paste the command into a file named {curl_file}")
        return False
    
    # Read the curl command from the file
    with open(curl_file, 'r') as f:
        curl_command = f.read().strip()
    
    if not curl_command:
        print(f"Error: {curl_file} is empty.")
        return False
    
    # Extract headers and cookies
    headers, cookies, url = extract_from_curl(curl_command)
    
    if not headers and not cookies:
        print("Error: Failed to extract headers or cookies from the curl command.")
        print("Please make sure the curl command is valid and contains cookies.")
        print("Look for either a '-H 'cookie:...' or a '-b '...' parameter in the curl command.")
        return False
    
    # Generate config file
    success = generate_config(headers, cookies, url, config_file)
    
    if success:
        print(f"\nSuccessfully created {config_file} with:")
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
        
        return True
    
    return False 