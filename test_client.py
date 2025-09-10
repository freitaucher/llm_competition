# client.py
import string
import socket
import json
import time
import sys
import random


def display_messages_simple(messages_list):
    """Display list of messages with basic formatting"""
    # print("=" * 60)
    # print("CONVERSATION HISTORY")
    # print("=" * 60)

    for i, message in enumerate(messages_list, 1):
        print(f"\nMessage {i}:")
        print("-" * 40)
        print(message)
        print()  # Empty line between messages


def randomStringwithDigitsAndSymbols(stringLength=10):
    """Generate a random string of letters, digits and special characters """
    password_characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(password_characters) for i in range(stringLength))


class NodeAClient:
    def __init__(self, server_ip, port=9000):
        self.server_ip = server_ip
        self.port = port
        self.message_history = []

    def generate_message_a(self):
        # Rich text message with paragraphs and formatting
        return f"""

        Message from Node A - Transmission
        Dear Node B,

        This message demonstrates the capability to handle
        multi-line text content with proper formatting.

        We can include:
        - Bullet points
        - Numbered lists
        - Special characters: !@#$%^&*()|\/''"
        - And even emoji if supported: 😊

        Sincerely,
        Node A
        """

    def communicate(self, iterations=2):
        for i in range(iterations):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(10)
                    print(f"Connecting to {self.server_ip}:{self.port}...")
                    s.connect((self.server_ip, self.port))

                    # Generate new message
                    message_a = self.generate_message_a()
                    data_to_send = self.message_history + [message_a]

                    # Send JSON to Node B
                    json_data = json.dumps(data_to_send, ensure_ascii=False)
                    s.send(json_data.encode('utf-8'))
                    print(f"\nSent to Node B:\n {data_to_send}")
                    display_messages_simple(data_to_send)

                    # Receive response from Node B
                    response = s.recv(16384)
                    if response:
                        response_str = response.decode('utf-8')
                        try:
                            self.message_history = json.loads(response_str)
                            print("\nRaw response:\n", self.message_history)
                            display_messages_simple(self.message_history)
                        except json.JSONDecodeError as e:
                            print(f"Failed to parse JSON response: {e}")
                            print(f"Raw response was: {response_str}")
                    else:
                        print("No response received from server")

                    # print(f"\n\n--- Completed iteration {i+1} ---\n\n")
                    time.sleep(2)

            except socket.timeout:
                print("Connection timeout, retrying...")
            except ConnectionRefusedError:
                print("Connection refused, make sure server is running. Retrying in 3 seconds...")
                time.sleep(3)
            except Exception as e:
                print(f"Error: {e}, retrying in 3 seconds...")
                time.sleep(3)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 client.py <server_ip>")
        print("Example: python3 client.py 192.168.2.113")
        sys.exit(1)

    client = NodeAClient(sys.argv[1], 9000)
    client.communicate()
