#!/usr/bin/env python3
"""
Test script for the random rating functionality.
"""

import json
import sys
from src.main import process_uri

def test_random_ratings():
    """Test the random rating functionality by submitting a form with random ratings."""
    
    # Use the URI from curl.txt that we know works
    uri = "/submissions/638720-ai-virtual-pet/judging"
    
    print(f"🎲 Testing random ratings for URI: {uri}")
    
    try:
        # Generate random ratings between 2 and 4
        print("Generating random ratings...")
        
        # Use process_uri with random ratings
        # Make sure we're not just fetching data by setting fetch_only=False
        result = process_uri(uri, rating=None, use_ai=False, fetch_only=False)
        
        # Print the result in a nicely formatted way
        print(f"\n✅ Form submission {'successful' if result.get('success') else 'failed'}")
        print(f"\nResponse details:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return
    
if __name__ == "__main__":
    test_random_ratings() 