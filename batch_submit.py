#!/usr/bin/env python3
"""
Batch submission script for processing multiple projects.
"""

from src.main import process_uri
import json
import time
import argparse

def batch_submit_forms(uris, rating=3, delay=2, auto_mode=False, ai_mode=False):
    """
    Submit forms for multiple projects in batch
    
    Args:
        uris (list): List of project URIs to process
        rating (int): Rating to apply to all criteria (default: 3)
        delay (int): Delay in seconds between requests (default: 2)
        auto_mode (bool): Use automatic random ratings (2-4) if True (default: False)
        ai_mode (bool): Use AI-generated ratings if True (default: False)
        
    Returns:
        dict: Results of all submissions
    """
    results = {}
    
    for i, uri in enumerate(uris, 1):
        print(f"\nProcessing {i}/{len(uris)}: {uri}")
        
        # Submit the form using process_uri
        if ai_mode:
            print("Using AI to generate ratings based on project content...")
            result = process_uri(uri, use_ai=True)
        elif auto_mode:
            print("Using automatic random ratings (2-4)...")
            result = process_uri(uri, rating=None)  # None triggers random ratings
        else:
            result = process_uri(uri, rating=rating)
            
        results[uri] = result
        
        # Save progress after each submission
        with open('submission_results.json', 'w') as outfile:
            json.dump(results, outfile, indent=2)
        
        # Add a delay between requests to avoid overwhelming the server
        if i < len(uris):
            print(f"Waiting {delay} seconds before next submission...")
            time.sleep(delay)
    
    return results

def main():
    parser = argparse.ArgumentParser(description='Submit forms for multiple projects in batch')
    parser.add_argument('-r', '--rating', type=int, default=3, 
                        help='Rating to apply to all criteria (1-5, default: 3)')
    parser.add_argument('-d', '--delay', type=int, default=2,
                        help='Delay in seconds between requests (default: 2)')
    parser.add_argument('-f', '--file', type=str, default='uri.txt',
                        help='File containing URIs to process (default: uri.txt)')
    parser.add_argument('-c', '--count', type=int, default=None,
                        help='Number of URIs to process (default: all)')
    parser.add_argument('-a', '--auto', action='store_true', 
                        help='Use automatic random ratings (2-4) instead of fixed rating')
    parser.add_argument('-ai', '--ai', action='store_true', 
                        help='Use AI to generate ratings based on project content')
    args = parser.parse_args()
    
    # Check for conflicting modes
    if args.auto and args.ai:
        print("Error: Cannot use both --auto and --ai modes simultaneously. Please choose one.")
        return
    
    # Validate rating if not in auto or AI mode
    if not args.auto and not args.ai and (args.rating < 1 or args.rating > 5):
        print(f"Invalid rating: {args.rating}. Must be between 1 and 5.")
        return
    
    # Read URIs from file
    with open(args.file, 'r') as file:
        uris = [line.strip().strip(',') for line in file.readlines()]
    
    # Limit the number of URIs to process if specified
    if args.count is not None and args.count > 0:
        uris = uris[:args.count]
    
    if args.ai:
        print(f"Preparing to submit forms for {len(uris)} projects with AI-GENERATED ratings")
    elif args.auto:
        print(f"Preparing to submit forms for {len(uris)} projects with AUTOMATIC RANDOM ratings (2-4)")
    else:
        print(f"Preparing to submit forms for {len(uris)} projects with rating {args.rating}")
    
    # Confirm with the user
    confirm = input("Continue? (y/n): ")
    if confirm.lower() != 'y':
        print("Aborted.")
        return
    
    # Submit forms
    results = batch_submit_forms(uris, rating=args.rating, delay=args.delay, 
                               auto_mode=args.auto, ai_mode=args.ai)
    
    # Count successes and failures
    successes = sum(1 for result in results.values() if result.get('success', False))
    failures = len(results) - successes
    
    print(f"\nCompleted {len(results)} submissions: {successes} successful, {failures} failed")
    print(f"Results saved to submission_results.json")

if __name__ == "__main__":
    main() 
