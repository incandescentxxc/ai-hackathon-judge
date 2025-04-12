#!/usr/bin/env python3
"""
Test script for the AI judge functionality.
"""

import json
import sys
import argparse
from src.main import process_uri
from src.ai_judge import generate_ratings

def test_ai_judge(test_mode=True):
    """
    Test the AI judge functionality by getting AI ratings for a URI and submitting them.
    
    Args:
        test_mode (bool): If True, print additional debug information like the OpenAI prompt
    """
    
    # Use the URI that we know works
    uri = "/submissions/638720-ai-virtual-pet/judging"
    
    print(f"🤖 Testing AI judging for URI: {uri}")
    
    try:
        # Generate AI ratings based on the project content
        print("\n📋 Generating AI ratings with test_mode=" + ("enabled" if test_mode else "disabled"))
        ai_ratings = generate_ratings(uri, test_mode=test_mode)
        
        if not ai_ratings:
            print("❌ Failed to generate AI ratings. Check your OpenAI API key and connection.")
            return
            
        # Print the AI-generated ratings in a more detailed format
        print("\n🧠 AI-generated ratings:")
        
        # Get the grade IDs (assuming they're in the same order as in the AI judge module)
        grade_ids = list(ai_ratings.keys())
        if len(grade_ids) >= 4:
            criteria = [
                ("Quality of Idea (20%)", grade_ids[0]),
                ("Quality of Code (20%)", grade_ids[1]),
                ("Quality of Project (40%)", grade_ids[2]),
                ("Project Impact (20%)", grade_ids[3])
            ]
            
            # Calculate the weighted score
            weights = [0.2, 0.2, 0.4, 0.2]  # 20%, 20%, 40%, 20%
            total_score = 0
            
            for i, (name, grade_id) in enumerate(criteria):
                score = ai_ratings[grade_id]
                weighted = score * weights[i]
                total_score += weighted
                print(f"  {name}: {score}/5 (weighted: {weighted:.1f})")
            
            print(f"\n  Overall Score: {total_score:.2f}/5")
            
        # Submit the form with AI-generated ratings using process_uri
        print("\n📝 Submitting form with AI ratings...")
        
        # Option 1: Using process_uri with AI judging enabled
        result = process_uri(uri, use_ai=True, fetch_only=False)
        
        # Print the result
        print(f"\n✅ Form submission {'successful' if result.get('success') else 'failed'}")
        print(f"\nResponse details:")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test AI judging functionality")
    parser.add_argument("--test-mode", "-t", action="store_true", default=True, 
                        help="Enable test mode to see the OpenAI prompt and additional information")
    
    args = parser.parse_args()
    test_ai_judge(test_mode=args.test_mode) 