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

SCRIPT_PATH = Path("stepper_motor_async.py")

# create gui
class SMControllerMainWindow(QMainWindow):  # we're extending the QMainWindow obj here and calling it SMControllerMainWindow
    def __init__(self):
        super().__init__()
        self.stepper_motor_process = None
        self.read_child_output_task = None
        self.script_log_identifier = "[main.py] - "
        self.default_param1_placeholder_text = "param 1"
        self.default_param2_placeholder_text = "param 2"
        self.default_param3_placeholder_text = "param 3"
        self.default_param4_placeholder_text = "param 4"
        self.widget_width = 300

        self.setWindowTitle("LeafGen Stepper Motor Controller")
        self.resize(900, 600)

        # create output textbox
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setPlaceholderText("output...")

        # create labels
        self.param1_label = QLabel("param1")
        self.param2_label = QLabel("param2")
        self.param3_label = QLabel("param3")
        self.param4_label = QLabel("param4")

        # create user input fields
        self.param1 = QLineEdit()
        self.param1._connected_init_stepper_motor_slot = False
        self.param1._connected_update_child_process_slot = False
        self.param1.setPlaceholderText(self.default_param1_placeholder_text)
        self.param1.setValidator(QIntValidator())
        self.param1.setFixedWidth(self.widget_width)
        self.param1.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.param2 = QLineEdit()
        self.param2._connected_init_stepper_motor_slot = False
        self.param2._connected_update_child_process_slot = False
        self.param2.setPlaceholderText(self.default_param3_placeholder_text)
        self.param2.setValidator(QIntValidator())
        self.param2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.param2.setFixedWidth(self.widget_width)

        self.param3 = QLineEdit()
        self.param3._connected_init_stepper_motor_slot = False
        self.param3._connected_update_child_process_slot = False
        self.param3.setPlaceholderText(self.default_param3_placeholder_text)
        self.param3.setValidator(QIntValidator())
        self.param3.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.param3.setFixedWidth(self.widget_width)

        self.param4 = QLineEdit()
        self.param4._connected_init_stepper_motor_slot = False
        self.param4._connected_update_child_process_slot = False
        self.param4.setPlaceholderText(self.default_param4_placeholder_text)
        self.param4.setValidator(QIntValidator())
        self.param4.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.param4.setFixedWidth(self.widget_width)

        # grouping all QLineEdits to better connect signals
        self.input_fields_list = [self.param1, self.param2, self.param3, self.param4]

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
        self.start_btn.clicked.connect(self.init_stepper_motor_sim)
        self.stop_btn.clicked.connect(lambda: self.stop_child_process(False))
        self.update_btn.clicked.connect(self.update_child_process)
        self.param4.returnPressed.connect(lambda: self.param4.clearFocus())
        for field in self.input_fields_list:
            field.returnPressed.connect(self.init_stepper_motor_sim)
            field._connected_init_stepper_motor_slot = True

        # create layout of window and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.text_output)  # adds output textbox to layout
        
        layout.addWidget(self.param1_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.param1, alignment=Qt.AlignmentFlag.AlignCenter)   # adds user input field to layout

        layout.addWidget(self.param2_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.param2, alignment=Qt.AlignmentFlag.AlignCenter)   # adds user input field to layout

        layout.addWidget(self.param3_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.param3, alignment=Qt.AlignmentFlag.AlignCenter)   # adds user input field to layout

        layout.addWidget(self.param4_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.param4, alignment=Qt.AlignmentFlag.AlignCenter)   # adds user input field to layout
        
        layout.addWidget(self.start_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.update_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.stop_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # creates the container inside of the window
        main_container = QWidget()
        main_container.setLayout(layout)
        self.setCentralWidget(main_container)   # sets the main window's central widget to the argument passed in

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
    async def init_stepper_motor_sim(self):
        self.start_btn.setEnabled(False)

        param1_input = self.param1.text().strip()
        param2_input = self.param2.text().strip()
        param3_input = self.param3.text().strip()
        param4_input = self.param4.text().strip()
        params_list = [param1_input,
                       param2_input,
                       param3_input,
                       param4_input]

        if not all(params_list):
            self.display_no_start_values_message()
            self.start_btn.setEnabled(True)
            return
        
        self.stepper_motor_process = await create_subprocess_exec(
            sys.executable,
            '-u',
            str(SCRIPT_PATH),
            str(param1_input), str(param2_input),
            str(param3_input), str(param4_input),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # clears input fields and notifies user of their previously entered params
        self.param1.clear()
        self.param1.setPlaceholderText(f"currently running with param1 of {param1_input}")
        self.param2.clear()
        self.param2.setPlaceholderText(f"currently running with param2 of {param2_input}")
        self.param3.clear()
        self.param3.setPlaceholderText(f"currently running with param3 of {param3_input}")
        self.param4.clear()
        self.param4.setPlaceholderText(f"currently running with param4 of {param4_input}")
        self.update_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)

        
        for field in self.input_fields_list:
            if field._connected_init_stepper_motor_slot:
                field.returnPressed.disconnect(self.init_stepper_motor_sim)
                field._connected_init_stepper_motor_slot = False
            if not field._connected_update_child_process_slot:
                field.returnPressed.connect(self.update_child_process)
                field._connected_update_child_process_slot = True
        
        self.read_child_output_task = asyncio.create_task(self.read_child_output())

    @asyncSlot()
    async def stop_child_process(self, is_update: bool):
        print("[main.py] - stop command received")
        stop_command = "leafgen_stop_command"

        if self.stepper_motor_process and self.stepper_motor_process.stdin:
            # sends the stop_command to the child script
            # this links to the listen() function in the child script
                # in the child script, the listen() function is a blocking call so it needs
                # to be offloaded to a separate thread
            self.stepper_motor_process.stdin.write((stop_command + '\n').encode())
            await self.stepper_motor_process.stdin.drain()

            # waits for the child process to send the sys.exit() return back
            await self.stepper_motor_process.wait()
            print("[main.py] - child process exited")

            # waits for the scheduled coroutine output_task to finish
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
                        print("TASK NOT CANCELLED CORRECTLY")

                self.read_child_output_task = None

            # cleaning up, making sure the process is set to None
            self.stepper_motor_process = None

            # ui updates
            self.start_btn.setEnabled(True)
            self.update_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)

            self.param1.clear() if is_update == False else None
            self.param1.setPlaceholderText(self.default_param1_placeholder_text)        
    
            self.param2.clear() if is_update == False else None
            self.param2.setPlaceholderText(self.default_param2_placeholder_text)

            self.param3.clear() if is_update == False else None
            self.param3.setPlaceholderText(self.default_param3_placeholder_text)

            self.param4.clear() if is_update == False else None
            self.param4.setPlaceholderText(self.default_param4_placeholder_text)

            print("[main.py] - stepper motor sim stopped successfully")

    @asyncSlot()
    async def update_child_process(self):
        self.update_btn.setEnabled(False)

        param1_text = self.param1.text().strip()
        param2_text = self.param2.text().strip()
        param3_text = self.param3.text().strip()
        param4_text = self.param4.text().strip()
        params_text = [param1_text, param2_text, param3_text, param4_text]

        # ensures all values have been set
        if not all(params_text):
            self.display_no_update_values_message()
            self.update_btn.setEnabled(True)
            return
        
        # stop process before restarting with new params
        await self.stop_child_process(True)
        print("[main.py] - stepper motor stopped")

        print(f"{self.script_log_identifier} - restarting stepper motor simulator...")

        # restart stepper motor simulator
        await self.init_stepper_motor_sim()

        print("[main.py] - stepper motor restarted")
        
    async def read_child_output(self):
        while True:
            process_output = await self.stepper_motor_process.stdout.readline()
                # this is needed bc when we close the child process it returns an empty bytes object (b'') which signals
                # the EOF and then we can break out of the while loop then throw the exception to cancel this coroutine
            if not process_output:
                break
            self.text_output.append(f"[main.py] stepper motor output - {process_output.decode().rstrip()}")

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

if __name__ == "__main__":
    print("[main.py] -stepper motor controller initiated!" \
            "\n[main.py] - shhhh im listening...")
    app = QApplication(sys.argv)   # create a new instance of a QApplication
    event_loop = QEventLoop(app)   # create a new QEventLoop (event loop) and add the new instance of QApplication to it
    asyncio.set_event_loop(event_loop)   # we set the event loop for pythons/asyncio's default event loop to be our instance of QEventLoop
    window = SMControllerMainWindow()
    window.show()
    
    with event_loop:
        event_loop.run_forever()