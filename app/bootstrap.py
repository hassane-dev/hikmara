import os
from core.logging.service import system_logger
from runtime import global_runtime_engine

def bootstrap_application():
    os.makedirs("logs", exist_ok=True)
    os.makedirs("database", exist_ok=True)
    os.makedirs("cache/temporary", exist_ok=True)
    global_runtime_engine.bootstrap()
