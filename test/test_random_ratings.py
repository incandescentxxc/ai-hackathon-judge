#!/usr/bin/env python3
from judge import submit_form
import json

def test_random_ratings():
    """Test submitting a form with random ratings between 2-4"""
    # Test with a specific URI
    uri = "/submissions/638720-ai-virtual-pet/judging"
    
    print(f"Testing form submission with random ratings for: {uri}")
    
    # Submit the form with random ratings (by passing None for ratings)
    result = submit_form(uri, ratings=None)
    
    print("\nSubmission result:")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_random_ratings() 