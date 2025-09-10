# server.py
import socket
import json
import string
#
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
#
from utils import remove_all_think_tags, single_node_step, safe_json_decode, display_messages_simple

config = None
with open('config_c.json') as f:
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


class NodeCServer:
    def __init__(self, host='0.0.0.0', port=9001):
        self.host = host
        self.port = port
        self.message_history = []

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.host, self.port))
            s.listen(5)
            print(f"Node C server started on {self.host}:{self.port}")

            while True:
                conn, addr = s.accept()
                print(f"Connection established with {addr}")
                with conn:
                    try:
                        # Receive data
                        data = conn.recv(config["buffer_size"]).decode('utf-8')  # Larger buffer for big messages
                        if data:
                            self.message_history = json.loads(data)
                            # print(f"Received {len(received_data)} messages")
                            # display_messages_simple(self.message_history, show_last_only=True)  # opponents' message
                            # Generate response message with rich text
                            message_b, self.stop = single_node_step("C", self.message_history, system_message_llm, human_prompt_template, llm, verbose=False)
                            self.message_history += [message_b]  # update history by me
                            display_messages_simple(self.message_history, show_last_only=True)  # my verdict

                            # Send JSON response
                            response_json = json.dumps(self.message_history, ensure_ascii=False)
                            conn.send(response_json.encode('utf-8'))
                            # print("Response sent successfully")
                        else:
                            print("Received empty data")

                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
                    except Exception as e:
                        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    server = NodeCServer(port=config["my_port"])
    server.start_server()
