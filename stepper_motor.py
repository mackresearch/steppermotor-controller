import sys
import time
import select
    
def main():
    sys.stdout.write("stepper motor simulator started!\n")
    start_stepper_motor_sim()

def start_stepper_motor_sim():
    param1 = sys.argv[1]
    param2 = sys.argv[2]
    param3 = sys.argv[3]
    param4 = sys.argv[4]
    print(f"[stepper_motor.py] - starting stepper motor sim with params - {param1}, {param2}, {param3}, {param4}")
    
    # simulates the stepper motorrunning
    while True:
        sys.stdout.write("[stepper_motor.py] - simming stepper motor...\n")
        sys.stdout.flush()
        time.sleep(1)
        rlist, _, _ = select.select([sys.stdin], [], [], 0)
        if rlist:
            input_data = sys.stdin.readline().strip()
            if input_data == "leafgen_stop_command":
                # since we're listening to the stdout in the parent process we can't be writing to the stdout or else it'll throw an exception
                # sys.stdout.write(f"STOPPING STEPPER MOTOR\n")
                break
            else:
                sys.stdout.write(f"[stepper_motor.py] - SUCCESSFULLY RECEIVED NON-BLOCKING INPUT - {input_data}\n")
                sys.stdout.flush()

if __name__ == "__main__":
    main()
