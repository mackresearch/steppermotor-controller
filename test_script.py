from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import board
import time

motorkit = MotorKit(i2c=board.I2C())

print("starting stepper motor")
for i in range (475):
    motorkit.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.SINGLE)
    time.sleep(.01)

motorkit.stepper2.release()