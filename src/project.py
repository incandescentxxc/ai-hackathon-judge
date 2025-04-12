#!/usr/bin/env python3
"""
Project-related functionality for fetching and processing projects.
"""

import requests
from .settings import get_auth_headers_and_cookies, load_config
from .parser import parse_project_page

def fetch_and_parse_project(uri):
    """
    Fetch the project page from the URL and parse it.
    
    Args:
        uri (str): The URI of the project
        
    Returns:
        dict: A dictionary containing the extracted sections
    """
    headers, cookies, base_url, _, _ = load_config()
    url = f"{base_url}{uri}"
    
    try:
        # Make the request with the authentication headers and cookies
        response = requests.get(url, headers=headers, cookies=cookies)
        response.raise_for_status()
        return parse_project_page(response.content)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None 