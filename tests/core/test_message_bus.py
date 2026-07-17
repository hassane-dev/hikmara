import pytest
from core.communication.service import MessageBus
from core.communication.models import APIRequest, APIResponse

def test_message_bus_routing():
    bus = MessageBus()

    # Handler must receive APIRequest and return APIResponse
    def handler(req: APIRequest) -> APIResponse:
        return APIResponse(status="success", data={"echo": req.parameters})

    bus.register_module("echo_mod", handler)

    req = APIRequest(module="echo_mod", action="echo_action", parameters={"hello": "world"})
    resp = bus.send(req)

    assert resp.status == "success"
    assert resp.data == {"echo": {"hello": "world"}}

    # Non-existent module should fail gracefully
    req_missing = APIRequest(module="invalid_mod", action="echo_action", parameters={})
    resp_missing = bus.send(req_missing)
    assert resp_missing.status == "error"
    assert "not registered" in resp_missing.error
