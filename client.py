import tkinter as tk
import socket
import json

HOST = "localhost"
PORT = 12345

# Create and maintain a persistent socket connection
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

def send_input(data):
    message = json.dumps(data)
    client_socket.sendall(message.encode())  # Send data through the open connection
    print(f"Sent: {message}")

def reset(data):
    data["reset"] = True
    send_input(data)
    

# GUI Setup
root = tk.Tk()
root.title("Stepper Motor Controller")
root.geometry("400x300")

tk.Label(root, text="Upward Strokes:").pack()
upward_stroke = tk.Entry(root)
upward_stroke.pack(expand=True)

tk.Label(root, text="Upward Stroke Wait Time:").pack()
upward_stroke_wait_time = tk.Entry(root)
upward_stroke_wait_time.pack(expand=True)

tk.Label(root, text="Downward Strokes:").pack()
downward_stroke = tk.Entry(root)
downward_stroke.pack(expand=True)

tk.Label(root, text="Downward Stroke Wait Time:").pack()
downward_stroke_wait_time = tk.Entry(root)
downward_stroke_wait_time.pack(expand=True)

tk.Label(root, text="Cycle Iteration Count:").pack()
cycle_interations = tk.Entry(root)
cycle_interations.pack(expand=True)

data = {
        "upward_strokes": upward_stroke.get(),
        "upward_strokes_wait_time": upward_stroke_wait_time.get(),
        "downward_strokes": downward_stroke.get(),
        "downward_strokes_wait_time": downward_stroke_wait_time.get(),
        "cycle_interation_count": cycle_interations.get(),
        "reset": False
    }

tk.Button(root, text="Submit", command=lambda: send_input(data)).pack(pady=(10, 20))
tk.Button(root, text="Reset", command=lambda: reset(data)).pack(pady=(10, 20))

root.mainloop()

# Close the connection when GUI closes
client_socket.close()