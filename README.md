# steppermotor-controller

### Start Up Instructions
A Python virtual environment (venv) will need to be spun up for this application to run successfully. To spin up the venv that corresponds to this app, run this command in a terminal session `source /home/admin/steppermotor/steppermotor_venv/bin/activate`

After the virtual environment is has been spun up, go to  `/home/admin/steppermotor/stepper_motor_controller_gui` to run the application by running `python main.py`

### Stepper Motor Specifics
One step = 1.8 degrees

Full rotation (360 degrees) = 200 steps

<b>Stepper Motor API Documentation</b> -

https://docs.circuitpython.org/projects/motorkit/en/latest/

https://github.com/adafruit/Adafruit_CircuitPython_MotorKit?tab=readme-ov-file

https://docs.circuitpython.org/projects/motor/en/latest/api.html#adafruit-motor-stepper

<b> How To Turn On Camera </b> -
To turn on the camera run the following command in its own separate terminal session  `qv4l2`

> The command is Q V 4 L 2, the l is not a capital 'i', its a lowercase L

https://docs.arducam.com/UVC-Camera/Quick-Start-Guide%28USB2%29/Linux/#install-v4l-utility-packages



### Stepper Motor Parameter 
<b>step_time</b>: amount of time the leaf will wait before it moves into its downstroke position

<b>loop_limit</b>: amount of time it performs a full upstroke and downstroke

<b>upstroke_count</b>: amount of steps to move the leaf upwards

<b>downstroke_count</b>: amount of steps to move the leaf downwards

<b>upstroke_wait_time</b>: duration in which the leaf waits after it has moved upwards

<b>downstroke_wait_time</b>: duration in which the leaf waits after is has moved downwards

