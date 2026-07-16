import threading
import time
from core.logging.service import system_logger
from core.system.service import global_resource_monitor
from core.module_registry.service import global_module_registry

class ServiceManager:
    def __init__(self):
        self._services = {}

    def register_service(self, name, service_inst):
        self._services[name] = service_inst

    def start_all(self):
        for name, inst in self._services.items():
            if hasattr(inst, "start"):
                inst.start()

    def stop_all(self):
        for name, inst in self._services.items():
            if hasattr(inst, "stop"):
                inst.stop()

class HealthMonitor:
    def __init__(self):
        self._running = False
        self._thread = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False

    def _monitor_loop(self):
        while self._running:
            metrics = global_resource_monitor.get_metrics()
            time.sleep(5.0)

class RuntimeEngine:
    def __init__(self):
        self.service_manager = ServiceManager()
        self.health_monitor = HealthMonitor()

    def bootstrap(self):
        global_module_registry.register("core_api", "0.1.0")
        global_module_registry.register("core_tasks", "0.1.0")
        global_module_registry.register("core_security", "0.1.0")
        self.health_monitor.start()
        self.service_manager.start_all()

    def shutdown(self):
        self.health_monitor.stop()
        self.service_manager.stop_all()

global_runtime_engine = RuntimeEngine()
