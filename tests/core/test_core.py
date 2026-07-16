import pytest
from core.configuration.service import get_config
from core.communication.service import global_message_bus
from core.communication.models import APIRequest
from core.events.service import global_event_bus
from core.security.service import global_security_policy

def test_configuration_loading():
    val = get_config("system").get("system", {}).get("name")
    assert val == "Hikmara AI"

def test_message_bus_routing():
    global_message_bus.register_module("mock_mod", lambda req: req.parameters)
    req = APIRequest(module="mock_mod", action="run", parameters={"hello": "world"})
    resp = global_message_bus.send(req)
    assert resp.status == "success"
    assert resp.data == {"hello": "world"}

def test_event_bus():
    received = []
    def callback(evt, payload): received.append(payload)
    global_event_bus.subscribe("test_evt", callback)
    global_event_bus.trigger("test_evt", "payload")
    assert "payload" in received

def test_security_auth():
    assert global_security_policy.authenticate("admin", "admin123") is True
