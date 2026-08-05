from pathlib import Path
from subprocess import Popen
import threading


class TensorBoardManager:

    def __init__(self):
        self._process = None
        self._lock = threading.Lock()

    def is_running(self):
        return (
            self._process is not None
            and self._process.poll() is None
        )

    def start(self, logdir):

        with self._lock:

            if self.is_running():
                return False

            self._process = Popen([
                "tensorboard",
                "--logdir", str(logdir),
                "--host", "0.0.0.0",
                "--port", "6006",
            ])

            return True

    def stop(self):

        with self._lock:

            if not self.is_running():
                return False

            self._process.terminate()
            self._process.wait(timeout=5)

            self._process = None

            return True