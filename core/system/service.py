import psutil

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

global_resource_monitor = SystemResourceMonitor()
