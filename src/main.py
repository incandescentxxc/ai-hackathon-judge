#!/usr/bin/env python3
"""
Main module for the AI Judge system.
Provides core functionality used by the CLI and other scripts.
"""

import json
import os
from .project import fetch_and_parse_project
from .judge import submit_form

def parse_projects(uri_file='uri.txt', output_file='project_data.json'):
    """
    Read URIs from a file, parse project pages, and save the data to a JSON file.
    
    Args:
        uri_file (str): Path to the file containing URIs
        output_file (str): Path to save the output JSON data
        
    Returns:
        dict: Results of all parsed projects
    """
    # Check if the URI file exists
    if not os.path.exists(uri_file):
        print(f"Error: URI file '{uri_file}' not found.")
        return {}
    
    # Read URIs from the file
    with open(uri_file, 'r') as file:
        uris = [line.strip().strip(',') for line in file.readlines()]
    
    results = {}
    for uri in uris:
        print(f"Processing {uri}...")
        project_data = fetch_and_parse_project(uri)
        if project_data:
            results[uri] = project_data
    
    # Save results to a JSON file
    with open(output_file, 'w') as outfile:
        json.dump(results, outfile, indent=2)
    
    print(f"Processed {len(results)} projects. Results saved to {output_file}")
    return results

def process_uri(uri, rating=None, use_ai=False, fetch_only=False, test_mode=False):
    """
    Process a single URI - either fetch project details or submit a form.
    
    Args:
        uri (str): URI of the project
        rating (int or dict, optional): Rating to apply
        use_ai (bool): Whether to use AI for rating
        fetch_only (bool): If True, only fetch project data without submitting
        test_mode (bool): If True, print additional debug info including OpenAI prompt
        
    Returns:
        dict: Result of the operation
    """
    # If only fetching project data
    if fetch_only:
        return fetch_and_parse_project(uri)
    
    # Submit form with ratings
    return submit_form(uri, ratings=rating, use_ai=use_ai, test_mode=test_mode)

if __name__ == "__main__":
    # When run directly, parse projects from uri.txt
    parse_projects() 