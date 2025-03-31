import os
import socket
import threading

HOST = "localhost"
PORT = 8080
DOCUMENT_ROOT = "./www"


def handle_request(client_socket):
    request = ""
    try:
        # while True:
        request = client_socket.recv(1024).decode()
        # 2. get headers
        headers = request.split("\r\n")
        # 3. split headers to methods
        method, path, protocol = headers[0].split(" ")
        # 4. give back response
        if method in ["GET", "HEAD"]:
            if path == "/":
                path = os.path.join(DOCUMENT_ROOT, "index.html")
            if os.path.exists(path):
                with open(path, "rb") as f:
                    content = f.read()
                response = (
                    f"{protocol} 200 OK\r\nContent-Length: {len(content)}\r\n".encode()
                )
                if method == "GET":
                    response = response + content
            else:
                response = b"HTTP/1.1 404 Not Found\r\nFile Not Found"

            client_socket.sendall(response)
    finally:
        client_socket.close()


def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (HOST, PORT)
    server_socket.bind(server_address)
    server_socket.listen(5)  # Allows up to 5 queued connections
    print(f"Server listening on {server_address}")
    try:
        while True:
            client_socket, _ = server_socket.accept()
            client_thread = threading.Thread(
                target=handle_request, args=(client_socket,)
            )
            client_thread.start()
    finally:
        server_socket.close()


if __name__ == "__main__":
    start_server()
