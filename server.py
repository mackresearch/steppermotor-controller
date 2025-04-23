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
process = None

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
        print(f"data received by server - reset value is: {received_data.get("reset")}")
        # check reset switch
        if received_data.get("reset") == True:
            print("terminating script now...")
            process.terminate()
            stdout, stderr = process.communicate()
            process.wait()
            print(f"process finished with exit code: {process.poll()}")
            print("standard output:")
            print(stdout.decode())
            print("standard error:")
            print(stderr.decode())
            print("successfully terminated process") if process.poll() is None else print("issue with terminating process")
        else:
            print(f"Received data: {received_data}")

            # Process fields
            command1 = received_data.get("upward_strokes", "")
            command2 = received_data.get("upward_strokes_wait_time", "")
            command3 = received_data.get("downward_strokes", "")
            command4 = received_data.get("downward_strokes_wait_time", "")
            command5 = received_data.get("cycle_interation_count", "")

            process = subprocess.Popen(["python",worker_path, json.dumps(received_data)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    except json.JSONDecodeError:
        print("Invalid JSON received!")

conn.close()  # This only happens if the script is stopped
