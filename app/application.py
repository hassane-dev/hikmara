from runtime import global_runtime_engine

class HikmaraApplication:
    def __init__(self):
        self.runtime = global_runtime_engine
    def initialize_and_run(self):
        self.runtime.bootstrap()

global_hikmara_application = HikmaraApplication()
