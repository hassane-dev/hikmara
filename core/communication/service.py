from typing import Callable, Dict, List
from core.communication.models import APIRequest, APIResponse

class MessageBus:
    def __init__(self):
        self._handlers = {}

    def register_module(self, name: str, handler: Callable):
        self._handlers[name.lower()] = handler

    def unregister_module(self, name: str):
        if name.lower() in self._handlers:
            del self._handlers[name.lower()]

    def send(self, request_payload: APIRequest) -> APIResponse:
        module = request_payload.module.lower()
        if module not in self._handlers:
            return APIResponse(
                status="error",
                error=f"Destination module '{request_payload.module}' not registered on the MessageBus."
            )
        try:
            res = self._handlers[module](request_payload)
            if isinstance(res, dict):
                return APIResponse(status="success", data=res)
            return res
        except Exception as e:
            return APIResponse(status="error", error=str(e))

global_message_bus = MessageBus()
