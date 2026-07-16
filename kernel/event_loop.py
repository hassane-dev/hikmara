import threading
import time
from typing import Callable, List

class SoftwareEventLoop:
    def __init__(self):
        self._queue = []
        self._lock = threading.Lock()
        self._running = False

    def post(self, func: Callable[[], None]):
        with self._lock:
            self._queue.append(func)

    def start(self):
        self._running = True
        while self._running:
            func = None
            with self._lock:
                if self._queue:
                    func = self._queue.pop(0)
            if func:
                try:
                    func()
                except Exception:
                    pass
            time.sleep(0.01)

    def stop(self):
        self._running = False

global_event_loop = SoftwareEventLoop()
