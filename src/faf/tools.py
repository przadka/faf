import json
import re

def follow_up_then(prompt:str, date: str, message: str) -> str:
    """
    Send a follow-up reminder with the given date and message.
    Use ONLY IF there is a specific date provided or
    a time reference, like "tomorrow" or "in 2 days".

    Constraints on the date:

      - Never use "this" in the date like "thisMonday" or "thisTuesday" as FUT does not
        support them.
      - Never use "in a week", "in two weeks" or "in a month" replace them with "1week",
      "2weeks" and "1month" respectively.
      - Date cannot have any spaces, dots, semicolons or commas.
      - Never use colons in hours, use "3pm" instead of "3:00pm".

    Args:
        prompt: Full input provided by the user, exactly as it was typed.
        date: Date of the follow-up in the format like "1August", "tomorrow3pm" or "in2days".
        message: Message to send. Do not include the date in the message.

    Returns:
        JSON string with all the data.
    """

    # the following shouln't be needed as the LLM already does knows the date specs
    # and should generate the date in the correct format
    # but just in case, we do it here as well

    date = date.replace("this", "")
    date = date.replace(" ", "")
    date = date.replace(".", "")
    date = date.replace(",", "")
    date = date.replace(":", "")

    # remove "in" if used as "inXday" or "inXweek" or "inXmonth", match the number and the unit
    date = re.sub(r'in(\d+)(day|week|month)', r'\1\2', date)

    tool_data = {
        "prompt": prompt,
        "command": "follow_up_then",
        "payload": {
            "date": date,
            "message": message
        }
    }

    # return the JSON object as a string
    return json.dumps(tool_data)

def note_to_self(prompt:str, message: str) -> str:
    """
    Send a note to user with the given message.
    Useful for simple todos, reminders and short-term follow ups.

    Args:
        prompt: Full input provided by the user, exactly as it was typed.
        message: Message to send. Should be based on the prompt, without any additional information.

    Returns:
        JSON string with all the data.
    """

    tool_data = {
        "prompt": prompt,
        "command": "note_to_self",
        "payload": {
            "message": message
        }
    }

    return json.dumps(tool_data)

def save_url(prompt:str, url: str) -> str:
    """
    Save a URL to a URL list so that I can review it later. Use only if the input is a valid URL.

    Args:
        prompt: Full input provided by the user, exactly as it was typed.
        user_url: URL to append to the URL list.

    Returns:
        JSON string with all the data.
    """

    # check if the input is URL-like, starts with http or https, has a dot in the middle,
    # and does not have any spaces

    if not url.startswith("http") or "." not in url or " " in url:
        return "Error: The input is not a valid URL."

    tool_data = {
        "prompt": prompt,
        "command": "save_url",
        "payload": {
            "url": url
        }
    }

    return json.dumps(tool_data)

def journaling_topic(prompt:str, topic: str) -> str:
    """
    Save a journaling topic to the idea list, to write about later.

    Args:
        prompt: Full input provided by the user, exactly as it was typed.
        topic: Topic to save, with any relevant details.

    Returns:
        JSON string with all the data.
    """

    tool_data = {
        "prompt": prompt,
            "command": "journaling_topic",
            "payload": {
            "topic": topic
        }
    }

    return json.dumps(tool_data)

def va_request(prompt:str, title:str, request: str) -> str:
    """
    Send a request to the VA with the given message. Use only if the input explicitly asks for a
    virtual assistant or VA. Use ONLY if the prompt includes the words "virtual assistant",
    "v assistant" or "VA".

    Args:
        prompt: Full input provided by the user, exactly as it was typed.
        title: Title of the request, used as a Trello card title. Keep it short.
        request: Request to send.

    Returns:
        JSON string with all the data.
    """

    tool_data = {
        "prompt": prompt,
        "command": "va_request",
        "payload": {
            "title": title,
            "request": request
        }
    }

    return json.dumps(tool_data)

