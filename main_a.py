# client.py
import string
import socket
import json
import time
import sys
import random
#
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
#
from utils import remove_all_think_tags, single_node_step, safe_json_decode, display_messages_simple, Colors, Styles


config = None
with open('config_a.json') as f:
    config = json.load(f)

with open(config["prompt_path"], "r") as file:
    prompt_template = file.read()


# system message templates:
system_message_llm = SystemMessage(content=prompt_template)
human_template = """
Below is the current debate history.
{debate_history}
"""

human_prompt_template = ChatPromptTemplate.from_messages([
    ("system", "{system_message}"),
    ("human", human_template),
])


# Initialize the LLM
llm = ChatOllama(model=config["model_name"], temperature=config["temperature"], device_map=config["device_map"])
# llm = ChatOllama(model="deepseek-r1:1.5b", temperature=0.7, device_map="auto")
# llm = ChatOllama(model="deepseek-llm:latest", temperature=0.7, device_map="auto")
# llm = ChatOllama(model="gpt-oss:latest", temperature=0.7, device_map="auto")


class NodeAClient:
    def __init__(self, server_ip, port=9000):
        self.server_ip = server_ip
        self.port = port
        self.message_history = []

    def communicate(self, iterations=100):
        stop_discussion = False
        for i in range(iterations):
            if not stop_discussion:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.settimeout(10)
                        print(f"Connecting to {self.server_ip}:{self.port}...")
                        s.connect((self.server_ip, self.port))

                        # Generate new message
                        message_a, self.stop = single_node_step("A", self.message_history, system_message_llm, human_prompt_template, llm, verbose=False)
                        self.message_history += [message_a]

                        # Send JSON to Node B

                        if eval(config["pausing"]):
                            print("Press Enter to continue...")
                            input()  # Script will pause here until Enter is pressed

                        json_data = json.dumps(self.message_history, ensure_ascii=False)
                        s.send(json_data.encode('utf-8'))
                        # print(f"\nSent to Node B:\n {data_to_send}")
                        display_messages_simple(self.message_history, show_last_only=True, color=Colors.BLUE, style=Styles.BOLD)  # updated by me

                        # Receive response from Node B
                        response = s.recv(config["buffer_size"])

                        if response:
                            response_str = response.decode('utf-8')
                            try:
                                self.message_history = json.loads(response_str)
                                # print("\nRaw response:\n", self.message_history)
                                display_messages_simple(self.message_history, show_last_only=True, color=Colors.GREEN, style=Styles.BOLD)  # updated by the opponent
                                if 'DISCUSSION STOPS' in self.message_history[-1]:
                                    print("\nDISCUSSION STOPS, judge takes a word..")
                                    stop_discussion = True
                                    break

                            except json.JSONDecodeError as e:
                                print(f"Failed to parse JSON response: {e}")
                                print(f"Raw response was: {response_str}")
                        else:
                            print("No response received from server")

                        time.sleep(2)

                except socket.timeout:
                    print("Connection timeout, retrying...")
                except ConnectionRefusedError:
                    print("Connection refused, make sure server is running. Retrying in 3 seconds...")
                    time.sleep(3)
                except Exception as e:
                    print(f"Error: {e}, retrying in 3 seconds...")
                    time.sleep(3)
            else:
                return


if __name__ == "__main__":
    client = NodeAClient(config["host_b"], config["port_b"])
    client.communicate()
