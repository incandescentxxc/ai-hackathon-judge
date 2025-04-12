#!/usr/bin/env python3
"""
Command line interface for the AI Judge system.
"""

import argparse
import sys
import os
import json
from src.main import parse_projects, process_uri
from src.ai_judge import generate_ratings
from src.extractor import extract_from_file

def main():
    """Main entry point for the AI Judge CLI."""
    parser = argparse.ArgumentParser(description='AI Judge system for evaluating submissions')
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Setup command
    setup_parser = subparsers.add_parser('setup', help='Set up configuration from curl command')
    setup_parser.add_argument('-f', '--file', type=str, default='curl.txt',
                            help='File containing the curl command (default: curl.txt)')
    setup_parser.add_argument('-o', '--output', type=str, default='config.py',
                            help='Output config file (default: config.py)')
    
    # Parse command
    parse_parser = subparsers.add_parser('parse', help='Parse projects and save data to JSON')
    parse_parser.add_argument('-f', '--file', type=str, default='uri.txt',
                            help='File containing project URIs (default: uri.txt)')
    parse_parser.add_argument('-o', '--output', type=str, default='project_data.json',
                            help='Output JSON file (default: project_data.json)')
    
    # Submit command
    submit_parser = subparsers.add_parser('submit', help='Submit ratings for a project')
    submit_parser.add_argument('uri', help='URI of the project to submit')
    submit_parser.add_argument('-r', '--rating', type=int, help='Fixed rating to apply (1-5)')
    submit_parser.add_argument('-a', '--auto', action='store_true', help='Use automatic random ratings (2-4)')
    submit_parser.add_argument('-ai', '--ai', action='store_true', help='Use AI-generated ratings')
    submit_parser.add_argument('-t', '--test-mode', action='store_true', help='Enable test mode to see the OpenAI prompt')
    
    # Fetch command
    fetch_parser = subparsers.add_parser('fetch', help='Fetch project details without submitting')
    fetch_parser.add_argument('uri', help='URI of the project to fetch')
    fetch_parser.add_argument('-o', '--output', type=str, help='Output JSON file (optional)')
    
    # AI command
    ai_parser = subparsers.add_parser('ai', help='Generate AI ratings for a project')
    ai_parser.add_argument('uri', help='URI of the project to analyze')
    ai_parser.add_argument('-o', '--output', help='Output file for the AI ratings (default: stdout)')
    ai_parser.add_argument('-t', '--test-mode', action='store_true', help='Enable test mode to see the OpenAI prompt')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Run test scripts')
    test_parser.add_argument('script', choices=['random', 'ai', 'parser'], help='Test script to run')
    test_parser.add_argument('-t', '--test-mode', action='store_true', help='Enable test mode to see additional debug info')
    test_parser.add_argument('-u', '--url', help='URL to test (for parser tests)')
    test_parser.add_argument('-o', '--output', help='Output file for parser test results')
    
    # Parse arguments
    args = parser.parse_args()
    
    # If no arguments are given, print help
    if not hasattr(args, 'command'):
        parser.print_help()
        return 0
    
    if args.command == 'setup':
        print("Setting up configuration from curl command...")
        success = extract_from_file(curl_file=args.file, config_file=args.output)
        if success:
            print(f"\nSetup complete! Configuration saved to {args.output}")
            print("You can now use the other commands to judge submissions.")
            return 0
        else:
            print("\nSetup failed. Please check the error messages above.")
            return 1
    
    elif args.command == 'parse':
        parse_projects(uri_file=args.file, output_file=args.output)
        return 0
        
    elif args.command == 'submit':
        # Check for conflicting options
        if args.rating is not None and args.auto:
            print("Error: Cannot use both --rating and --auto. Please choose one.")
            return 1
        if args.rating is not None and args.ai:
            print("Error: Cannot use both --rating and --ai. Please choose one.")
            return 1
        if args.auto and args.ai:
            print("Error: Cannot use both --auto and --ai. Please choose one.")
            return 1
            
        # Set up ratings based on options
        ratings = None
        use_ai = False
        
        if args.rating is not None:
            ratings = args.rating
        elif args.ai:
            use_ai = True
        # For args.auto, ratings=None is correct
            
        # Submit the form using process_uri from main.py
        # Make sure fetch_only is False for form submission
        result = process_uri(args.uri, rating=ratings, use_ai=use_ai, fetch_only=False, test_mode=args.test_mode)
        
        # Check result
        if result.get('success', False):
            print(f"Successfully submitted ratings for {result.get('project_title', args.uri)}")
            return 0
        else:
            print(f"Failed to submit ratings: {result.get('error', 'Unknown error')}")
            return 1
    
    elif args.command == 'fetch':
        # Fetch project details without submitting
        project_data = process_uri(args.uri, fetch_only=True)
        
        if project_data:
            print(f"Successfully fetched project: {project_data.get('title', args.uri)}")
            
            # Save to file if output is specified
            if args.output:
                with open(args.output, 'w') as outfile:
                    json.dump(project_data, outfile, indent=2)
                print(f"Project data saved to {args.output}")
            
            return 0
        else:
            print(f"Failed to fetch project data for {args.uri}")
            return 1
            
    elif args.command == 'ai':
        # Generate AI ratings for a project, but don't submit
        ratings = generate_ratings(args.uri, test_mode=args.test_mode)
        
        if ratings:
            if args.output:
                with open(args.output, 'w') as outfile:
                    json.dump(ratings, outfile, indent=2)
                print(f"AI ratings saved to {args.output}")
            return 0
        else:
            print(f"Failed to generate AI ratings for {args.uri}")
            return 1
            
    elif args.command == 'test':
        if args.script == 'random':
            from test_random_ratings import test_random_ratings
            test_random_ratings()
        elif args.script == 'ai':
            from test_ai_judge import test_ai_judge
            test_ai_judge(test_mode=args.test_mode)
        elif args.script == 'parser':
            if args.url:
                # Test parser on a specific URL
                from test_html_parser import test_url_parser
                result = test_url_parser(args.url)
                if args.output and result:
                    with open(args.output, 'w') as outfile:
                        json.dump(result, outfile, indent=2)
                    print(f"Parser test results saved to {args.output}")
            else:
                # Run the standard parser test on example.html
                from test_html_parser import test_html_parser
                test_html_parser()
        return 0
        
    else:
        parser.print_help()
        
    return 0

if __name__ == "__main__":
    sys.exit(main()) 