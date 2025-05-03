import sys
import asyncio

async def main():
    sys.stdout.write("stepper motor simulator started!\n")
    sys.stdout.flush()

    await start_stepper_motor_sim()

    print("[stepper_motor.py] - shutdown complete")
    sys.exit(0)

async def start_stepper_motor_sim():
    param1, param2, param3, param4 = sys.argv[1:5]
    print(f"[stepper_motor.py] - starting stepper motor sim with params - {param1}, {param2}, {param3}, {param4}")
    sys.stdout.flush()

    shutdown_event = asyncio.Event()
    async with asyncio.TaskGroup() as tg:
        tg.create_task(simulate_motor(shutdown_event))
        tg.create_task(watch_for_commands_threaded(shutdown_event))
    print("[stepper_motor.py] - all child tasks complete")


async def simulate_motor(shutdown_event):
    while not shutdown_event.is_set():
        sys.stdout.write("[stepper_motor.py] - simming stepper motor...\n")
        sys.stdout.flush()
        await asyncio.sleep(1)  # simulate motor activity

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
