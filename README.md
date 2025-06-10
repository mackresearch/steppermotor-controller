# steppermotor-controller

### Start Up Instructions
When you are on the Pi you will need to navigate to `/home/admin/steppermotor/steppermotor_venv` to activate the virtual Python environment. Then come back to this directory to start the application.

To start a virtual environment use the following command 
> `source venv/bin/activate`

### Stepper Motor Specifics
One step = 1.8 degrees

Full rotation (360 degrees) = 200 steps

<b>Stepper Motor API Documentation</b> -

https://docs.circuitpython.org/projects/motorkit/en/latest/

https://github.com/adafruit/Adafruit_CircuitPython_MotorKit?tab=readme-ov-file

https://docs.circuitpython.org/projects/motor/en/latest/api.html#adafruit-motor-stepper

<b> How To Turn On Camera </b> -
https://docs.arducam.com/UVC-Camera/Quick-Start-Guide%28USB2%29/Linux/#install-v4l-utility-packages


### Stepper Motor Parameter 
<b>step_time</b>: amount of time the leaf will wait before it moves into its downstroke position

<b>loop_limit</b>: amount of time it performs a full upstroke and downstroke

<b>upstroke_count</b>: amount of steps to move the leaf upwards

<b>downstroke_count</b>: amount of steps to move the leaf downwards

<b>upstroke_wait_time</b>: duration in which the leaf waits after it has moved upwards

<b>downstroke_wait_time</b>: duration in which the leaf waits after is has moved downwards

