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

```
git clone https://github.com/przadka/faf.git
```

2. **Set up a virtual environment and activate it:**

```
pip install virtualenv
virtualenv venv
source venv/bin/activate
```

3. **Install the necessary dependencies:**

```
pip install -r requirements.txt
```

4. **Set the required environment variables:**

FAF uses the following environment variables: 

```
export OPENAI_API_KEY=your_openai_api_key
export FAF_JSON_OUTPUT_PATH=/path/to/your/desired/folder
export FAF_USER_NAME="John" # optional
export FAF_CUSTOM_RULES_FILE="/path/to/custom/rules/file.md" # optional
```

`OPENAI_API_KEY` is your unique OpenAI API key necessary for language model processing. `FAF_JSON_OUTPUT_PATH` specifies the path to the folder where you want the output JSON files to be stored. `FAF_USER_NAME` and `FAF_CUSTOM_RULES_FILE` allow you to control how FAF responds to your instructions.

### Usage

Once your environment is set up and the necessary environment variables are defined, you can use FAF like so:

```
python src/faf/main.py "Your text input here"
```

Inputs can range from simple tasks, such as "Buy milk", to more complex instructions like "Follow up with John in 3 weeks about sales meeting". The processed results will be saved as JSON files, which can be uploaded to your cloud storage for further actions.

You can customize FAF behavior using the following environment variables:

- `FAF_USER_NAME` - is a string representing the user name. FAF will try to use that name when executing tasks. This parameter is optional.
- `FAF_CUSTOM_RULES_FILE` - is a path to an MD file which stores additional rules that allow you to further customize how FAF responds to your request. The instructions should be provided as a well-formatted markdown list, for example:

```
- If the user mentions Multischool, Multi or simply "school" , make sure you use the MT prefix in your content. Example: "MT - Follow up with the teacher about the new project.".
- If Multischool, Multi or school is not mentioned, YOU ARE NOT ALLOWED to use the MT prefix.
- The user's wife's name is Kavita. Try to use Kavita rather than just "wife" in your content.
```

### Creating a single executable file

If you wish to package FAF into a single executable file for easier distribution or deployment across your operating system, follow the steps below:

```
nox -s package
```

After running the command, you'll find the single file executable in the `dist` folder.

### Example workflow

FAF serves as a link in a chain of automation tasks. After processing your input and saving it as JSON files, these files can be uploaded to your cloud storage solution, and then processed further. Here's a sample workflow for how you might use FAF:

1. Using [Autokey](https://github.com/autokey/autokey), capture user input with a simple text window and pass this input to FAF. You can review a simple script that does that in `autokey.py`. By setting up the `FAF_JSON_OUTPUT_PATH` variable, make sure that the file is stored in a folder you wish, for example: `/home/john/.faf`.
2. Next, utilize a tool like Zapier to create a new row in a Google Sheet every time a new file is uploaded to your Dropbox 'faf' folder. The integration will add a new row to the Google Sheet, with the details from the file included in the new row.
3. With each new row added to the Google Sheet, further process this input with a Google Apps Script, invoking relevant actions based on the nature of the input. An example Google Sheet integration code is available in the `gsheets.gs` file in this repository.

## Contributing

Contributions are welcomed!

## License

FAF is open-source software licensed under the MIT License.
