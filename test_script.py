from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import board
import time

motorkit = MotorKit(i2c=board.I2C())
print("starting stepper motor")
for i in range(300):
    motorkit.stepper2.onestep()

time.sleep(2)

for i in range (475):
    motorkit.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)
    time.sleep(.01)

time.sleep(2)

for i in range(250):
    motorkit.stepper2.onestep(direction=stepper.FORWARD, style=stepper.MICROSTEP)


motorkit.stepper2.release()