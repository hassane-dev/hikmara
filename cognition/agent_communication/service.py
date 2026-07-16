class AgentCommunicationBus:
    def __init__(self):
        self._handlers = {}

    def subscribe_to_agent_topic(self, topic, callback):
        topic = topic.lower()
        if topic not in self._handlers: self._handlers[topic] = []
        self._handlers[topic].append(callback)

    def publish_agent_event(self, topic, payload):
        topic = topic.lower()
        for callback in self._handlers.get(topic, []):
            try: callback(topic, payload)
            except Exception: pass

global_agent_comm_bus = AgentCommunicationBus()
