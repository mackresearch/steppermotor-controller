# imports necessary libz
import json
import math
import sys

# init variables
upstroke_count = None
upstroke_wait_time = None
downstroke_count = None
downstroke_wait_time = None
loop_limit = math.inf   # loop indefinitley if no value is passed
interation_count = None

# sets the desired values to the leaf's required parameters
def process_data(data):
    upstroke_count = data.get("upward_strokes")
    upstroke_wait_time = data.get("upward_strokes_wait_time")
    downstroke_count = upstroke_count + data.get("downward_strokes")
    downstroke_wait_time = data.get("downward_strokes_wait_time")
    loop_limit = data.get("cycle_interation_count")

def simAppRun():
    while(True):
        print("simming app run...")

# this is used when the script is executed directly rather than being imported as a modul.it specifies that the following code should execute only if the script is executed directly
# when the script is executed directly the special __name__ variable in Python sets this value to "__main__"
if __name__ == "__main__":
    # Read JSON input from the command-line arguments
    # sys.argv is a list that contains the command-line arguments passed to the script
    # the first element (sys.argv[0]) is always the script name
    if len(sys.argv) > 1:
        try:
            data = json.loads(sys.argv[1])  # convert argument to dictionary
        except json.JSONDecodeError:
            print("Error: Invalid JSON input")
    else:
        print("No data received...")
        sys.exit()

    process_data(data)
    simAppRun()

    while interation_count  < loop_limit:
        print("executing process loop")
        interation_count += 1

sys.exit()