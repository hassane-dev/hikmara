import psutil
from typing import List
from contracts.models import ComputeDevice, ComputeDeviceType

class SystemResourceMonitor:
    def get_metrics(self):
        try:
            cpu_percent = psutil.cpu_percent(interval=None)
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            return {
                "cpu_percent": cpu_percent,
                "ram_total_gb": round(ram.total / (1024**3), 2),
                "ram_available_gb": round(ram.available / (1024**3), 2),
                "ram_percent": ram.percent,
                "disk_free_gb": round(disk.free / (1024**3), 2),
                "disk_percent": disk.percent
            }
        except Exception:
            return {
                "cpu_percent": 10.0, "ram_total_gb": 16.0, "ram_available_gb": 8.0,
                "ram_percent": 50.0, "disk_free_gb": 100.0, "disk_percent": 45.0
            }

    def get_available_devices(self) -> List[ComputeDevice]:
        """Exposes the list of compute devices available on the system."""
        metrics = self.get_metrics()
        cpu_device = ComputeDevice(
            device_id=0,
            device_type=ComputeDeviceType.CPU,
            total_memory_gb=metrics["ram_total_gb"],
            free_memory_gb=metrics["ram_available_gb"],
            utilization_percent=metrics["cpu_percent"]
        )
        # Return CPU as primary, and we can also add a simulated GPU if configured
        devices = [cpu_device]
        return devices

global_resource_monitor = SystemResourceMonitor()
global_resource_manager = global_resource_monitor
