import sys
import asyncio
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QTextEdit, QLineEdit,
    QPushButton, QMessageBox, QFormLayout
)
from qasync import QEventLoop, asyncSlot
from asyncio.subprocess import PIPE, create_subprocess_exec
from pathlib import Path

SCRIPT_PATH = Path("stepper_motor.py")

# create gui
class SMControllerMainWindow(QMainWindow):  # we're extending the QMainWindow obj here and calling it SMControllerMainWindow
    def __init__(self):
        super().__init__()
        self.stepper_motor_process = None
        self.read_output_task = None

        self.setWindowTitle("LeafGen Stepper Motor Controller")
        self.resize(600, 400)

        # create output textbox
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setPlaceholderText("output...")

        # create user input fields
        self.param1 = QLineEdit()
        self.param1.setPlaceholderText("param 1")
        self.param2 = QLineEdit()
        self.param2.setPlaceholderText("param 2")
        self.param3 = QLineEdit()
        self.param3.setPlaceholderText("param 3")
        self.param4 = QLineEdit()
        self.param4.setPlaceholderText("param 4")

        # form layout
        form_layout = QFormLayout()
        form_layout.addRow("Param1:", self.param1)
        form_layout.addRow("Param2:", self.param2)


        # create buttons
        self.start_btn = QPushButton("start")
        self.update_btn = QPushButton("update params")
        self.update_btn.setEnabled(False)
        self.stop_btn = QPushButton("stop")
        self.stop_btn.setEnabled(False)
        
        # connect signals
        self.start_btn.clicked.connect(self.init_stepper_motor_sim)
        self.stop_btn.clicked.connect(self.stop_child_process)
        self.update_btn.clicked.connect(self.upate_child_process)
        # self.param1.returnPressed.connect(self.send_input)

        # create layout of window and add widgets
        layout = QVBoxLayout()
        layout.addWidget(self.text_output)  # adds output textbox to layout
        layout.addWidget(self.param1)   # adds user input field to layout
        layout.addWidget(self.param2)   # adds user input field to layout
        layout.addWidget(self.param3)   # adds user input field to layout
        layout.addWidget(self.param4)   # adds user input field to layout
        layout.addWidget(self.start_btn)
        layout.addWidget(self.update_btn)
        layout.addWidget(self.stop_btn)

        # layout.addLayout(form_layout)

        # creates the container inside of the window
        main_container = QWidget()
        main_container.setLayout(layout)
        self.setCentralWidget(main_container)   # sets the main window's central widget to the argument passed in

    def display_no_start_values_message(self):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setText("all params required to start the stepper motor")
        msg_box.setWindowTitle("Error")
        msg_box.exec()

    def display_no_update_values_message(self):
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Icon.Critical)
        msg_box.setText("all params required to update the stepper motor")
        msg_box.setWindowTitle("Error")
        msg_box.exec()
    
    # this needs to be handled by either a return key press or a button click
    @asyncSlot()
    async def init_stepper_motor_sim(self):
        self.start_btn.setEnabled(False)
        param1_text = self.param1.text().strip()
        param2_text = self.param2.text().strip()
        param3_text = self.param3.text().strip()
        param4_text = self.param4.text().strip()
        params_text = [param1_text, param2_text, param3_text, param4_text]
        if not all(params_text):
            self.display_no_start_values_message()
            self.start_btn.setEnabled(True)
            return
        
        self.stepper_motor_process = await create_subprocess_exec(
            sys.executable,
            '-u',
            str(SCRIPT_PATH),
            str(param1_text), str(param2_text),
            str(param3_text), str(param4_text),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        # clears input fields and notifies user of their previously entered params
        self.param1.clear()
        self.param1.setPlaceholderText(f"currently running with param1 of {param1_text}")
        self.param2.clear()
        self.param2.setPlaceholderText(f"currently running with param2 of {param2_text}")
        self.param3.clear()
        self.param3.setPlaceholderText(f"currently running with param3 of {param3_text}")
        self.param4.clear()
        self.param4.setPlaceholderText(f"currently running with param4 of {param4_text}")
        self.update_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)


        self.read_output_task = asyncio.create_task(self.read_output())

    # stop function
    @asyncSlot()
    async def stop_child_process(self):
        stop_command = "leafgen_stop_command"
        if self.stepper_motor_process and self.stepper_motor_process.stdin:
            self.stepper_motor_process.stdin.write((stop_command + '\n').encode())
            await self.stepper_motor_process.stdin.drain()

            # cancel background task before waiting or else the event loop will freak out
            # not exactly sure why this happens yet though
            if self.read_output_task:
                self.read_output_task.cancel()
                try:
                    await self.read_output_task
                except asyncio.CancelledError:
                    pass
            self.read_output_task = None

            await self.stepper_motor_process.wait()
            self.start_btn.setEnabled(True)
            self.update_btn.setEnabled(False)
            self.stop_btn.setEnabled(False)

    @asyncSlot()
    async def upate_child_process(self):
        self.update_btn.setEnabled(False)
        param1_text = self.param1.text().strip()
        param2_text = self.param2.text().strip()
        param3_text = self.param3.text().strip()
        param4_text = self.param4.text().strip()
        params_text = [param1_text, param2_text, param3_text, param4_text]
        if not all(params_text):
            self.display_no_update_values_message()
            self.update_btn.setEnabled(True)
            return
        # stop process before restarting with new params
        await self.stop_child_process()
        print("[main.py] - stepper motor stopped")
        await self.init_stepper_motor_sim()
        print("[main.py] - stepper motor restarted")
        
    async def read_output(self):
        while True:
            process_output = await self.stepper_motor_process.stdout.readline()
            if not process_output:
                break
            self.text_output.append(f"[main.py] stepper motor output - {process_output.decode().rstrip()}")


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