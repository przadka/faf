# Fire And Forget (FAF)

FAF is a command-line tool designed to streamline your GTD (Getting Things Done) workflow. By capturing and processing any text input using a large language model, FAF structures your data and saves it as a JSON object. These JSON files can be uploaded to Dropbox or another system of your choice and then imported into a Google Sheet for future actions. 

FAF enables you to take quick notes, schedule follow-ups, and more, saving precious time in your day. All of this is accomplished without direct interaction with your email service or other APIs; it simply organizes actions into JSON files ready to be processed further.

At the moment, this is more of a proof-of-concept rather than a production-ready tool, so please use it responsibly. I have already successfully integrated it with my GTD workflow, wrapping it with [Autokey](https://github.com/autokey/autokey), and processing the output in the Google Sheet.

## Features

- **Text Processing**: Utilizes a large language model for processing and understanding input.
- **JSON File Output**: Stores processed information as JSON files that can be uploaded to cloud storage systems like Dropbox for further processing.
- **Command Line Interface**: Easy to integrate with CLI data input.
- **Grammar and Spell Checking**: The large language model will fix any typos and mistakes in your input, ensuring that the output passed further is in correct English.

Currently, FAF recognizes the following requests:

- Send a note to self, e.g., "Buy milk".
- Send a [Follow Up Then](https://www.followupthen.com) message with a specific date or time reference, e.g., "Remind me to buy flowers for my wedding anniversary, this Monday".
- Save a given URL for reviewing it later, e.g., "https://arxiv.org/abs/1706.03762".

## Getting Started

This section provides the instructions necessary to get FAF up and running on your local machine for development and testing.

### Prerequisites

Before getting started, make sure you have the following:

- Python 3.6 or later
- OpenAI key for Langchain
- A cloud storage account, such as Dropbox, for uploading and storing the JSON output files

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

3. **Install the necessary dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set the required environment variables:**

    ```bash
    export OPENAI_API_KEY=your_openai_api_key
    export FAF_JSON_OUTPUT_PATH=/path/to/your/desired/folder
    ```

### Usage

Once your environment is set up and the necessary environment variables are defined, you can use FAF like so:

```bash
python src/faf/main.py "Your text input here"
```

Inputs can range from simple tasks, such as "Buy milk", to more complex instructions like "Follow up with John in 3 weeks about sales meeting". The processed results will be saved as JSON files, which can be uploaded to your cloud storage for further actions.

### Processing JSON files in Google Sheets

FAF outputs processed commands as JSON files. These can be uploaded to your cloud storage solution, and then imported into a Google Sheet for further processing. To automate this process, you can use Google Apps Script or a similar tool to trigger actions based on these commands. You can review an example Google Sheet integration code in the `gsheets.gs` file in this repository.

## Contributing

Contributions are welcomed!

## License

FAF is open-source software licensed under the MIT License.
