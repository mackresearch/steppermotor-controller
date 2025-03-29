import tkinter as tk
import socket
import json

HOST = "localhost"
PORT = 12345

# Create and maintain a persistent socket connection
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((HOST, PORT))

def send_input():
    data = {
        "upward_strokes": entry1.get(),
        "upward_strokes_wait_time": entry2.get(),
        "downward_strokes": entry3.get(),
        "downward_strokes_wait_time": entry4.get(),
        "cycle_interation_count": entry5
    }

    message = json.dumps(data)
    client_socket.sendall(message.encode())  # Send data through the open connection
    print(f"Sent: {message}")

# GUI Setup
root = tk.Tk()
root.title("Stepper Motor Controller")
root.geometry("400x300")

tk.Label(root, text="Upward Strokes:").pack()
entry1 = tk.Entry(root)
entry1.pack(expand=True)

tk.Label(root, text="Upward Stroke Wait Time:").pack()
entry2 = tk.Entry(root)
entry2.pack(expand=True)

tk.Label(root, text="Downwar Strokes:").pack()
entry3 = tk.Entry(root)
entry3.pack(expand=True)

tk.Label(root, text="Downward Stroke Wait Time:").pack()
entry4 = tk.Entry(root)
entry4.pack(expand=True)

tk.Label(root, text="Cycle Iteration Count:").pack()
entry5 = tk.Entry(root)
entry5.pack(expand=True)

tk.Button(root, text="Submit", command=send_input).pack(pady=(10, 20))

root.mainloop()

# Close the connection when GUI closes
client_socket.close()