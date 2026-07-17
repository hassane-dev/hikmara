import pytest
from core.events.service import global_event_bus

def test_event_bus_pub_sub():
    received = []
    def callback(evt, payload):
        received.append((evt, payload))

    global_event_bus.subscribe("my_event", callback)
    global_event_bus.trigger("my_event", "my_payload")

    assert len(received) == 1
    assert received[0] == ("my_event", "my_payload")
