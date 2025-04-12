# AI Judge System

A tool for automatically evaluating submissions with both random and AI-powered grading.

## Setup

1. Run the setup script to install dependencies and configure the system:

```bash
python setup.py
```

The setup will:
- Check your Python version (requires 3.6+)
- Install required dependencies
- Help you set up the configuration
- Check for a URI file

## Configuration

During setup, you can configure the system in two ways:

1. **Extract from curl command**: If you have a curl command from the browser, the system can extract important parameters automatically.
2. **Manual setup**: Provide parameters manually.

You'll also be prompted for an OpenAI API key if you plan to use AI-powered judging.

### Extracting Headers and Cookies from Browser

To make configuration easier, you can extract authentication headers and cookies directly from your browser:

1. Log in to your Devpost account in your browser
2. Open browser developer tools (F12 or right-click > Inspect)
3. Go to the Network tab and refresh the page
4. Right-click on any document request and select "Copy as cURL"
5. When running `python setup.py`, choose the extract from curl command option
6. Paste the copied curl command when prompted

Alternatively, you can use the CLI command:

```bash
# Extract from curl.txt and save to config.py
python cli.py setup

# Specify custom input/output files
python cli.py setup -f my_curl.txt -o my_config.py
```

This extraction process automatically gets all the necessary headers and cookies for authentication, making setup much easier.

## Usage

### Random Ratings Test

To test form submission with random ratings:

```bash
python test_random_ratings.py
```

This will submit a form with random ratings between 2 and 4 for each grading section.

### AI Judging Test

To test the AI-powered judging:

```bash
python test_ai_judge.py
```

This will:
1. Generate AI ratings based on project content
2. Submit the form with these AI-generated ratings
3. Display the results

## Files

- `src/`: Core package directory
  - `__init__.py`: Package initialization
  - `config.py`: Configuration loading and management
  - `parser.py`: HTML parsing utilities
  - `project.py`: Project fetching and processing
  - `judge.py`: Form submission logic
  - `ai_judge.py`: AI-powered rating generation
  - `main.py`: Core functionality for the entire system
  - `extractor.py`: Header and cookie extraction utilities
- `cli.py`: Main entry point and command-line interface
- `batch_submit.py`: Script for batch processing submissions
- `test_random_ratings.py`: Script to test random ratings
- `test_ai_judge.py`: Script to test AI judging
- `config_template.py`: Template for authentication configuration
- `setup.py`: Installation and configuration script
- `uri.txt`: List of submission URIs (referenced during tests)

## CLI Usage

The project's main entry point is `cli.py`, providing a unified command-line interface:

```bash
# Set up configuration from a curl command
python cli.py setup

# Use custom curl file and config output file
python cli.py setup -f my_curl.txt -o my_config.py

# Parse projects and save data to JSON
python cli.py parse

# Parse with custom input/output files
python cli.py parse -f my_uris.txt -o output.json

# Fetch project details without submitting
python cli.py fetch /submissions/123456-project-name/judging

# Save fetched project details to a file
python cli.py fetch /submissions/123456-project-name/judging -o project.json

# Submit ratings for a specific project (with fixed rating 3)
python cli.py submit /submissions/123456-project-name/judging -r 3

# Submit with random ratings
python cli.py submit /submissions/123456-project-name/judging -a

# Submit with AI-generated ratings
python cli.py submit /submissions/123456-project-name/judging -ai

# Generate and display AI ratings (without submitting)
python cli.py ai /submissions/123456-project-name/judging

# Save AI ratings to a file
python cli.py ai /submissions/123456-project-name/judging -o ratings.json

# Run test scripts
python cli.py test random
python cli.py test ai
```

Batch processing is also available through the batch_submit.py script:

```bash
# Submit with AI ratings for all projects in uri.txt
python batch_submit.py -ai

# Submit with automatic random ratings
python batch_submit.py -a

# Process only the first 5 projects with a fixed rating of 4
python batch_submit.py -r 4 -c 5
```

## Project Architecture

The AI Judge system follows a modular architecture:

1. **CLI Layer** (`cli.py`): The main entry point that provides a command-line interface
2. **Core Logic** (`src/main.py`): Central module providing unified functionality
3. **Service Modules**:
   - `src/judge.py`: Form submission logic
   - `src/ai_judge.py`: AI rating generation
   - `src/project.py`: Project data fetching
   - `src/parser.py`: HTML parsing
   - `src/config.py`: Configuration management
   - `src/extractor.py`: Header and cookie extraction for authentication

This layered approach makes the code more maintainable and allows for easy extension of functionality.

## How It Works

The system can operate in two modes:

1. **Random Rating**: Generates random scores between 2-4 for each grading section.
2. **AI Rating**: Uses OpenAI to analyze project content and generate appropriate ratings.

When submitting a form, the system will:
- Fetch the project details
- Generate ratings (either randomly or using AI)
- Submit the form with these ratings
- Return the response
