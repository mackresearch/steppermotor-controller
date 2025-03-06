import sys
import json

def process_data(data):
    print(f"Worker Script Received: {data}")
    print(f"Step Count is:  {data.get("step_count")}")

if __name__ == "__main__":
    # Read JSON input from the command-line arguments
    if len(sys.argv) > 1:
        try:
            data = json.loads(sys.argv[1])  # Convert argument to dictionary
            process_data(data)
        except json.JSONDecodeError:
            print("Error: Invalid JSON input")
    else:
        print("No data received!")
