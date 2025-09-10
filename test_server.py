# server.py
import socket
import json
import string


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


class NodeBServer:
    def __init__(self, host='0.0.0.0', port=9000):
        self.host = host
        self.port = port
        self.message_history = []

    def generate_message_b(self):
        # Multi-line message with paragraphs
        return f"""Message from Node B - Response #{len(self.message_history)//2 + 1}

This is the first paragraph of my response.
It contains multiple lines and demonstrates
how we can handle rich text content.

Here's another paragraph with empty lines above and below.

And a final paragraph to complete the message.
"""

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
                        # Receive data
                        data = conn.recv(8192).decode('utf-8')  # Larger buffer for big messages
                        if data:
                            received_data = json.loads(data)
                            print(f"Received {len(received_data)} messages")

                            # Generate response message with rich text
                            message_b = self.generate_message_b()
                            response = received_data + [message_b]
                            self.message_history = response

                            # Send JSON response
                            response_json = json.dumps(response, ensure_ascii=False)
                            conn.send(response_json.encode('utf-8'))
                            print("Response sent successfully")
                        else:
                            print("Received empty data")

                    except json.JSONDecodeError as e:
                        print(f"JSON decode error: {e}")
                    except Exception as e:
                        print(f"Unexpected error: {e}")


if __name__ == "__main__":
    server = NodeBServer(port=9000)
    server.start_server()
