import threading


class TrainingManager:

    def __init__(self):
        self.thread = None
        self.running = False
        self.error = None

    def start(self, target, *args):

        if self.running:
            return False

        self.running = True

        self.thread = threading.Thread(
            target=self._run,
            args=(target, *args),
            daemon=True
        )

        self.thread.start()

        return True


    def _run(self, target, *args):

        try:
            target(*args)

        except Exception as e:
            self.error = str(e)

        finally:
            self.running = False


    def status(self):

        return {
            "running": self.running,
            "error": self.error
        }