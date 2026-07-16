from core.system.service import global_resource_monitor

class ModelManager:
    def __init__(self):
        self._loaded = {}
    def detect_hardware_compatibility(self, size_gb):
        m = global_resource_monitor.get_metrics()
        return m["ram_available_gb"] > size_gb
    def load_model(self, model_id, inst):
        inst.load()
        self._loaded[model_id] = inst
        return True

global_model_manager = ModelManager()
