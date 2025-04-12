#!/usr/bin/env python3
from batch_submit import batch_submit_forms

def test_batch():
    """Test batch submission with one project"""
    # Get the first URI from uri.txt
    with open('uri.txt', 'r') as file:
        uri = file.readline().strip().strip(',')
    
    print(f"Testing batch submission with URI: {uri}")
    
    # Submit form with automatic random ratings
    results = batch_submit_forms([uri], auto_mode=True)
    
    # Print summary
    successes = sum(1 for result in results.values() if result.get('success', False))
    failures = len(results) - successes
    
    print(f"\nCompleted {len(results)} submissions: {successes} successful, {failures} failed")

if __name__ == "__main__":
    test_batch() 