#!/usr/bin/env python3
"""
Test script for parsing HTML files to verify the HTML parser's functionality.

This script serves several important functions:
1. Testing the HTML parser against sample HTML files
2. Verifying proper extraction of project title and description
3. Checking for correct identification of form fields and authentication tokens
4. Validating the extraction of project sections
5. Detecting potential content duplication issues between sections

Usage:
    python test_html_parser.py [html_file]

    If no html_file is specified, it will use example.html by default.

Output:
    The script prints a formatted summary of the extracted data and saves
    the complete results to parsed_example.json for further inspection.
"""

import json
import sys
import os
from src.parser import parse_project_page
from bs4 import BeautifulSoup
import requests

def test_html_parser(html_file='example.html'):
    """
    Parse the example HTML file and print the extracted data.
    
    Args:
        html_file (str): Path to the HTML file to parse
    """
    print(f"🔍 Testing HTML parser with file: {html_file}")
    
    try:
        # Read the HTML file
        with open(html_file, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Debug: Check if h1 tag is actually present
        soup = BeautifulSoup(html_content, 'html.parser')
        h1_tags = soup.find_all('h1')
        print(f"\n🔍 DEBUG: Found {len(h1_tags)} h1 tags in the document")
        for i, h1 in enumerate(h1_tags):
            print(f"  - h1 #{i+1}: '{h1.text.strip()}'")
        
        # Parse the HTML using our parser
        result = parse_project_page(html_content)
        
        # Print the results in a readable format
        print("\n✅ Parsed data:")
        
        # Print important fields
        important_fields = ['title', 'description', 'authenticity_token', 'submission_judging_id']
        for field in important_fields:
            if field in result:
                if field == 'authenticity_token':
                    # Truncate long tokens for readability
                    value = result[field][:20] + "..." if len(result[field]) > 20 else result[field]
                else:
                    value = result[field]
                print(f"  - {field}: {value}")
        
        # Print grade fields
        if 'grade_fields' in result:
            grade_count = len(result['grade_fields'])
            print(f"  - grade_fields: {grade_count} fields found")
            for i, (grade_id, value) in enumerate(result['grade_fields'].items()):
                if i < 5:  # Show only first 5 for brevity
                    print(f"    * {grade_id}: {value}")
                else:
                    print(f"    * ... and {grade_count - 5} more")
                    break
        
        # Print project sections with better formatting
        print("\n📑 Project Sections:")
        for key, value in result.items():
            if key not in important_fields and key != 'grade_fields':
                # Format section content for readability
                content = value.strip()
                print(f"\n  🔹 {key}:")
                if len(content) > 200:
                    # Show first 200 chars with ellipsis for longer sections
                    print(f"     {content[:200]}...")
                    print(f"     [Total length: {len(content)} chars]")
                else:
                    print(f"     {content}")
        
        # Check if we have unique content in each section
        sections_content = [result[k] for k in result if k not in important_fields and k != 'grade_fields']
        unique_content = set(sections_content)
        if len(unique_content) < len(sections_content):
            print("\n⚠️  Warning: Some sections have duplicate content!")
        else:
            print("\n✅ All sections have unique content!")
        
        # Save the full result to a JSON file for reference
        with open('parsed_example.json', 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nComplete parsed data saved to parsed_example.json")
        
        return result
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_url_parser(url):
    """
    Test the HTML parser on a URL directly.
    
    Args:
        url (str): The URL to fetch and parse
        
    Returns:
        dict: The parsed data or None if an error occurred
    """
    print(f"🌐 Testing HTML parser on URL: {url}")
    
    try:
        # Fetch the HTML content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise exception for bad status codes
        
        html_content = response.text
        print(f"✅ Successfully fetched HTML ({len(html_content)} bytes)")
        
        # Parse the HTML using our parser
        return parse_project_page(html_content)
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    import sys
    import json
    
    test_file = "example.html"
    print(f"🔍 Testing HTML parser with file: {test_file}")
    
    with open(test_file, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Parse the HTML using our parser
    result = parse_project_page(html_content)
    
    # Print formatted results
    print("\n✅ Parsed data:")
    if 'title' in result:
        print(f"  - title: {result['title']}")
    if 'description' in result:
        print(f"  - description: {result['description']}")
    if 'authenticity_token' in result:
        token = result['authenticity_token']
        print(f"  - authenticity_token: {token[:20]}...")
    if 'submission_judging_id' in result:
        print(f"  - submission_judging_id: {result['submission_judging_id']}")
    if 'grade_fields' in result:
        print(f"  - grade_fields: {len(result['grade_fields'])} fields found")
        for field_id, value in result['grade_fields'].items():
            print(f"    * {field_id}: {value}")
    
    # Extract just the project sections (not metadata)
    sections_content = [result[k] for k in result if k not in ['title', 'description', 'authenticity_token', 'submission_judging_id', 'grade_fields']]
    unique_content = set(sections_content)
    if len(unique_content) < len(sections_content):
        print("\n⚠️  Warning: Some sections have duplicate content!")
    else:
        print("\n✅ All sections have unique content!")
    
    # Save the full result to a JSON file for reference
    with open('parsed_example.json', 'w') as f:
        json.dump(result, f, indent=2)
    print(f"\nComplete parsed data saved to parsed_example.json") 