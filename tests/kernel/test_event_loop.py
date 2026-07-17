import time
import threading
import pytest
from kernel.event_loop import SoftwareEventLoop

def test_event_loop_posting():
    loop = SoftwareEventLoop()
    called = []

    def task():
        called.append("yes")
        loop.stop()

    loop.post(task)

    # Run the loop in a separate thread so it doesn't block infinitely if it fails
    t = threading.Thread(target=loop.start, daemon=True)
    t.start()
    t.join(timeout=1.0)

    assert "yes" in called
