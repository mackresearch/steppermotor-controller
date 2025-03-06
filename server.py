import socket
import json
import subprocess
import os

HOST = "localhost"  
PORT = 12345        

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(1)  # Allow only one client for now
worker_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "worker.py")

print("Waiting for a connection...")
conn, addr = server_socket.accept()
print(f"Connected to {addr}")

while True:
    data = conn.recv(1024).decode()  # Keep receiving data from the client
    if not data:
        print("Client disconnected. Waiting for a new connection...")
        conn, addr = server_socket.accept()  # Wait for a new connection
        print(f"Connected to {addr}")
        continue

    try:
        received_data = json.loads(data)

        print(f"Received data: {received_data}")

        # Process fields
        command1 = received_data.get("step_distance", "")
        command2 = received_data.get("step_time", "")
        command3 = received_data.get("step_limit", "")
        command4 = received_data.get("step_count", "")

        print(f"Processing Command 1: {command1}")
        print(f"Processing Command 2: {command2}")
        print(f"Processing Command 3: {command3}")
        print(f"Processing Command 3: {command4}")

        subprocess.run(["python", worker_path, json.dumps(received_data)], shell=True)

    except json.JSONDecodeError:
        print("Invalid JSON received!")

conn.close()  # This only happens if the script is stopped
