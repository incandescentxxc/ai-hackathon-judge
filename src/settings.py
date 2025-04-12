#!/usr/bin/env python3
"""
Settings utilities for the AI Judge system.
Handles loading of authentication credentials and other settings.
"""

import os
import importlib.util

def load_config():
    """
    Load configuration from config.py if available, otherwise use default values.
    
    Returns:
        tuple: (headers, cookies, base_url, openai_api_key, openai_model)
    """
    # Default values
    default_headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'max-age=0',
        'sec-ch-ua': '"Google Chrome";v="135", "Not-A.Brand";v="8", "Chromium";v="135"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36',
    }
    
    default_cookies = {}  # Empty by default, requiring user to set up their own
    default_base_url = 'https://hackatopia.devpost.com'
    default_openai_api_key = os.environ.get('OPENAI_API_KEY', '')
    default_openai_model = 'gpt-3.5-turbo'
    
    # Try to import the user config from root directory
    try:
        # We're deliberately looking for config.py in the root, not in the src directory
        spec = importlib.util.spec_from_file_location("config", "config.py")
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        
        # Get values from config, use defaults if not present
        headers = getattr(config, 'HEADERS', default_headers)
        cookies = getattr(config, 'COOKIES', default_cookies)
        base_url = getattr(config, 'BASE_URL', default_base_url)
        openai_api_key = getattr(config, 'OPENAI_API_KEY', default_openai_api_key)
        openai_model = getattr(config, 'OPENAI_MODEL', default_openai_model)
        
        return headers, cookies, base_url, openai_api_key, openai_model
    except (ImportError, FileNotFoundError):
        print("Warning: config.py not found. Using default headers with empty cookies.")
        print("Please create a config.py file by copying config_template.py and setting your own authentication.")
        return default_headers, default_cookies, default_base_url, default_openai_api_key, default_openai_model

def get_auth_headers_and_cookies():
    """
    Get the authentication headers and cookies for requests.
    
    Returns:
        tuple: (headers, cookies) for use in requests
    """
    headers, cookies, _, _, _ = load_config()
    return headers, cookies 