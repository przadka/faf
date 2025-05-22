# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Fire And Forget (FAF) is a command-line tool for productivity that helps with GTD (Getting Things Done) workflows by capturing and processing text input using a large language model (LLM). It structures data as JSON objects that can be uploaded to storage services and processed with automation tools like Zapier.

FAF can process different types of requests including:
- Notes to self (simple todos)
- Follow-up reminders with date/time references
- URL saving for later review
- Virtual assistant requests
- Journaling topics

## Environment Setup

FAF requires the following environment variables:
```
export OPENAI_API_KEY=your_openai_api_key
export FAF_JSON_OUTPUT_PATH=/path/to/your/desired/folder
export FAF_USER_NAME="John" # optional
export FAF_CUSTOM_RULES_FILE="/path/to/custom/rules/file.md" # optional
```

## Development Commands

### Installation and Setup

```bash
# Clone the repository
git clone https://github.com/przadka/faf.git

# Set up virtual environment
pip install virtualenv
virtualenv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application

```bash
# Run FAF with input
python src/faf/main.py "Your text input here"
```

### Packaging

To create a single executable file:
```bash
nox -s package
```
This will create an executable in the `dist` folder.

### Linting

```bash
ruff check .
```

### AWS Lambda Deployment (Optional)

```bash
# Copy and customize the example files
cp samconfig.example.toml samconfig.toml
cp scripts/lambda_deploy.example.sh scripts/lambda_deploy.sh

# Edit the files with your own values, then run:
./scripts/lambda_deploy.sh
```

## Code Architecture

### Core Components

1. **Main Module** (`src/faf/main.py`):
   - Contains the application logic, environment setup, and LLM interactions
   - Processes user input using OpenAI's API
   - Handles both local CLI execution and AWS Lambda invocation

2. **Tools Module** (`src/faf/tools.py`):
   - Defines the core functions that process different request types:
     - `follow_up_then`: For scheduling reminders
     - `note_to_self`: For simple notes/todos
     - `save_url`: For saving URLs for later
     - `va_request`: For virtual assistant requests
     - `journaling_topic`: For saving journaling ideas

3. **Custom Rules** (`custom_rules.md`):
   - Optional file that can be referenced via environment variables
   - Allows customization of how FAF processes requests

### Data Flow

1. User input is captured (via CLI or Lambda)
2. Input is preprocessed and categorized by type
3. LLM processes the input and determines which tool function to use
4. The appropriate tool function structures the output as JSON
5. JSON is saved to the specified output directory
6. External integrations (like Google Sheets via Apps Script) can process the JSON files

### Integration Mechanisms

1. **Autokey Integration** (`integrations/autokey.py`):
   - Creates a dialog for capturing input
   - Calls FAF with the captured input

2. **Google Sheets Integration** (`integrations/gsheets.gs`):
   - Processes JSON files uploaded to Google Sheets
   - Executes different actions based on the command type

## Tips for Development

- When modifying tool functions, ensure the function docstrings remain accurate as they're used to generate function descriptions for the LLM
- When adding new tools, update the `tools_list()` function in `main.py` to include the new function
- Custom rules are loaded from the `FAF_CUSTOM_RULES_FILE` and added to the LLM context

## Best Practices

- Avoid AI attribution in commit messages