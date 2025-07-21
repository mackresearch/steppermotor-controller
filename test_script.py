from adafruit_motorkit import MotorKit
from adafruit_motor import stepper
import board

motorkit = MotorKit(i2c=board.I2C())

for i in range (200):
    motorkit.stepper2.onestep(style=stepper.SINGLE)

motorkit.stepper2.release()