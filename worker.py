import sys
import json
import time

def process_data(data):
    print(f"Worker Script Received: {data}")

def sim_app_run():
    while(True):
        print("simming app run...")
        time.sleep(10)

if __name__ == "__main__":
    # Read JSON input from the command-line arguments
    if len(sys.argv) > 1:
        try:
            data = json.loads(sys.argv[1])  # Convert argument to dictionary; i think this is the entire dataset that is passed from the client
            print("data has reached worker script...")
            process_data(data)
            sim_app_run()

        except json.JSONDecodeError:
            print("Error: Invalid JSON input")
    else:
        print("No data received!")
