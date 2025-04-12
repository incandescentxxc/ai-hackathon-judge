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
    
    Args:
        html_content (str): The HTML content of the project page
        
    Returns:
        dict: A dictionary containing the extracted sections
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
    
    # Extract the title from the h1 tag (find all h1 tags and use the one with content)
    h1_tags = soup.find_all('h1')
    title = ""
    for h1 in h1_tags:
        if h1.text.strip():
            title = clean_text(h1.text)
            break
    
    if title:
        result['title'] = title
    
    # Find the h1 tag with the title (the one containing non-empty text)
    title_tag = None
    for h1 in h1_tags:
        if h1.text.strip():
            title_tag = h1
            break
    
    # Extract the description from the h3 tag following the title h1
    if title_tag and title_tag.find_next('h3'):
        result['description'] = clean_text(title_tag.find_next('h3').text)
    
    # Define the sections to extract
    sections = [
        "Inspiration",
        "What it does",
        "How we built it",
        "Challenges we ran into",
        "Accomplishments that we're proud of",
        "What we learned",
        "What's next for"
    ]
    
    # Extract each section by finding the h2 tag and the following p tag
    for section in sections:
        # For "What's next for", we need to handle it differently since it includes the project name
        if section == "What's next for":
            # Find all h2 tags that start with "What's next for"
            h2_tags = soup.find_all('h2', string=lambda s: s and s.startswith(section))
            if h2_tags:
                h2_tag = h2_tags[0]
                section_name = clean_text(h2_tag.text)
                # Extract content from the following p tag
                p_tag = h2_tag.find_next('p')
                if p_tag:
                    result[section_name] = clean_text(p_tag.text)
        else:
            # For other sections, find the exact h2 tag
            h2_tag = soup.find('h2', string=section)
            if h2_tag:
                # Extract content from the following p tag
                p_tag = h2_tag.find_next('p')
                if p_tag:
                    result[section] = clean_text(p_tag.text)
    
    return result 