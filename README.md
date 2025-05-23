# Fire And Forget (FAF)

FAF is a versatile command-line tool tailored for productivity enthusiasts, developers, and anyone engaged in a Getting Things Done (GTD) approach. Designed to streamline your GTD workflow, FAF captures and processes any text input using a large language model, structuring your data and saving it as JSON objects. These JSON files can be uploaded to Dropbox or another system of your choice and then processed further with [Zapier](https://zapier.com) or other automation tools. 

FAF enables you to take quick notes, schedule follow-ups, and more, saving some time in your day. This is accomplished without direct interaction with your email service or other APIs; it simply organizes actions into JSON files ready to be processed further.

At the moment, this is more of a proof-of-concept rather than a production-ready tool, so please use it responsibly. I have already successfully integrated it with my GTD workflow, wrapping it with [Autokey](https://github.com/autokey/autokey), and processing the output in a Google Sheet.

## Features

- **Text Processing**: Utilizes a large language model for processing and understanding input.
- **JSON File Output**: Stores processed information as JSON files that can be uploaded to cloud storage systems like Dropbox for further processing.
- **Command Line Interface**: Easy to integrate with CLI data input.
- **Grammar and Spell Checking**: The large language model will fix any typos and mistakes in your input, ensuring that the output passed further is in correct English.
- **Minimal dependency**: Relies primarily on the native OpenAI Assistant API, ensuring a lightweight and efficient operation with minimal setup requirements.
- **MCP Server**: Provides a Model Context Protocol (MCP) server for integration with MCP-compatible clients.

Currently, FAF recognizes the following requests:

- Send a note to self, e.g. "Buy milk".
- Send a [Follow Up Then](https://www.followupthen.com) message with a specific date or time reference, e.g. "Remind me to buy flowers for my wedding anniversary, this Monday".
- Save a given URL for reviewing it later, e.g. "https://arxiv.org/abs/1706.03762".
- Request for a human virtual assistant, e.g., "VA: My wife's birthday is on 28th April. Please help me to book an evening in a nice vegan/vegetarian restaurant."

Every time a user makes any request, FAF will translate it into a single JSON file, compatible with the request. Example of the output JSON file:

```
{"prompt": "VA: My wife's birthday is on 28th April. Please help me to book an evening in a nice vegan/vegetarian restaurant.", "command": "va_request", "payload": {"title": "Birthday dinner reservation for Kavita", "request": "My wife Kavita's birthday is on 28th April. Please help me to book an evening in a nice vegan/vegetarian restaurant."}}
```

## Getting Started

This section provides the instructions necessary to get FAF up and running on your local machine for development and testing.

### Prerequisites

Before getting started, make sure you have the following:

- Python 3.6 or later.
- OpenAI key for interacting with the OpenAI API.

### Installation

1. **Clone the repository:**

```bash
git clone https://github.com/przadka/faf.git
```

2. **Set up a virtual environment and activate it:**

```bash
pip install virtualenv
virtualenv venv
source venv/bin/activate
```

3. **Install the package in development mode:**

```bash
pip install -e .
```

4. **Set the required environment variables:**

FAF uses the following environment variables: 

```bash
export OPENAI_API_KEY=your_openai_api_key
export FAF_JSON_OUTPUT_PATH=/path/to/your/desired/folder
export FAF_USER_NAME="John" # optional
export FAF_CUSTOM_RULES_FILE="/path/to/custom/rules/file.md" # optional
```

`OPENAI_API_KEY` is your unique OpenAI API key necessary for language model processing. `FAF_JSON_OUTPUT_PATH` specifies the path to the folder where you want the output JSON files to be stored. `FAF_USER_NAME` and `FAF_CUSTOM_RULES_FILE` allow you to control how FAF responds to your instructions.

### Usage

Once your environment is set up and the necessary environment variables are defined, you can use FAF like so:

```bash
faf "Your text input here"
```

Inputs can range from simple tasks, such as "Buy milk", to more complex instructions like "Follow up with John in 3 weeks about sales meeting". The processed results will be saved as JSON files, which can be uploaded to your cloud storage for further actions.

You can customize FAF behavior using the following environment variables:

- `FAF_USER_NAME` - is a string representing the username. FAF will try to use that name when executing tasks. This parameter is optional.
- `FAF_CUSTOM_RULES_FILE` - is a path to an MD file which stores additional rules that allow you to further customize how FAF responds to your request. The instructions should be provided as a well-formatted Markdown list, for example:

```markdown
- If the user mentions Multischool, Multi or simply "school" , make sure you use the MT prefix in your content. Example: "MT - Follow up with the teacher about the new project.".
- If Multischool, Multi or school is not mentioned, YOU ARE NOT ALLOWED to use the MT prefix.
- The user's wife's name is Kavita. Try to use Kavita rather than just "wife" in your content.
```

### Creating a single executable file

If you wish to package FAF into a single executable file for easier distribution or deployment across your operating system, follow the steps below:

```bash
nox -s package
```

After running the command, you'll find the single file executable in the `dist` folder.

### Example workflow

FAF serves as a link in a chain of automation tasks. After processing your input and saving it as JSON files, these files can be uploaded to your cloud storage solution, and then processed further. Here's a sample workflow for how you might use FAF:

1. Using [Autokey](https://github.com/autokey/autokey), capture user input with a simple text window and pass this input to FAF. You can review a simple script that does that in `integrations/autokey.py`. By setting up the `FAF_JSON_OUTPUT_PATH` variable, make sure that the file is stored in a folder you wish, for example: `/home/john/.faf`.
2. Next, use a tool like Zapier or Make to create a new row in a Google Sheet every time a new file is uploaded to your Dropbox 'faf' folder. The integration will add a new row to the Google Sheet, with the details from the file included in the new row.
3. With each new row added to the Google Sheet, further process this input with a Google Apps Script, invoking relevant actions based on the nature of the input. An example Google Sheet integration code is available in the `integrations/gsheets.gs` file in this repository.

## Deployment

FAF can be run locally as a standard Python CLI tool, or optionally deployed to AWS Lambda for serverless operation. Most users will simply run FAF locally; Lambda deployment is provided for advanced or cloud-based use cases.

### Running Locally

After installing the package and setting environment variables as described above, you can run FAF directly:

```bash
faf "Your text input here"
```

### Deploying to AWS Lambda (Optional)

Before deploying, copy the example SAM config and fill in your own values:

```bash
cp samconfig.example.toml samconfig.toml
# Edit samconfig.toml and set your stack name, region, and S3 prefix
```

To deploy FAF to AWS Lambda using AWS SAM, use the provided deployment script template:

```bash
cp scripts/lambda_deploy.example.sh scripts/lambda_deploy.sh
# Edit scripts/lambda_deploy.sh and fill in your own values
./scripts/lambda_deploy.sh
```

By default, the script uses a placeholder for the custom rules file path. Edit the script to set your actual path. For convenience, `scripts/lambda_deploy.sh` is gitignored, so your personal deployment script will not be committed.

The script will package the code and dependencies, then run `sam build` and `sam deploy`.

### Running the MCP Server

FAF includes an MCP (Model Context Protocol) server that allows integration with MCP-compatible clients. The MCP server exposes FAF's functionality as tools that translate requests into JSON files, which are stored in a specified location for further processing by integrations like Zapier, Google Sheets, and other automation tools.

The server supports two transport protocols:

#### Stdio Transport (Recommended for Desktop Clients)

Stdio transport is the preferred method for local development and desktop applications like Claude Desktop and VS Code extensions:

```bash
# Start the server with stdio transport (default)
faf-mcp

# Or explicitly specify stdio transport
faf-mcp --transport stdio
```

#### MCP Client Configuration

**Claude Desktop Configuration:**

Add this to your Claude Desktop configuration file (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

```json
{
  "mcpServers": {
    "faf": {
      "command": "faf-mcp",
      "env": {
        "OPENAI_API_KEY": "your_openai_api_key",
        "FAF_JSON_OUTPUT_PATH": "/absolute/path/to/your/output/folder",
        "FAF_USER_NAME": "YourName",
        "FAF_CUSTOM_RULES_FILE": "/absolute/path/to/custom_rules.md"
      }
    }
  }
}
```

**Alternative configurations:**

For packaged installation:
```json
{
  "mcpServers": {
    "faf": {
      "command": "faf-mcp",
      "env": {
        "OPENAI_API_KEY": "your_openai_api_key",
        "FAF_JSON_OUTPUT_PATH": "/absolute/path/to/your/output/folder"
      }
    }
  }
}
```

For HTTP transport:
```json
{
  "mcpServers": {
    "faf": {
      "command": "faf-mcp",
      "args": ["--transport", "http", "--host", "127.0.0.1", "--port", "5000"],
      "env": {
        "OPENAI_API_KEY": "your_openai_api_key",
        "FAF_JSON_OUTPUT_PATH": "/absolute/path/to/your/output/folder"
      }
    }
  }
}
```

**VS Code Extensions and other MCP clients:**

For stdio transport (most common):
```json
{
  "command": "faf-mcp",
  "env": {
    "OPENAI_API_KEY": "your_openai_api_key",
    "FAF_JSON_OUTPUT_PATH": "/absolute/path/to/your/output/folder"
  }
}
```

#### HTTP Transport (For Remote Deployments)

HTTP transport uses FastMCP's streamable-http protocol for remote deployments and testing:

```bash
# Start the server with HTTP transport (uses streamable-http)
faf-mcp --transport http --host 127.0.0.1 --port 5000

# Customize the mount path and logging level
faf-mcp --transport http --host 127.0.0.1 --port 5000 --path /faf --log-level debug
```

The MCP server provides the following tools:
- `follow_up_then` - Send a follow-up reminder with a specific date
- `note_to_self` - Send a simple note/to-do
- `save_url` - Save a URL for later review
- `va_request` - Send a request to a virtual assistant
- `journaling_topic` - Save a journaling topic

**Testing HTTP Transport:**

You can test the streamable HTTP transport using curl or any HTTP client:

```bash
# Test a connection to the server (default path /mcp)
curl -X POST http://127.0.0.1:5000/mcp -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"capabilities/get","params":{},"id":1}'

# Execute a tool
curl -X POST http://127.0.0.1:5000/mcp -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"tools/execute","params":{"name":"note_to_self","arguments":{"prompt":"Test note","message":"Remember to test the MCP server"}},"id":2}'

# If using a custom path, adjust the URL accordingly
curl -X POST http://127.0.0.1:5000/faf -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"capabilities/get","params":{},"id":1}'
```

#### Troubleshooting MCP Setup

**Common Issues and Solutions:**

1. **Server fails to start:**
   ```bash
   Error: Could not import FastMCP
   ```
   **Solution:** Install FastMCP: `pip install fastmcp`

2. **Environment variables not found:**
   ```bash
   Error: OPENAI_API_KEY not set
   ```
   **Solution:** Ensure all required environment variables are set in the MCP client configuration, not just in your shell.

3. **Claude Desktop doesn't recognize the server:**
   - Verify the configuration file path is correct
   - Use absolute paths for `command` and file paths in `env`
   - Restart Claude Desktop after configuration changes
   - Check Claude Desktop logs for specific error messages

4. **Permission denied errors:**
   ```bash
   Error: Permission denied: python
   ```
   **Solutions:** 
   - Use the full path to python: `/usr/bin/python3` or `/path/to/venv/bin/python`
   - Ensure the FAF directory and files are readable
   - On macOS, grant Terminal/Claude Desktop appropriate permissions

5. **Tools not appearing in client:**
   - Verify the server starts without errors: `python src/faf/mcp_server.py --transport stdio`
   - Check that all environment variables are properly set
   - Ensure `FAF_JSON_OUTPUT_PATH` directory exists and is writable

6. **Module not found errors:**
   ```python
   ModuleNotFoundError: No module named 'faf'
   ```
   **Solution:** Install FAF in development mode: `pip install -e .`

**Debugging Tips:**

- Test the MCP server standalone before configuring with clients: `faf-mcp --transport stdio`
- Use `faf-mcp --transport stdio` to test server startup and tool availability
- Check that JSON output files are being created in `FAF_JSON_OUTPUT_PATH`
- Verify the OpenAI API key works by testing FAF CLI directly first

**Environment Variable Requirements:**

All MCP client configurations must include these environment variables:
- `OPENAI_API_KEY` (required): Your OpenAI API key
- `FAF_JSON_OUTPUT_PATH` (required): Directory for JSON output files
- `FAF_USER_NAME` (optional): Username for personalization
- `FAF_CUSTOM_RULES_FILE` (optional): Path to custom rules file

## Contributing

Contributions are welcomed!

## License

FAF is open-source software licensed under the MIT License.
