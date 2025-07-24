from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import board

motorkit = MotorKit(i2c=board.I2C())

print("starting stepper motor")

for i in range (200):
    motorkit.stepper1.onestep(style=stepper.SINGLE)

motorkit.stepper1.release()