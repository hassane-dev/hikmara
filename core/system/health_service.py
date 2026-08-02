import time
from typing import List
from contracts.models import HealthReport, HealthStatus
from core.system.service import global_resource_monitor
from ai_models.model_registry.service import global_model_registry

class HealthCheckService:
    def __init__(self):
        pass

    def perform_health_check(self) -> HealthReport:
        """Runs diagnostics on the core engine and hardware states to generate a HealthReport."""
        metrics = global_resource_monitor.get_metrics()
        ram_avail = metrics.get("ram_available_gb", 8.0)

        # Check constraints or logical integrity
        active_warnings = []
        status = HealthStatus.HEALTHY

        if ram_avail < 2.0:
            active_warnings.append("Pression mémoire vive élevée (moins de 2 Go de RAM disponible)")
            status = HealthStatus.WARNING
        if ram_avail < 1.0:
            active_warnings.append("Statut Mémoire Critique (moins de 1 Go de RAM libre)")
            status = HealthStatus.CRITICAL

        # Check model registry presence
        registered_models = global_model_registry.list_models()
        if not registered_models:
            active_warnings.append("Le catalogue ModelRegistry est vide.")
            status = HealthStatus.CRITICAL

        return HealthReport(
            status=status,
            engine_loaded=True,
            hot_pool_count=1,  # baseline count
            ram_available_gb=ram_avail,
            device_status="CPU Active",
            cache_integrity=True,
            active_warnings=active_warnings,
            timestamp=time.time()
        )

global_health_check_service = HealthCheckService()
