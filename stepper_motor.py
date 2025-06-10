import sys
import asyncio
import json
import constants
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import board

motorkit = MotorKit(i2c=board.I2C())
logger_identifer = "[stepper-motor.py] -"
async def main():
    sys.stdout.write(f"{logger_identifer} stepper motor script initated!\n")

    await parameter_listener()

    print(f"{logger_identifer} - shutdown complete")
    sys.exit(0)

def build_params_string(params_list):
    params_str = ""
    for p in params_list:
        p = p + ", "
        params_str += p
    return params_str

def map_parameters(params_list):
    # need to write check to make sure the two arrays are the same length or else throw some fatal error
    keys_list = [
        constants.STEP_TIME,
        constants.ITERATIONS,
        constants.UPSTROKE_STEPS,
        constants.DOWNSTROKE_STEPS,
        constants.UPSTROKE_DELAY,
        constants.DOWNSTROKE_DELAY
    ]

    return {key: int(value) for key, value in zip(keys_list, params_list)}

async def parameter_listener():
    sys.stdout.write(f"{logger_identifer} input received: {build_params_string(json.loads(sys.argv[1]))}\n")
    params_map = map_parameters(json.loads(sys.argv[1]))

    shutdown_event = asyncio.Event()
    async with asyncio.TaskGroup() as tg:
        tg.create_task(start_stepper_motor(shutdown_event, params_map))
        tg.create_task(watch_for_commands_threaded(shutdown_event))
   
    print(f"{logger_identifer} all scheduled tasks complete")

async def start_stepper_motor(shutdown_event: asyncio.Event, parameters_map: dict[str, int]):
    current_iteration = 0
    sys.stdout.write(f"{logger_identifer} starting stepper motor\n"
                     f"step time: {parameters_map.get(constants.STEP_TIME)}\n"
                     f"iterations: {parameters_map.get(constants.ITERATIONS)}\n")
       
    while current_iteration < parameters_map.get(constants.ITERATIONS) and not shutdown_event.is_set():
        current_iteration += 1
        # MOVES STEPPER MOTOR UPWARDS
            # need to determine if this is BACKWARDS/FORWARDS
        sys.stdout.write(f"{logger_identifer} start of upward strokes\n")
        for i in range(parameters_map.get(constants.UPSTROKE_STEPS)):
            sys.stdout.write(f"{logger_identifer} upstroke step count: {i}\n")
            motorkit.stepper2.onestep(style=stepper.DOUBLE)
            # needed to give the stepper motor time to move
            await asyncio.sleep(.5)

        # DELAY BEFORE MOVING FROM UPWARDS -> DOWNWARDS
        sys.stdout.write(f"{logger_identifer} waiting for {parameters_map.get(constants.DOWNSTROKE_DELAY)} secs before moving downwards\n")
        await asyncio.sleep(parameters_map.get(constants.DOWNSTROKE_DELAY))

        # MOVES STEPPER MOTOR DOWNWARDS
            # need to determine if thi is BACKWARDS/FORWARDS
        sys.stdout.write(f"{logger_identifer} start of downward strokes\n")
        for i in range(parameters_map.get(constants.DOWNSTROKE_STEPS)):
            sys.stdout.write(f"{logger_identifer} downstroke step count: {i}\n")
            motorkit.stepper2.onestep(style=stepper.DOUBLE, direction=stepper.BACKWARD)
            # needed to give the stepper motor time to move
            await asyncio.sleep(.5)

    # TODO: write logic to set the shutdown event and tell the parent process that this child process is complete
    # so it it can reset the UI widgets
    # secondly, break this out into a separate function
    sys.stdout.write(f"{logger_identifer} reached max amount of iterations. stepper motor is resetting now...\n")
    shutdown_event.set()
    print(f"{logger_identifer} set shutdown_event successfully", flush=True)

def listen(shutdown_event: asyncio.Event):
    while True:
        line = sys.stdin.readline()
        if not line:
            continue
        command = line.strip()
        if command == "leafgen_stop_command":
            print(f"{logger_identifer} leafgen_stop_command received", flush=True)
            shutdown_event.set()
            break
        else:
            print(f"[stepper_motor.py] - received param update: {command}", flush=True)

async def watch_for_commands_threaded(shutdown_event):
    loop = asyncio.get_running_loop()
    # run this blocking function in a threadpool and return a future i can wait on
    # Waits for the result of the thread using a Future — when the thread finishes, the event loop picks up the result and resumes the await.
    await loop.run_in_executor(None, listen, shutdown_event)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        sys.stderr.write(f"{logger_identifer} FATAL ERROR: {e}\n")
        sys.exit(1)