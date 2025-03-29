# steppermotor-controller

### Start Up Instructions
The server needs to be started before the client starts or else the client will have nothing to connect to and will fail.

To start up the server run the following command -
> python server.py

Open up another terminal instance and run the following command to start up the client -
> python client.py

### Start Up Virtual Python Env (venv)
1. Open up steppermotor folder (project folder)
2. Open steppermotor_venv folder
3. Run the following command -
> source bin/activate

Now you can start up the app using the python command

### Stepper Motor Specifics
One step = 1.8 degrees

Full rotation (360 degrees) = 200 steps

<b>Stepper Motor API Documentation</b> -

https://docs.circuitpython.org/projects/motorkit/en/latest/

https://github.com/adafruit/Adafruit_CircuitPython_MotorKit?tab=readme-ov-file

https://docs.circuitpython.org/projects/motor/en/latest/api.html#adafruit-motor-stepper


### Stepper Motor Parameter 
<b>step_time</b>: amount of time the leaf will wait before it moves into its downstroke position

<b>loop_limit</b>: amount of time it performs a full upstroke and downstroke

<b>upstroke_count</b>: amount of steps to move the leaf upwards

<b>downstroke_count</b>: amount of steps to move the leaf downwards

<b>upstroke_wait_time</b>: duration in which the leaf waits after it has moved upwards

<b>downstroke_wait_time</b>: duration in which the leaf waits after is has moved downwards