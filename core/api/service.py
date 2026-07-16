import json
from core.communication.models import APIRequest, APIResponse
from core.communication.service import global_message_bus

class APIRouter:
    def route_request(self, payload_json: str) -> str:
        try:
            data = json.loads(payload_json)
            req = APIRequest(**data)
            resp = global_message_bus.send(req)
            return resp.model_dump_json()
        except Exception as e:
            return APIResponse(status="error", error=str(e)).model_dump_json()

global_api_router = APIRouter()
