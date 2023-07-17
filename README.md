# Fire And Forget (FAF)

FAF is a command line tool designed to streamline your GTD (Getting Things Done) workflow. By capturing and processing any text input using a sophisticated language model, FAF structures your data and stores it directly in a Google Sheet for future actions. 

FAF enables you to take quick notes, schedule follow-ups, and more, saving precious time in your day. All this without direct interaction with your email service or other APIs; it simply organizes actions into your Google Sheet via an IFTTT webhook. 

## Features

- **Text Processing**: Utilizes a powerful language model for processing and understanding input.
- **Google Sheets Integration**: Communicates with Google Sheets through IFTTT, storing processed information for subsequent actions.
- **Command Line Interface**: User-friendly and easy-to-use for quick data input.

## Getting Started

This section provides the instructions necessary to get FAF up and running on your local machine for development and testing.

### Prerequisites

Before getting started, make sure you have the following:

- Python 3.6 or later
- IFTTT key
- OpenAI key for Langchain
- An IFTTT webhook integration that saves given URL requests in a Google Sheet

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
    export IFTTT_KEY=your_ifttt_key
    ```

### Usage

Once your environment is set up and the necessary environment variables are defined, you can use FAF like so:

```bash
python src/faf/main.py "Your text input here"
```

Inputs can range from simple tasks, such as "Buy milk", to more complex instructions like "Follow up with John in 3 weeks about sales meeting". The processed results will be saved in your designated Google Sheet for further actions.

## Contributing

Contributions are welcomed! For detailed information about our code of conduct and the process for submitting pull requests, please read our [contribution guidelines](https://github.com/przadka/faf/CONTRIBUTING.md).

## License

FAF is open-source software licensed under the MIT License. For more information, see the [LICENSE.md](https://github.com/przadka/faf/LICENSE.md) file.