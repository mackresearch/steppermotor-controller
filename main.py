import sys
import asyncio
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QMessageBox, QLabel
)
from PyQt6.QtGui import QIntValidator
from qasync import QEventLoop, asyncSlot
from asyncio.subprocess import create_subprocess_exec
from pathlib import Path
import json
import constants

SCRIPT_PATH = Path("stepper_motor.py")

# create gui
class SMControllerMainWindow(QMainWindow):  # we're extending the QMainWindow obj here and calling it SMControllerMainWindow
    def __init__(self):
        super().__init__()
        self.script_log_identifier = "[main.py] - "
        self.stepper_motor_process = None
        self.read_child_output_task = None
        self.stop_command = "leafgen_stop_command"
        self.widget_width = 300
        self.setWindowTitle("LeafGen Stepper Motor Controller")
        self.resize(300, 600)
        self.ERR_LABEL_MSG = "invalid input. only numbers are allowed."

        # default placehodler text values
        # step time - time the leaf will wait before it switches from the upward stroke the downward stroke
        self.default_placeholder_text_step_time = "step time"
        # iterations - sets the amount of iterations for a full stroke (upstroke and downstroke)
        self.default_placeholder_text_iterations = "iterations"
        # upstroke steps - amount of steps to move the leaf upwards
        self.default_placeholder_text_upstroke_steps = "upstroke steps"
        # downstroke count - amount of steps to move the leaf downwards
        self.default_placeholder_text_downstroke_steps = "downstroke steps"
        # upstroke wait time - duration the leaf waits after it's moved upwards
        self.default_placeholder_text_upstroke_wait_time = "upstroke wait time"
        # downstroke wait time - duration the leaf waits after it's moved downwards
        self.default_placeholder_text_downstroke_wait_time = "downstroke wait time"

        # create output textbox that displays child stdout data
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setPlaceholderText("output...")

        # create labels
        self.label_step_time = QLabel("step time")
        self.label_iterations = QLabel("iterations")
        self.label_upstroke_steps = QLabel("upstroke steps")
        self.label_downstroke_steps = QLabel("downstroke steps")
        self.label_upstroke_wait_time = QLabel("upstroke wait time")
        self.label_downstroke_wait_time = QLabel("downstroke wait time")

        # create error msg labels
        self.err_label_step_time = QLabel(self.ERR_LABEL_MSG)
        self.err_label_step_time.setVisible(False)
        self.err_label_iterations = QLabel(self.ERR_LABEL_MSG)
        self.err_label_iterations.setVisible(False)
        self.err_label_upstroke_steps = QLabel(self.ERR_LABEL_MSG)
        self.err_label_upstroke_steps.setVisible(False)
        self.err_label_downstroke_steps = QLabel(self.ERR_LABEL_MSG)
        self.err_label_downstroke_steps.setVisible(False)
        self.err_label_upstroke_delay = QLabel(self.ERR_LABEL_MSG)
        self.err_label_upstroke_delay.setVisible(False)
        self.err_label_downstroke_delay = QLabel(self.ERR_LABEL_MSG)
        self.err_label_downstroke_delay.setVisible(False)

        # create user input fields
        self.input_step_time = QLineEdit()
        self.input_step_time.setObjectName(constants.STEP_TIME)
        self.input_step_time._connected_init_stepper_motor_slot = False
        self.input_step_time._connected_update_child_process_slot = False
        self.input_step_time.setPlaceholderText(self.default_placeholder_text_step_time)
        self.input_step_time.setValidator(QIntValidator())
        self.input_step_time.setFixedWidth(self.widget_width)
        self.input_step_time.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.input_iterations = QLineEdit()
        self.input_iterations.setObjectName(constants.ITERATIONS)
        self.input_iterations._connected_init_stepper_motor_slot = False
        self.input_iterations._connected_update_child_process_slot = False
        self.input_iterations.setPlaceholderText(self.default_placeholder_text_iterations)
        self.input_iterations.setValidator(QIntValidator())
        self.input_iterations.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_iterations.setFixedWidth(self.widget_width)

        self.input_upstroke_steps = QLineEdit()
        self.input_upstroke_steps.setObjectName(constants.UPSTROKE_STEPS)
        self.input_upstroke_steps._connected_init_stepper_motor_slot = False
        self.input_upstroke_steps._connected_update_child_process_slot = False
        self.input_upstroke_steps.setPlaceholderText(self.default_placeholder_text_upstroke_steps)
        self.input_upstroke_steps.setValidator(QIntValidator())
        self.input_upstroke_steps.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_upstroke_steps.setFixedWidth(self.widget_width)

        self.input_downstroke_steps = QLineEdit()
        self.input_downstroke_steps.setObjectName(constants.DOWNSTROKE_STEPS)
        self.input_downstroke_steps._connected_init_stepper_motor_slot = False
        self.input_downstroke_steps._connected_update_child_process_slot = False
        self.input_downstroke_steps.setPlaceholderText(self.default_placeholder_text_downstroke_steps)
        self.input_downstroke_steps.setValidator(QIntValidator())
        self.input_downstroke_steps.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_downstroke_steps.setFixedWidth(self.widget_width)

        self.input_upstroke_wait_time = QLineEdit()
        self.input_upstroke_wait_time.setObjectName(constants.UPSTROKE_DELAY)
        self.input_upstroke_wait_time._connected_init_stepper_motor_slot = False
        self.input_upstroke_wait_time._connected_update_child_process_slot = False
        self.input_upstroke_wait_time.setPlaceholderText(self.default_placeholder_text_upstroke_wait_time)
        self.input_upstroke_wait_time.setValidator(QIntValidator())
        self.input_upstroke_wait_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_upstroke_wait_time.setFixedWidth(self.widget_width)

        self.input_downstroke_wait_time = QLineEdit()
        self.input_downstroke_wait_time.setObjectName(constants.DOWNSTROKE_DELAY)
        self.input_downstroke_wait_time._connected_init_stepper_motor_slot = False
        self.input_downstroke_wait_time._connected_update_child_process_slot = False
        self.input_downstroke_wait_time.setPlaceholderText(self.default_placeholder_text_downstroke_wait_time)
        self.input_downstroke_wait_time.setValidator(QIntValidator())
        self.input_downstroke_wait_time.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_downstroke_wait_time.setFixedWidth(self.widget_width)

        # grouping all QLineEdits to better connect signals
        self.input_fields_list = [
            self.input_step_time,
            self.input_iterations,
            self.input_upstroke_steps,
            self.input_downstroke_steps,
            self.input_upstroke_wait_time,
            self.input_downstroke_wait_time
        ]

        # create buttons
        self.start_btn = QPushButton("start")
        self.start_btn.setFixedWidth(self.widget_width)

        self.update_btn = QPushButton("update params")
        self.update_btn.setFixedWidth(self.widget_width)
        self.update_btn.setEnabled(False)

        self.stop_btn = QPushButton("stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setFixedWidth(self.widget_width)
       
        # connect signals
        self.start_btn.clicked.connect(self.init_stepper_motor)
        self.stop_btn.clicked.connect(lambda: self.stop_child_process(False))
        self.update_btn.clicked.connect(self.update_child_process)
        self.input_downstroke_wait_time.returnPressed.connect(lambda: self.input_downstroke_wait_time.clearFocus())
        for field in self.input_fields_list:
            field.returnPressed.connect(self.init_stepper_motor)
            field.textChanged.connect(self.show_err_label)
            field._connected_init_stepper_motor_slot = True

        # create layout of window and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.text_output)
       
        layout.addWidget(self.label_step_time, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.err_label_step_time, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.input_step_time, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.label_iterations, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.err_label_iterations, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.input_iterations, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.label_upstroke_steps, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.err_label_upstroke_steps, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.input_upstroke_steps, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.label_downstroke_steps, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.err_label_downstroke_steps, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.input_downstroke_steps, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.label_upstroke_wait_time, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.err_label_upstroke_delay, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.input_upstroke_wait_time, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addWidget(self.label_downstroke_wait_time, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.err_label_downstroke_delay, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.input_downstroke_wait_time, alignment=Qt.AlignmentFlag.AlignCenter)
       
        layout.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.update_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.stop_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # creates the container inside of the window
        main_container = QWidget()
        main_container.setLayout(layout)
        self.setCentralWidget(main_container)   # sets the main window's central widget to the argument passed in

    # TODO: create slot to react to invalid user input (characters instead of numbers)
    def show_err_label(self, text):
        # need to determine which label received the user input
        print(f"{self.sender().objectName()}")
        # if the input is not a character display the err label
        # if the user input is a character hide the err label
       
    def display_no_start_values_message(self):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setText("all params required to start the stepper motor")
        msg_box.setWindowTitle("Error")
        msg_box.show()

    def display_no_update_values_message(self):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setText("all params required to update the stepper motor")
        msg_box.setWindowTitle("Error")
        msg_box.show()
   
    @asyncSlot()
    async def init_stepper_motor(self):
        self.start_btn.setEnabled(False)

        step_time = self.input_step_time.text().strip()
        iterations = self.input_iterations.text().strip()
        upstroke_steps = self.input_upstroke_steps.text().strip()
        downstroke_steps = self.input_downstroke_steps.text().strip()
        upstroke_wait_time = self.input_upstroke_wait_time.text().strip()
        downstroke_wait_time = self.input_downstroke_wait_time.text().strip()

        params_list = [step_time,
                       iterations,
                       upstroke_steps,
                       downstroke_steps,
                       upstroke_wait_time,
                       downstroke_wait_time]

        if not all(params_list):
            self.display_no_start_values_message()
            self.start_btn.setEnabled(True)
            return
       
        self.stepper_motor_process = await create_subprocess_exec(
            sys.executable,
            '-u',
            str(SCRIPT_PATH),
            json.dumps(params_list),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        self.read_stderr_task = asyncio.create_task(self.read_stderr())

        self.read_child_output_task = asyncio.create_task(self.read_child_output())

        # clears input fields and displays the previously entered param
        self.input_step_time.clear()
        self.input_step_time.setPlaceholderText(f"step time = {step_time}")

        self.input_iterations.clear()
        self.input_iterations.setPlaceholderText(f"iterations = {iterations}")

        self.input_upstroke_steps.clear()
        self.input_upstroke_steps.setPlaceholderText(f"upstroke steps = {upstroke_steps}")

        self.input_downstroke_steps.clear()
        self.input_downstroke_steps.setPlaceholderText(f"downstroke steps {downstroke_steps}")
       
        self.input_upstroke_wait_time.clear()
        self.input_upstroke_wait_time.setPlaceholderText(f"upstroke wait time =  {upstroke_wait_time}s")
        self.input_downstroke_wait_time.clear()
        self.input_downstroke_wait_time.setPlaceholderText(f"downsroke wait time = {downstroke_wait_time}s")

        self.update_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)

        # connects and disconnects slots accordingly
        for field in self.input_fields_list:
            if field._connected_init_stepper_motor_slot:
                field.returnPressed.disconnect(self.init_stepper_motor)
                field._connected_init_stepper_motor_slot = False
            if not field._connected_update_child_process_slot:
                field.returnPressed.connect(self.update_child_process)
                field._connected_update_child_process_slot = True

    async def stop_scheduled_coroutine(self):
        print(f"{self.script_log_identifier} stopping scheduled coroutine")

        if self.read_child_output_task:
            try:
                self.read_child_output_task.cancel()
                try:
                    await self.read_child_output_task
                except asyncio.CancelledError:
                    # this exception is thrown when a task is canclled so this is expected to be thrown
                    print("[main.py] - stop coroutine received CancelledError exception")
            finally:
                if self.read_child_output_task.cancelled():
                    print("[main.py] - successfullly cancelled the read_output_task")
                else:
                    print(f"{self.script_log_identifier} TASK NOT CANCELLED CORRECTLY")

            self.read_child_output_task = None
   
    @asyncSlot()
    async def stop_child_process(self, is_update: bool):
        print(f"{logger_identifier} - stop command received")

        if self.stepper_motor_process and self.stepper_motor_process.stdin:
            # sends the stop_command to the child script
            # this links to the listen() function in the child script
                # in the child script, the listen() function is a blocking call so it needs
                # to be offloaded to a separate thread
            self.stepper_motor_process.stdin.write((self.stop_command + '\n').encode())
            await self.stepper_motor_process.stdin.drain()

            # waits for the child process to send the sys.exit() return back
            await self.stepper_motor_process.wait()
            print("[main.py] - exited stepper motor child process")

            # waits for the scheduled coroutine output_task to finish
            await self.stop_scheduled_coroutine()

            # cleaning up, making sure the process is set to None
            self.stepper_motor_process = None

            # ui updates
            self.start_btn.setEnabled(True)
            self.update_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)

            self.input_step_time.clear() if is_update == False else None
            self.input_step_time.setPlaceholderText(self.default_placeholder_text_step_time)
   
            self.input_iterations.clear() if is_update == False else None
            self.input_iterations.setPlaceholderText(self.default_placeholder_text_iterations)

            self.input_upstroke_steps.clear() if is_update == False else None
            self.input_upstroke_steps.setPlaceholderText(self.default_placeholder_text_upstroke_steps)

            self.input_downstroke_steps.clear() if is_update == False else None
            self.input_downstroke_steps.setPlaceholderText(self.default_placeholder_text_downstroke_steps)

            self.input_upstroke_wait_time.clear() if is_update == False else None
            self.input_upstroke_wait_time.setPlaceholderText(self.default_placeholder_text_upstroke_wait_time)

            self.input_downstroke_wait_time.clear() if is_update == False else None
            self.input_downstroke_wait_time.setPlaceholderText(self.default_placeholder_text_downstroke_wait_time)

            print(f"{logger_identifier} stepper motor sim stopped successfully")

    @asyncSlot()
    async def update_child_process(self):
        self.update_btn.setEnabled(False)

        p1_text = self.input_step_time.text().strip()
        p2_text = self.input_iterations.text().strip()
        p3_text = self.input_upstroke_steps.text().strip()
        p4_text = self.input_downstroke_steps.text().strip()
        p5_text = self.input_upstroke_wait_time.text().strip()
        p6_text = self.input_downstroke_wait_time.text().strip()
        params_text = [p1_text, p2_text, p3_text,
                       p4_text, p5_text, p6_text]


        # ensures all values have been set
        if not all(params_text):
            self.display_no_update_values_message()
            self.update_btn.setEnabled(True)
            return
       
        # stop process before restarting with new params
        await self.stop_child_process(True)
        print(f"{self.script_log_identifier} stepper motor stopped")

        print(f"{self.script_log_identifier} - restarting stepper motor simulator...")

        # restart stepper motor simulator
        await self.init_stepper_motor()

        print(f"{self.script_log_identifier} stepper motor restarted")

    async def read_stderr(self):
        self.stderr_lines = []
        while True:
            line = await self.stepper_motor_process.stderr.readline()
            if not line:
                break
            decoded = line.decode(errors='replace').strip()
            self.stderr_lines.append(decoded)
            print(f"[stderr] {decoded}", file=sys.stderr)
            raise RuntimeError(f"Child process stderr output detected:\n{decoded}")
       
    async def read_child_output(self):
        while True:
            process_output = await self.stepper_motor_process.stdout.readline()
                # this is needed bc when we close the child process it returns an empty bytes object (b'') which signals the EOF and then we can break out of the while loop then throw the exception to cancel this coroutine
            if not process_output:
                break
            self.text_output.append(process_output.decode().rstrip())

        # since this task is always listening to the child process we need to manually throw the CancelledError
        # exception to ensure it is cancelled correctly
        raise asyncio.CancelledError()
    

    @asyncSlot()    # this decorator is only used for async slots
    async def send_input(self):
        user_input = self.input_line.text()
        self.input_line.clear()

        if self.stepper_motor_process and self.stepper_motor_process.stdin:
            self.stepper_motor_process.stdin.write((user_input + '\n').encode())
            await self.stepper_motor_process.stdin.drain()

logger_identifier = "[main.py] -"
if __name__ == "__main__":
    print(f"{logger_identifier} stepper motor controller initiated!\n"
          f"{logger_identifier} shhhh im listening...")
    app = QApplication(sys.argv)   # create a new instance of a QApplication
    event_loop = QEventLoop(app)   # create a new QEventLoop (event loop) and add the new instance of QApplication to it
    asyncio.set_event_loop(event_loop)   # we set the event loop for pythons/asyncio's default event loop to be our instance of QEventLoop
    window = SMControllerMainWindow()
    window.show()
   
    with event_loop:
        event_loop.run_forever()