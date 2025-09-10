# server.py
import socket
import json
import string
#
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
#
from utils import remove_all_think_tags, single_node_step, safe_json_decode, display_messages_simple, Colors, Styles
import time


config = None
with open('config_b.json') as f:
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


class NodeBServer:
    def __init__(self, host='0.0.0.0', port=9000):
        self.host = host
        self.port = port
        self.message_history = []

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(5)
            print(f"Node B server started on {self.host}:{self.port}")

            while True:
                conn, addr = s.accept()
                print(f"Connection established with {addr}")
                with conn:
                    try:
                        # Receive data from opponent
                        data = conn.recv(config["buffer_size"]).decode('utf-8')  # Larger buffer for big messages
                        if data:
                            self.message_history = json.loads(data)  # history updated by opponent
                            # print(f"Received {len(received_data)} messages")
                            display_messages_simple(self.message_history, show_last_only=True, color=Colors.BLUE, style=Styles.BOLD)  # opponents' message
                            # Generate response message with rich text
                            message_b, self.stop = single_node_step("B", self.message_history, system_message_llm, human_prompt_template, llm, verbose=False)
                            self.message_history += [message_b]  # update history by me
                            display_messages_simple(self.message_history, show_last_only=True, color=Colors.GREEN, style=Styles.BOLD)  # my message

                            stop_discussion = False
                            if not "CONTINUE DEBATE" in self.message_history[-1] and not "CONTINUE DEBATE" in self.message_history[-2]:
                                self.message_history[-1] = self.message_history[-1] + ' DISCUSSION STOPS'
                                print("\nDISCUSSION STOPS, judge takes a word..")
                                stop_discussion = True

                            # Send JSON response to opponent
                            if eval(config["pausing"]):
                                print("Press Enter to continue...")
                                input()  # Script will pause here until Enter is pressed

                            response_json = json.dumps(self.message_history, ensure_ascii=False)
                            conn.send(response_json.encode('utf-8'))
                            # print("Response sent successfully")
                            if stop_discussion:
                                return self.message_history
                        else:
                            print("Received empty data")

                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
                    except Exception as e:
                        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    server = NodeBServer(port=config["my_port"])
    message_history = server.start_server()

    # sent message_history to judgement
    host_c = config["host_c"]
    port_c = config["port_c"]
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10)
            print(f"Connecting to C: {host_c}:{port_c}...")
            s.connect((host_c, port_c))

            # Send JSON to Node B
            json_data = json.dumps(message_history, ensure_ascii=False)
            s.send(json_data.encode('utf-8'))
            # print(f"\nSent to Node C:\n {data_to_send}")
            # display_messages_simple(message_history, show_last_only=True)

            # Receive response from Node C
            response = s.recv(config["buffer_size"])

            if response:
                response_str = response.decode('utf-8')
                try:
                    message_history = json.loads(response_str)
                    # print("\nRaw response:\n", self.message_history)
                    display_messages_simple(message_history, show_last_only=True, color=Colors.RED, style=Styles.BOLD)  # updated by judge

                except json.JSONDecodeError as e:
                    print(f"Failed to parse JSON response: {e}")
                    print(f"Raw response was: {response_str}")
            else:
                print("No response received from server")

            time.sleep(2)

    except socket.timeout:
        print("Connection timeout, retrying...")
    except ConnectionRefusedError:
        print("Connection refused, make sure server C is running. Retrying in 3 seconds...")
        time.sleep(3)
    except Exception as e:
        print(f"Error: {e}, retrying in 3 seconds...")
        time.sleep(3)
