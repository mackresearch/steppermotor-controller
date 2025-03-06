import time
import board

kit = MotorKit(i2c=board.I2C())

# These two variables define how many steps the motor should take, how long it will take between steps, and how many times it should loop.
step_distance = 200
step_time = 5
loop_limit = 3
loop_count = 0

#The motor turns from the base position to an up-stroke position. Then it waits while the leaf pulls upwards.
for i in range(step_distance/2):
    print('looping through forward step')
    kit.stepper2.onestep()
    time.sleep(0.01)
time.sleep(step_time)

#the while loop executes a cycle as many times as set via loop_limit
while loop_limit > loop_count:
  #The motor turns from an up-stroke position to a down-stroke position. Then it waits while the leaf goes downwards.
  for i in range(step_distance):
      print('looping through backward step')
      kit.stepper2.onestep(direction=kit.BACKWARDS)
      time.sleep(0.01)
  time.sleep(step_time)
  
  #The motor turns from a down-stroke position to an up-stroke position. Then it waits while the leaf goes upwards.
  for i in range(step_distance):
      print('looping through forward step')
      kit.stepper2.onestep()
      time.sleep(0.01)
  time.sleep(step_time)
  loop_count += 1

#after the loop has completed, the motor turns from an up-stroke position to the base position, then exits the program.
for i in range(step_distance/2):
    print('looping through backward step')
    kit.stepper2.onestep(direction=kit.BACKWARDS)
    time.sleep(0.01)    
kit.stepper2.release()