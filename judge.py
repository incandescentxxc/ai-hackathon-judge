#!/usr/bin/env python3
import os
import requests
from bs4 import BeautifulSoup
import re
import json
import urllib.parse
import random
import importlib.util
import sys

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

def load_config():
    """
    Load configuration from config.py if available, otherwise use default values.
    
    Returns:
        tuple: (headers, cookies, base_url)
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
    
    # Try to import config
    try:
        spec = importlib.util.spec_from_file_location("config", "config.py")
        config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(config)
        
        # Get values from config, use defaults if not present
        headers = getattr(config, 'HEADERS', default_headers)
        cookies = getattr(config, 'COOKIES', default_cookies)
        base_url = getattr(config, 'BASE_URL', default_base_url)
        
        return headers, cookies, base_url
    except (ImportError, FileNotFoundError):
        print("Warning: config.py not found. Using default headers with empty cookies.")
        print("Please create a config.py file by copying config_template.py and setting your own authentication.")
        return default_headers, default_cookies, default_base_url

def get_auth_headers_and_cookies():
    """
    Get the authentication headers and cookies for requests.
    
    Returns:
        tuple: (headers, cookies) for use in requests
    """
    headers, cookies, _ = load_config()
    return headers, cookies

def fetch_and_parse_project(uri):
    """
    Fetch the project page from the URL and parse it.
    
    Args:
        uri (str): The URI of the project
        
    Returns:
        dict: A dictionary containing the extracted sections
    """
    headers, cookies, base_url = load_config()
    url = f"{base_url}{uri}"
    
    try:
        # Make the request with the authentication headers and cookies
        response = requests.get(url, headers=headers, cookies=cookies)
        response.raise_for_status()
        return parse_project_page(response.content)
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return None

def submit_form(uri, ratings=None):
    """
    Submit a form with ratings for a project.
    
    Args:
        uri (str): The URI of the project
        ratings (int or dict): Rating value(s) to submit. 
                              If int, all criteria get the same rating.
                              If dict, keys are grade IDs and values are ratings.
                              If None, randomly generate ratings between 2-4.
        
    Returns:
        dict: Response information including status code, content
    """
    # First, fetch the page to get the authenticity_token and form fields
    project_data = fetch_and_parse_project(uri)
    
    if not project_data:
        return {'success': False, 'error': 'Failed to fetch project data'}
    
    if 'authenticity_token' not in project_data:
        return {'success': False, 'error': 'Authenticity token not found'}
    
    if 'grade_fields' not in project_data:
        return {'success': False, 'error': 'Grade fields not found'}
    
    if 'submission_judging_id' not in project_data:
        return {'success': False, 'error': 'Submission judging ID not found'}
    
    # Prepare the ratings data
    grade_data = {}
    if isinstance(ratings, int):
        # Apply the same rating to all criteria
        for grade_id in project_data['grade_fields'].keys():
            grade_data[f'grades[{grade_id}]'] = str(ratings)
    elif isinstance(ratings, dict):
        # Apply specific ratings to each criterion
        for grade_id, rating in ratings.items():
            grade_data[f'grades[{grade_id}]'] = str(rating)
    else:
        # Generate random ratings between 2 and 4 for each criterion
        for grade_id in project_data['grade_fields'].keys():
            random_rating = random.randint(2, 4)
            grade_data[f'grades[{grade_id}]'] = str(random_rating)
        
        # Log the randomly generated ratings
        random_ratings_log = {grade_id: grade_data[f'grades[{grade_id}]'] for grade_id in project_data['grade_fields']}
        print(f"Generated random ratings: {random_ratings_log}")
    
    # Prepare the form data
    form_data = {
        'utf8': '✓',
        '_method': 'patch',
        'authenticity_token': project_data['authenticity_token'],
        'submission_judging[recused]': '0',
        'commit': 'Save and continue'
    }
    
    # Add the grade data
    form_data.update(grade_data)
    
    # Get the submission URL and load config
    headers, cookies, base_url = load_config()
    submission_url = f"{base_url}/submissions/{uri.split('/')[2]}/submission_judgings/{project_data['submission_judging_id']}"
    
    # Add content-type header for form submission
    headers['content-type'] = 'application/x-www-form-urlencoded'
    headers['origin'] = base_url
    headers['referer'] = f"{base_url}{uri}"
    
    try:
        # Make the POST request
        response = requests.post(
            submission_url,
            headers=headers,
            cookies=cookies,
            data=form_data
        )
        
        # Check response
        result = {
            'success': response.status_code == 200 or response.status_code == 302,
            'status_code': response.status_code,
            'project_title': project_data.get('title', ''),
            'submission_url': submission_url,
            'response_url': response.url,
        }
        
        if 'success' in result and result['success']:
            print(f"Successfully submitted ratings for {project_data.get('title', uri)}")
        else:
            print(f"Failed to submit ratings for {project_data.get('title', uri)}")
        
        return result
        
    except Exception as e:
        print(f"Error submitting form for {uri}: {e}")
        return {
            'success': False,
            'error': str(e),
            'project_title': project_data.get('title', ''),
            'submission_url': submission_url
        }

def main():
    # Read URIs from the uri.txt file
    with open('uri.txt', 'r') as file:
        uris = [line.strip().strip(',') for line in file.readlines()]
    
    results = {}
    for uri in uris:
        print(f"Processing {uri}...")
        project_data = fetch_and_parse_project(uri)
        if project_data:
            results[uri] = project_data
    
    # Save results to a JSON file
    with open('project_data.json', 'w') as outfile:
        json.dump(results, outfile, indent=2)
    
    print(f"Processed {len(results)} projects. Results saved to project_data.json")

if __name__ == "__main__":
    main()
