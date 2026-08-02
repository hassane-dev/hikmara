import time

class HikmaraError(Exception):
    schema_version: int = 1

    def __init__(self, error_code: str, component: str, severity: str, message: str, recoverable: bool):
        super().__init__(message)
        self.error_code = error_code       # Ex: MODEL_MEMORY_ERROR, ENGINE_LOAD_ERROR
        self.component = component         # Ex: "model_manager"
        self.severity = severity           # Ex: "warning", "critical"
        self.message = message
        self.recoverable = recoverable
        self.timestamp = time.time()

class ConfigurationError(HikmaraError):
    def __init__(self, message: str, recoverable: bool = True):
        super().__init__("CONFIGURATION_ERROR", "config_manager", "warning", message, recoverable)

class ModelLoadError(HikmaraError):
    def __init__(self, message: str, recoverable: bool = True):
        super().__init__("MODEL_LOAD_ERROR", "model_lifecycle_manager", "critical", message, recoverable)

class MemoryPressureError(HikmaraError):
    def __init__(self, message: str, recoverable: bool = True):
        super().__init__("MODEL_MEMORY_ERROR", "model_lifecycle_manager", "critical", message, recoverable)

class CacheError(HikmaraError):
    def __init__(self, message: str, recoverable: bool = True):
        super().__init__("CACHE_INVALIDATION_ERROR", "kv_cache_manager", "warning", message, recoverable)

class SecurityError(HikmaraError):
    def __init__(self, message: str, recoverable: bool = False):
        super().__init__("SECURITY_ERROR", "security_context", "critical", message, recoverable)

class SchedulerError(HikmaraError):
    def __init__(self, message: str, recoverable: bool = True):
        super().__init__("SCHEDULER_ERROR", "inference_scheduler", "warning", message, recoverable)

class PluginError(HikmaraError):
    def __init__(self, message: str, recoverable: bool = True):
        super().__init__("PLUGIN_ERROR", "plugin_manager", "warning", message, recoverable)
