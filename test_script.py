from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import board
import time

motorkit = MotorKit(i2c=board.I2C())

print("starting stepper motor")
for i in range(1200):
    motorkit.stepper2.onestep(style=stepper.DOUBLE)

time.sleep(5)

print("starting stepper motor")
for i in range(1200):
    motorkit.stepper2.onestep(direction=stepper.BACKWARD, style=stepper.DOUBLE)



motorkit.stepper2.release()