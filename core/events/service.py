from typing import Callable, Dict, List, Any

class EventBus:
    def __init__(self):
        self._subscribers = {}

    def subscribe(self, event_name: str, callback: Callable):
        event_name = event_name.lower()
        if event_name not in self._subscribers:
            self._subscribers[event_name] = []
        self._subscribers[event_name].append(callback)

    def trigger(self, event_name: str, payload: Any = None):
        event_name = event_name.lower()
        for callback in self._subscribers.get(event_name, []):
            try:
                callback(event_name, payload)
            except Exception:
                pass
        for callback in self._subscribers.get("*", []):
            try:
                callback(event_name, payload)
            except Exception:
                pass

global_event_bus = EventBus()
