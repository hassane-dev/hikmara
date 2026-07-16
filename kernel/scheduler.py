import threading
import time
from typing import Callable, List, Dict, Any, Optional

class KernelScheduler:
    def __init__(self):
        self._jobs = []
        self._running = False
        self._thread = None

    def add_interval_job(self, name: str, interval: float, func: Callable[[], None]):
        self._jobs.append({
            "name": name,
            "interval": interval,
            "func": func,
            "last_run": 0.0
        })

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _loop(self):
        while self._running:
            now = time.time()
            for job in self._jobs:
                if now - job["last_run"] >= job["interval"]:
                    try:
                        job["func"]()
                    except Exception:
                        pass
                    job["last_run"] = time.time()
            time.sleep(0.1)

global_kernel_scheduler = KernelScheduler()
