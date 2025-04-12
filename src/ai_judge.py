#!/usr/bin/env python3
"""
AI-powered judging for generating ratings based on project content.
"""

import json
import random
import os
from .settings import load_config
from .project import fetch_and_parse_project

# Try to import openai, but don't fail if it's not installed
try:
    from openai import OpenAI  # Import the client directly from openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    print("Warning: OpenAI module not installed. AI judging functionality will be limited.")
    print("Install with: pip install openai>=1.0.0")

# Global variables to track API errors
LAST_OPENAI_ERROR = None

def generate_ai_ratings(project_data, test_mode=False):
    """
    Use OpenAI's API to generate ratings for a project based on its content.
    
    Args:
        project_data (dict): The project data extracted from the page
        test_mode (bool): If True, print additional debug information
        
    Returns:
        dict: A dictionary mapping grade IDs to ratings (1-5)
    """
    global LAST_OPENAI_ERROR
    
    # Check if OpenAI is available
    if not OPENAI_AVAILABLE:
        print("Error: OpenAI module not installed. Cannot generate AI ratings.")
        print("Falling back to random ratings.")
        return generate_random_ratings(project_data)
    
    # Load OpenAI API key and model from config
    _, _, _, openai_api_key, openai_model = load_config()
    
    if not openai_api_key:
        print("Error: OpenAI API key not found. Please set OPENAI_API_KEY in config.py or as an environment variable.")
        return generate_random_ratings(project_data)
    
    # Prepare the project content for the prompt
    project_content = {
        "title": project_data.get("title", "Unknown Title"),
        "description": project_data.get("description", "No description available"),
    }
    
    # Add available sections
    section_keys = [
        "Inspiration",
        "What it does",
        "How we built it",
        "Challenges we ran into",
        "Accomplishments that we're proud of",
        "What we learned"
    ]
    
    for key in section_keys:
        if key in project_data:
            project_content[key] = project_data[key]
    
    # Check for "What's next for" section which includes the project name
    for key in project_data:
        if key.startswith("What's next for"):
            project_content["Future Plans"] = project_data[key]
    
    # Convert project content to a formatted string
    content_str = json.dumps(project_content, indent=2)
    
    # Prepare the prompt for the AI
    prompt = f"""
You are an experienced hackathon judge evaluating a project submission. Please analyze the following project information and rate it on a scale of 1-5 in each category, where:
1 = Poor
2 = Below Average
3 = Average
4 = Good
5 = Excellent

Project Information:
{content_str}

Please provide ratings for the following criteria:
1. Quality of Idea (20%): How original, innovative, and well-conceived is the project idea?
2. Quality of Code (20%): How technically complex, well-implemented, and clean is the project's code?
3. Quality of Project (40%): How well-executed is the overall project, including usability, design, and completeness?
4. Project Impact (20%): How impactful or useful is the project? What potential does it have to solve real problems?

Return your response in a valid JSON format with just the ratings, like this:
{{
  "idea_quality": 4,
  "code_quality": 3,
  "project_quality": 4,
  "impact": 5
}}

Only return the JSON, no additional text.
"""

    # In test mode, print the prompt for better observability
    if test_mode:
        print("\n===== AI MODEL INFORMATION =====")
        print(f"Model: {openai_model}")
        quota_error = LAST_OPENAI_ERROR if LAST_OPENAI_ERROR else "None (API call will be attempted)"
        print(f"API Key Status: {'Valid' if openai_api_key else 'Missing'}")
        print(f"API Key (first 8 chars): {openai_api_key[:8]}..." if openai_api_key and len(openai_api_key) > 8 else "N/A")
        print(f"Last Known Quota Error: {quota_error}")
        print("===== END MODEL INFORMATION =====\n")
        
        print("\n===== BEGIN OPENAI PROMPT =====")
        print(prompt)
        print("===== END OPENAI PROMPT =====\n")
        
        # Also print a summary of the project content being analyzed
        print("\n===== PROJECT CONTENT SUMMARY =====")
        print(f"Title: {project_content.get('title')}")
        print(f"Description: {project_content.get('description')[:100]}..." if len(project_content.get('description', '')) > 100 else project_content.get('description'))
        
        # Print the number of sections available
        sections_available = sum(1 for key in section_keys if key in project_content)
        print(f"Sections available: {sections_available}/{len(section_keys)}")
        
        # Print which sections are available and their length
        print("\nSection details:")
        for key in section_keys:
            if key in project_content:
                content = project_content[key]
                print(f"  - {key}: {len(content)} chars")
            else:
                print(f"  - {key}: Not available")
                
        # Print total content length
        total_chars = sum(len(project_content.get(key, "")) for key in project_content)
        print(f"\nTotal content length: {total_chars} characters")
        
        print("===== END PROJECT CONTENT SUMMARY =====\n")

    try:
        # Set up the OpenAI client using the latest API version
        # We avoid setting any proxy configuration to prevent issues
        client = OpenAI(
            api_key=openai_api_key,
            # Don't use any proxy configuration
            http_client=None
        )
        
        # Call the OpenAI API
        if test_mode:
            print("Calling OpenAI API with model:", openai_model)
            
        response = client.chat.completions.create(
            model=openai_model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        # Reset error since the call was successful
        LAST_OPENAI_ERROR = None
        
        # Get the response text
        ai_response = response.choices[0].message.content.strip()
        
        if test_mode:
            print("\n===== OPENAI RESPONSE =====")
            print(ai_response)
            print("===== END OPENAI RESPONSE =====\n")
        
        # Parse the JSON response
        try:
            ratings_data = json.loads(ai_response)
            
            # Map the AI ratings to the grade IDs
            # Since we don't know which grade ID corresponds to which criterion,
            # we'll assume the first field is idea quality, second is code quality, etc.
            # This works because the IDs are stable
            grade_ids = list(project_data['grade_fields'].keys())
            
            if len(grade_ids) >= 4:
                ai_ratings = {
                    grade_ids[0]: ratings_data.get('idea_quality', 3),
                    grade_ids[1]: ratings_data.get('code_quality', 3), 
                    grade_ids[2]: ratings_data.get('project_quality', 3),
                    grade_ids[3]: ratings_data.get('impact', 3)
                }
                
                print("AI-generated ratings:")
                print(f"  Quality of Idea (20%): {ai_ratings[grade_ids[0]]}")
                print(f"  Quality of Code (20%): {ai_ratings[grade_ids[1]]}")
                print(f"  Quality of Project (40%): {ai_ratings[grade_ids[2]]}")
                print(f"  Project Impact (20%): {ai_ratings[grade_ids[3]]}")
                
                return ai_ratings
            else:
                print("Error: Not enough grade fields to map AI ratings.")
                return generate_random_ratings(project_data)
            
        except json.JSONDecodeError:
            print("Error: Failed to parse AI response as JSON.")
            print(f"Response: {ai_response}")
            return generate_random_ratings(project_data)
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error calling OpenAI API: {error_msg}")
        
        # Store the last OpenAI error for future reference
        LAST_OPENAI_ERROR = error_msg
        
        return generate_random_ratings(project_data)

def generate_random_ratings(project_data):
    """Generate random ratings as a fallback."""
    grade_ids = list(project_data['grade_fields'].keys())
    random_ratings = {}
    
    # Create random ratings between 2-4 for each criteria
    for grade_id in grade_ids:
        random_ratings[grade_id] = random.randint(2, 4)
    
    print("Generated random ratings:")
    if len(grade_ids) >= 4:
        print(f"  Quality of Idea (20%): {random_ratings[grade_ids[0]]}")
        print(f"  Quality of Code (20%): {random_ratings[grade_ids[1]]}")
        print(f"  Quality of Project (40%): {random_ratings[grade_ids[2]]}")
        print(f"  Project Impact (20%): {random_ratings[grade_ids[3]]}")
    else:
        print(random_ratings)
        
    return random_ratings

def generate_ratings(uri, test_mode=False):
    """
    Generate AI ratings for a project based on its URI.
    
    Args:
        uri (str): The URI of the project
        test_mode (bool): If True, print additional debug information
        
    Returns:
        dict: A dictionary mapping grade IDs to ratings (1-5) or None if failed
    """
    # Fetch and parse the project data
    project_data = fetch_and_parse_project(uri)
    
    if not project_data:
        print(f"Failed to fetch project data for URI: {uri}")
        return None
    
    # Generate AI ratings using the project data
    return generate_ai_ratings(project_data, test_mode=test_mode) 