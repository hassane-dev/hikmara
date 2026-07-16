from core.events.service import global_event_bus

class ModuleManager:
    def __init__(self):
        self.loaded_modules = {}

    def load_module(self, name: str, instance):
        self.loaded_modules[name] = instance
        global_event_bus.trigger("module_loaded", {"module": name})

global_module_manager = ModuleManager()
