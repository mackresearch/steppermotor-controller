import sys
import asyncio
import board
from adafruit_motorkit import MotorKit
from adafruit_motor import stepper

kit = MotorKit(i2c=board.I2C())

async def main():
    sys.stdout.write("stepper motor simulator started!\n")
    sys.stdout.flush()

    await prep_stepper_motor()

    print("[stepper_motor.py] - shutdown complete")
    sys.exit(0)

async def prep_stepper_motor():
    step_distance, step_time, loop_limit, upstroke_count = sys.argv[1:5]
    print(f"[stepper_motor.py] - starting stepper motor sim with params - {step_distance}, {step_time}, {loop_limit}, {upstroke_count}")
    sys.stdout.flush()

    shutdown_event = asyncio.Event()
    async with asyncio.TaskGroup() as tg:
        tg.create_task(start_stepper_motor(shutdown_event))
        tg.create_task(watch_for_commands_threaded(shutdown_event))
    print("[stepper_motor.py] - all child tasks complete")


async def simulate_motor(shutdown_event):
    while not shutdown_event.is_set():
        sys.stdout.write("[stepper_motor.py] - simming stepper motor...\n")
        sys.stdout.flush()
        await asyncio.sleep(1)  # simulate motor activity

async def start_stepper_motor(shutdown_event):
    sys.stdout.write("[stepper_motor.py] - init start_stepper_motor\n")

    step_distance, step_time, loop_limit, upstroke_count = sys.argv[1:5]
    loop_count = 0

    while not shutdown_event.is_set():
        for i in range(loop_limit):
            loop_count += 1
            kit.stepper2.onestep(style=stepper.DOUBLE)
            sys.stdout.write(f"loop count: {loop_count}\n")
            await asyncio.sleep(.05)
        sys.stdout.flush("[stepper_motor.py] - loop limit has been reached\n")


def listen(shutdown_event: asyncio.Event):
    while True:
        line = sys.stdin.readline()
        if not line:
            continue
        command = line.strip()
        if command == "leafgen_stop_command":
            print("[stepper_motor.py] - leafgen_stop_command received", flush=True)
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
    asyncio.run(main())
