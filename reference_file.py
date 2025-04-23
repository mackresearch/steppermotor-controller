import sys
import asyncio
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QTextEdit, QLineEdit
)
from qasync import QEventLoop, asyncSlot
from asyncio.subprocess import PIPE, create_subprocess_exec


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PyQt6 + asyncio subprocess")
        self.resize(600, 400)

        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)

        self.input_line = QLineEdit()
        self.input_line.returnPressed.connect(self.send_input)

        layout = QVBoxLayout()
        layout.addWidget(self.text_output)
        layout.addWidget(self.input_line)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.proc = None

    async def start_subprocess(self):
        self.proc = await create_subprocess_exec(
            sys.executable, "-u", "-c",
            "import sys; [sys.stdout.write('Echo: '+line) or sys.stdout.flush() for line in sys.stdin]",
            stdin=PIPE, stdout=PIPE
        )
        asyncio.create_task(self.read_output())

    async def read_output(self):
        while True:
            line = await self.proc.stdout.readline()
            if not line:
                break
            self.text_output.append(f"[Child] {line.decode().rstrip()}")

    @asyncSlot()
    async def send_input(self):
        text = self.input_line.text()
        self.input_line.clear()
        if self.proc and self.proc.stdin:
            self.proc.stdin.write((text + "\n").encode())
            await self.proc.stdin.drain()


async def main():
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    window = MainWindow()
    window.show()
    await window.start_subprocess()

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    asyncio.run(main())
