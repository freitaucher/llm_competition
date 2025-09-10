import re
import json
from io import BytesIO


class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    BLUE = "\033[94m"
    MAGENTA = "\u001b[35m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"


class Styles:
    BOLD = "\u001b[1m"
    UNDERLINE = "\u001b[4m"
    RESET = "\033[0m"


def print_fancy(text, color, style):
    print(f"{color}{style}{text}{Colors.RESET}")


def display_messages_simple(messages_list, show_last_only=False, color=Colors.RESET, style=""):
    """Display list of messages with basic formatting"""
    for i, message in enumerate(messages_list, 1):
        if show_last_only:
            if i == len(messages_list):
                print(f"{color}{style}\nMessage {i}:{Colors.RESET}")
                print_fancy("-" * 40, color, style)
                print_fancy(message, color, style)
                print()  # Empty line between messages
        else:
            print(f"{color}\nMessage {i}:{Colors.RESET}")
            print_fancy("-" * 40, color, style)
            print_fancy(message, color, style)
            print()  # Empty line between messages


def remove_all_think_tags(text):
    pattern = r'<think>.*?<\/think>'
    return re.sub(pattern, '', text, flags=re.DOTALL)


def safe_json_decode(data_bytes):
    """Safely decode JSON data with error handling"""
    try:
        # Try UTF-8 first
        json_string = data_bytes.decode('utf-8')
        return json.loads(json_string)
    except UnicodeDecodeError:
        try:
            # Try other common encodings
            for encoding in ['latin-1', 'iso-8859-1', 'cp1252']:
                try:
                    json_string = data_bytes.decode(encoding)
                    return json.loads(json_string)
                except (UnicodeDecodeError, json.JSONDecodeError):
                    continue
            raise ValueError("Could not decode data with any supported encoding")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")


def single_node_step(name, debate_history, system_message, human_prompt_template, llm, verbose=True):
    if verbose:
        print("-----------------------------------------------------------------------")
        print("\n["+name+"'s Turn]")
    # prompt for А/B: its system message + debate history
    if debate_history == []:
        debate_history = ["Debates start."]
    prompt_for_node = human_prompt_template.format_messages(
        system_message=system_message.content,
        debate_history=debate_history[:]  # "\n".join(debate_history[-4:])
    )
    response = llm.invoke(prompt_for_node)
    # response_filtered = name+': ' + remove_all_think_tags(response.content)
    response_filtered = remove_all_think_tags(response.content)
    # debate_history.append(response_filtered)
    if verbose:
        print(response_filtered)
    stop = False
    if "CALL FOR JUDGMENT" in response_filtered or not "COMMAND" in response_filtered:
        stop = True

    return response_filtered, stop
