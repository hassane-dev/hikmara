from typing import Dict

class ModuleInfo:
    def __init__(self, name, version, active=True):
        self.name = name
        self.version = version
        self.active = active

class ModuleRegistry:
    def __init__(self):
        self._registry = {}

    def register(self, name, version) -> ModuleInfo:
        info = ModuleInfo(name, version)
        self._registry[name.lower()] = info
        return info

    def list_modules(self):
        return self._registry

global_module_registry = ModuleRegistry()
