#!/usr/bin/env python3
"""
Parser utilities for extracting data from Devpost project pages.
"""

from bs4 import BeautifulSoup
import re

def clean_text(text):
    """
    Clean up text by removing extra whitespace and newlines.
    
    Args:
        text (str): The text to clean
        
    Returns:
        str: The cleaned text
    """
    if not text:
        return ""
    
    # Replace all whitespace characters (including newlines, tabs, etc.) with a single space
    cleaned = re.sub(r'\s+', ' ', text)
    # Trim leading and trailing whitespace
    cleaned = cleaned.strip()
    return cleaned

def parse_project_page(html_content):
    """
    Parse the HTML content of a project page and extract specific sections.
    
    This function extracts various pieces of information from a Devpost project page:
    - Title: Extracted from non-empty h1 tags or meta tags
    - Description: Extracted from italic tags in subheaders or meta tags
    - Authentication token: For form submission
    - Submission judging ID: Used for form actions
    - Grade fields: Form input fields for grading
    - Project sections: Including Inspiration, What it does, How we built it, etc.
    
    The parser implements multiple fallback strategies to handle different HTML structures
    and ensure the best possible data extraction, even from incomplete project pages.
    
    Args:
        html_content (str): The HTML content of the project page
        
    Returns:
        dict: A dictionary containing the extracted data with keys including:
            - title: Project title
            - description: Project description/tagline
            - authenticity_token: Form authentication token
            - submission_judging_id: ID for form submission
            - grade_fields: Dictionary of grading field IDs and values
            - [Section names]: Content from various project sections
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    result = {}
    
    # Extract the authenticity_token from the form
    authenticity_token_input = soup.find('input', {'name': 'authenticity_token'})
    if authenticity_token_input and 'value' in authenticity_token_input.attrs:
        result['authenticity_token'] = authenticity_token_input['value']
    
    # Extract all grade input fields to get their IDs
    grade_inputs = soup.find_all('input', {'name': re.compile(r'grades\[\d+\]')})
    if grade_inputs:
        grades = {}
        for input_field in grade_inputs:
            # Extract the ID from the name (e.g., "grades[12345]" -> "12345")
            name = input_field.get('name', '')
            match = re.search(r'grades\[(\d+)\]', name)
            if match:
                grade_id = match.group(1)
                grades[grade_id] = input_field.get('value', '')
        
        result['grade_fields'] = grades
    
    # Extract the submission_judging ID from the form action
    form = soup.find('form', {'action': re.compile(r'/submissions/\d+-[^/]+/submission_judgings/\d+')})
    if form and 'action' in form.attrs:
        match = re.search(r'/submissions/\d+-[^/]+/submission_judgings/(\d+)', form['action'])
        if match:
            result['submission_judging_id'] = match.group(1)
    
    # Extract the title
    # Find all h1 tags and pick the non-empty one for the project title
    h1_tags = soup.find_all('h1')
    title_h1 = None
    
    # Find the first non-empty h1 tag
    for h1 in h1_tags:
        if h1.text.strip():
            title_h1 = h1
            break
    
    if title_h1:
        result['title'] = clean_text(title_h1.text)
    else:
        # Fallback to meta tags
        meta_title = soup.find('meta', {'property': 'og:title'}) or soup.find('meta', {'name': 'twitter:title'})
        if meta_title and 'content' in meta_title.attrs:
            result['title'] = clean_text(meta_title['content'])
    
    # Extract the description
    # Find the description in <i> tag within <h3 class="subheader"> following h1
    description_element = None
    if title_h1:
        # Look for h3.subheader after h1
        subheader = title_h1.find_next('h3', class_='subheader')
        if subheader:
            # Find italic tag within the subheader
            italic = subheader.find('i')
            if italic:
                description_element = italic
    
    if description_element:
        result['description'] = clean_text(description_element.text)
    else:
        # Fallback to meta tags
        meta_desc = soup.find('meta', {'property': 'og:description'}) or soup.find('meta', {'name': 'description'}) or soup.find('meta', {'name': 'twitter:description'})
        if meta_desc and 'content' in meta_desc.attrs:
            result['description'] = clean_text(meta_desc['content'])
    
    # Define the sections to look for
    sections = [
        "Inspiration",
        "What it does",
        "How we built it",
        "Challenges we ran into",
        "Accomplishments that we're proud of",
        "What we learned",
        "What's next for"
    ]
    
    # First check if there are "Date entered" placeholders in the document
    # This indicates the project has sections that haven't been filled out yet
    date_placeholders = {}
    for date_elem in soup.find_all(string=lambda s: s and "Date entered:" in s):
        # Find the closest header element
        header = None
        for parent in date_elem.parents:
            prev_sibling = parent.find_previous_sibling(['h2', 'h3', 'h4'])
            if prev_sibling:
                header = prev_sibling
                break
        
        if header:
            header_text = clean_text(header.text)
            # Map this to the correct section
            for section in sections:
                if section in header_text:
                    date_placeholders[section if section != "What's next for" else header_text] = clean_text(date_elem)
    
    # Look for the app-details section which contains the structured content
    app_details = soup.select_one('.app-details') or soup.select_one('.content-blocks')
    
    if app_details:
        # Extract each section from the app-details container
        for section in sections:
            section_header = None
            
            # Find headers that match this section
            for header in app_details.select('h2, h3, h4'):
                header_text = clean_text(header.text)
                if section == "What's next for":
                    if header_text.startswith(section):
                        section_header = header
                        section_name = header_text
                        break
                elif header_text == section:
                    section_header = header
                    section_name = section
                    break
            
            if section_header:
                # For each section, find the content following the header
                content = ""
                
                # Try to find the section content in a structured way
                section_div = None
                for parent in section_header.parents:
                    if parent.name == 'div' and 'block' in parent.get('class', []):
                        section_div = parent
                        break
                
                if section_div:
                    # Extract content from this section div
                    content_elements = section_div.select('p, .large, .details')
                    if content_elements:
                        # Filter out the header itself
                        content_elements = [elem for elem in content_elements 
                                          if elem != section_header and section not in elem.text]
                        content = " ".join(elem.text.strip() for elem in content_elements if elem.text.strip())
                
                # If no structured content found, try getting siblings
                if not content:
                    # Get all siblings until the next header or end of parent
                    current = section_header.next_sibling
                    while current and current.name not in ['h1', 'h2', 'h3', 'h4']:
                        if current.name == 'p' or (current.name == 'div' and 'details' in current.get('class', [])):
                            content += " " + current.text.strip()
                        current = current.next_sibling
                
                # If still no content, check if we have a date placeholder
                if not content and (section_name in date_placeholders):
                    content = date_placeholders[section_name]
                
                # Only add non-empty sections
                if content:
                    result[section_name] = clean_text(content)
                elif section_name in date_placeholders:
                    result[section_name] = date_placeholders[section_name]
    
    # If we couldn't find structured sections, try to use the entire document body as a fallback
    if not any(k in result for k in sections):
        # Last resort: try to extract content from the document body
        main_content = soup.select_one('.app-details') or soup.select_one('main') or soup.select_one('body')
        
        if main_content:
            # Try to extract each section by finding headers and their following content
            for section in sections:
                # Find headers that match or start with this section
                headers = []
                if section == "What's next for":
                    headers = main_content.find_all(['h2', 'h3', 'h4'], 
                                                 string=lambda s: s and s.strip().startswith(section))
                else:
                    headers = main_content.find_all(['h2', 'h3', 'h4'], 
                                                 string=lambda s: s and s.strip() == section)
                
                for header in headers:
                    section_name = clean_text(header.text)
                    
                    # Get the content following this header
                    content = ""
                    current = header.next_sibling
                    
                    # Look at the next 5 elements maximum
                    for _ in range(5):
                        if not current:
                            break
                        
                        if current.name in ['h2', 'h3', 'h4']:
                            # Stop at the next header
                            break
                        
                        if current.name == 'p' or (hasattr(current, 'text') and current.text.strip()):
                            content += " " + current.text.strip()
                        
                        current = current.next_sibling
                    
                    # Only add non-empty sections
                    if content:
                        result[section_name] = clean_text(content)
                    elif section_name in date_placeholders:
                        result[section_name] = date_placeholders[section_name]
    
    # Clean up the results - ensure all required fields are present even if empty
    # Add empty title and description if not found
    if 'title' not in result:
        result['title'] = ""
    if 'description' not in result:
        result['description'] = ""
    
    return result 