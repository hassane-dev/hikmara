import sys
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, QPushButton, QLabel, QListWidget, QTabWidget, QCheckBox, QProgressBar
from PyQt6.QtCore import Qt
from core.security.service import global_security_policy
from core.tasks.service import global_task_manager
from core.system.service import global_resource_monitor
from core.module_registry.service import global_module_registry
from ai_models.llm.service import LLMEngine
from cognition.agents.manager.service import global_agent_manager
from interface.desktop.widgets.security_dialog import SecurityConsentDialog

class HikmaraMainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Hikmara AI - Universal Intelligent Local Control Center")
        self.llm = LLMEngine("qwen")
        self.llm.load()
        global_security_policy.set_consent_handler(self.request_user_consent)
        self.init_ui()

    def init_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout()
        central.setLayout(layout)

        left = QWidget()
        left_layout = QVBoxLayout()
        left.setLayout(left_layout)
        self.sim_offline_cb = QCheckBox("Simulation offline")
        self.sim_offline_cb.setChecked(True)
        left_layout.addWidget(self.sim_offline_cb)
        self.metrics_label = QLabel()
        left_layout.addWidget(self.metrics_label)
        layout.addWidget(left)

        self.chat_display = QTextEdit()
        layout.addWidget(self.chat_display)

    def request_user_consent(self, mod, act, params):
        d = SecurityConsentDialog(self, mod, act, params)
        d.exec()
        return d.approved
