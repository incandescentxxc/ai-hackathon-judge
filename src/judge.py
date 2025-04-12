#!/usr/bin/env python3
"""
Core judging functionality for submitting ratings to Devpost hackathon projects.
"""

import random
import requests
from .settings import load_config
from .project import fetch_and_parse_project
from .ai_judge import generate_ai_ratings

def submit_form(uri, ratings=None, use_ai=False, test_mode=False):
    """
    Submit a form with ratings for a project.
    
    Args:
        uri (str): The URI of the project
        ratings (int or dict): Rating value(s) to submit. 
                              If int, all criteria get the same rating.
                              If dict, keys are grade IDs and values are ratings.
                              If None, randomly generate ratings between 2-4.
        use_ai (bool): If True, use AI to generate ratings based on project content.
        test_mode (bool): If True, print additional debug info including OpenAI prompt
        
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
    
    # If using AI rating, get ratings from the AI
    if use_ai:
        print(f"Using AI to generate ratings for {project_data.get('title', uri)}...")
        ai_ratings = generate_ai_ratings(project_data, test_mode=test_mode)
        
        if ai_ratings:
            # Convert the AI ratings to the required format
            for grade_id, rating in ai_ratings.items():
                grade_data[f'grades[{grade_id}]'] = str(rating)
        else:
            print("AI rating failed. Falling back to random ratings.")
            # Fall back to random ratings if AI rating fails
            for grade_id in project_data['grade_fields'].keys():
                random_rating = random.randint(2, 4)
                grade_data[f'grades[{grade_id}]'] = str(random_rating)
            
            # Log the randomly generated ratings
            random_ratings_log = {grade_id: grade_data[f'grades[{grade_id}]'] for grade_id in project_data['grade_fields']}
            print(f"Generated random ratings: {random_ratings_log}")
    elif isinstance(ratings, int):
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
    headers, cookies, base_url, _, _ = load_config()
    submission_url = f"{base_url}/submissions/{uri.split('/')[2]}/submission_judgings/{project_data['submission_judging_id']}"
    
    # Add content-type header for form submission
    headers = headers.copy()  # Create a copy to avoid modifying the original
    headers['content-type'] = 'application/x-www-form-urlencoded'
    headers['origin'] = base_url
    headers['referer'] = f"{base_url}{uri}"
    
    try:
        # For debugging
        print(f"Submitting form to: {submission_url}")
        print(f"Form data: {form_data}")
        
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
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text[:200]}...")  # Print first 200 chars of response
        
        return result
        
    except Exception as e:
        print(f"Error submitting form for {uri}: {e}")
        return {
            'success': False,
            'error': str(e),
            'project_title': project_data.get('title', ''),
            'submission_url': submission_url
        } 