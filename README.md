# AI-Judge

A tool for automating the judging process for Devpost hackathon submissions. Created with the collaboration of @Cursor.

## Overview

This tool automates the process of submitting judge ratings for Devpost hackathon projects. It can:

- Parse project information from Devpost pages
- Submit ratings (fixed or random) for projects
- Process multiple submissions in batch

## Setup

1. Clone the repository:
   ```
   git clone https://github.com/your-username/ai-judge.git
   cd ai-judge
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up your authentication configuration:
   ```
   # Option 1 (Recommended): Use extract_header_cookie.py (see Authentication section)
   
   # Option 2: Manual setup
   cp config_template.py config.py
   # Then edit config.py with your own authentication details
   ```

## Usage

### Single Form Submission

You can submit a rating for a single project:

```python
from judge import submit_form

# Submit with a fixed rating (3)
result = submit_form("/submissions/123456-project-name/judging", ratings=3)

# Submit with random ratings (between 2-4)
result = submit_form("/submissions/123456-project-name/judging", ratings=None)
```

### Batch Submission

Process multiple submissions at once:

```
# Submit with a fixed rating (3) for all submissions
python batch_submit.py -r 3

# Submit with random ratings (between 2-4) for all submissions
python batch_submit.py -a

# Process only the first 10 submissions
python batch_submit.py -a -c 10

# Set a 5 second delay between submissions
python batch_submit.py -a -d 5

# Use a different URI file
python batch_submit.py -a -f my_uris.txt
```

### Testing

You can run the test script to verify the functionality:

```
python test_random_ratings.py
```

## Files

- `judge.py`: Main module with functions to parse project pages and submit ratings
- `batch_submit.py`: Script for batch processing multiple submissions
- `uri.txt`: List of project URIs to process
- `test_random_ratings.py`: Test script for the random rating functionality
- `config_template.py`: Template for authentication configuration
- `config.py`: Your personal authentication details (not included in repository)
- `extract_header_cookie.py`: Helper script to extract headers and cookies from a curl command
- `curl.txt`: File where you paste your curl command (not included in repository)
- `requirements.txt`: List of Python package dependencies

## Authentication

This tool requires authentication cookies from an active Devpost session to work correctly. 
You can use one of the following methods to set up authentication:

### Option 1: Using extract_header_cookie.py (Recommended)

This is the easiest way to set up authentication:

1. Log in to your Devpost account in your browser
2. Open browser developer tools (F12 or right-click > Inspect)
3. Go to the Network tab and refresh the page
4. Right-click on any document request and select "Copy as cURL"
5. Create a file named `curl.txt` and paste the copied curl command into it
6. Run the helper script:
   ```
   python extract_header_cookie.py
   ```
7. The script will automatically create a `config.py` file with your authentication details

### Option 2: Manual setup with config_template.py

1. Copy the template configuration:
   ```
   cp config_template.py config.py
   ```
2. Edit `config.py` and manually replace the cookie values with your own
3. To get cookie values:
   - Log in to your Devpost account in your browser
   - Open browser developer tools (F12)
   - Go to the Network tab and refresh the page
   - Click on any document request
   - Find the "Cookies" section in the request headers
   - Copy the needed cookie values (especially 'jwt', 'remember_user_token', and '_devpost')

**Important:** Never commit your `config.py` or `curl.txt` files to version control as they contain your personal authentication information.
